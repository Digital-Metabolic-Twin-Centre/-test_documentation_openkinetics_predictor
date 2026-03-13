#!/usr/bin/env python3
"""
Pure-Python integration test for one prediction method.

No web server, Celery worker, Redis, or Docker is required.
The script exercises the backend execution path directly via:
  - method registry loading
  - job creation
  - prediction execution helpers in api.tasks
  - output CSV checks

Optional:
  - run a DLKcat sanity scenario first.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


class IntegrationTestError(Exception):
    """Raised when a scenario fails."""


@dataclass
class Scenario:
    name: str
    prediction_type: str
    kcat_method: str = ""
    km_method: str = ""


def _print_header(title: str) -> None:
    print(f"\n=== {title} ===")


def _count_non_empty(series: pd.Series) -> int:
    return int((series.fillna("").astype(str).str.strip() != "").sum())


def _setup_django(repo_root: Path) -> None:
    sys.path.insert(0, str(repo_root))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webKinPred.settings")
    import django

    django.setup()


def _build_fixture_df(desc, rows: int = 2) -> pd.DataFrame:
    columns = ["Protein Sequence"] + list(desc.col_to_kwarg.keys())
    columns = list(dict.fromkeys(columns))

    sequences = [
        "MKTLLILAVAGFATVAQA",
        "GAVLIPFWYTSNQDEKRH",
    ]
    if rows > len(sequences):
        sequences.extend([sequences[-1]] * (rows - len(sequences)))
    sequences = sequences[:rows]

    data: dict[str, list[Any]] = {}
    for col in columns:
        if col == "Protein Sequence":
            data[col] = sequences
        elif col == "Substrate":
            data[col] = ["CC(=O)O", "C1CCCCC1"][:rows]
        elif col == "Substrates":
            data[col] = ["CC(=O)O;O", "C1CCCCC1;O"][:rows]
        elif col == "Products":
            data[col] = ["CC(O)=O;[H+]", "OC1CCCCC1;[H+]"][:rows]
        else:
            data[col] = [f"dummy_{i+1}" for i in range(rows)]

    return pd.DataFrame(data)


def _assert_descriptor_is_runnable(desc) -> None:
    if desc.pred_func is None and desc.subprocess is None:
        raise IntegrationTestError(
            f"Method '{desc.key}' has neither pred_func nor subprocess configured."
        )
    if desc.input_format not in {"single", "multi"}:
        raise IntegrationTestError(
            f"Method '{desc.key}' has invalid input_format='{desc.input_format}'."
        )
    if "Protein Sequence" in desc.col_to_kwarg:
        raise IntegrationTestError(
            f"Method '{desc.key}' must not map 'Protein Sequence' in col_to_kwarg."
        )


def _build_scenarios(desc, include_both: bool) -> list[Scenario]:
    supports = set(desc.supports)
    scenarios: list[Scenario] = []

    if "kcat" in supports:
        scenarios.append(
            Scenario(
                name=f"{desc.key} / kcat",
                prediction_type="kcat",
                kcat_method=desc.key,
            )
        )
    if "Km" in supports:
        scenarios.append(
            Scenario(
                name=f"{desc.key} / Km",
                prediction_type="Km",
                km_method=desc.key,
            )
        )
    if include_both and {"kcat", "Km"}.issubset(supports):
        scenarios.append(
            Scenario(
                name=f"{desc.key} / both",
                prediction_type="both",
                kcat_method=desc.key,
                km_method=desc.key,
            )
        )

    if not scenarios:
        raise IntegrationTestError(
            f"Method '{desc.key}' supports neither kcat nor Km."
        )
    return scenarios


def _make_job(
    prediction_type: str,
    kcat_method: str,
    km_method: str,
    requested_rows: int,
):
    from api.models import Job
    from django.conf import settings

    job = Job(
        prediction_type=prediction_type,
        kcat_method=kcat_method or None,
        km_method=km_method or None,
        status="Pending",
        handle_long_sequences="truncate",
        ip_address="127.0.0.1",
        requested_rows=requested_rows,
    )
    job.save()

    job_dir = Path(settings.MEDIA_ROOT) / "jobs" / str(job.public_id)
    job_dir.mkdir(parents=True, exist_ok=True)
    return job, job_dir


def _run_single_target_scenario(
    scenario: Scenario,
    desc,
    input_df: pd.DataFrame,
):
    from api.tasks import _execute_prediction

    target = scenario.prediction_type
    job, job_dir = _make_job(
        prediction_type=target,
        kcat_method=scenario.kcat_method,
        km_method=scenario.km_method,
        requested_rows=len(input_df),
    )

    input_path = job_dir / "input.csv"
    input_df.to_csv(input_path, index=False)

    try:
        _execute_prediction(
            job=job,
            desc=desc,
            df=input_df.copy(),
            target=target,
            experimental_results=[],
        )
    except Exception as e:
        raise IntegrationTestError(
            f"Execution failed for scenario [{scenario.name}]: {e}"
        ) from e

    output_path = job_dir / "output.csv"
    if not output_path.exists():
        raise IntegrationTestError(f"No output.csv produced for [{scenario.name}]")

    return job, job_dir, pd.read_csv(output_path)


def _run_both_scenario(
    scenario: Scenario,
    kcat_desc,
    km_desc,
    input_df: pd.DataFrame,
):
    from api.tasks import _execute_both_prediction

    job, job_dir = _make_job(
        prediction_type="both",
        kcat_method=scenario.kcat_method,
        km_method=scenario.km_method,
        requested_rows=len(input_df),
    )

    input_path = job_dir / "input.csv"
    input_df.to_csv(input_path, index=False)

    try:
        _execute_both_prediction(
            job=job,
            kcat_desc=kcat_desc,
            km_desc=km_desc,
            df=input_df.copy(),
            experimental_results=[],
        )
    except Exception as e:
        raise IntegrationTestError(
            f"Execution failed for scenario [{scenario.name}]: {e}"
        ) from e

    output_path = job_dir / "output.csv"
    if not output_path.exists():
        raise IntegrationTestError(f"No output.csv produced for [{scenario.name}]")

    return job, job_dir, pd.read_csv(output_path)


def _validate_output(
    scenario: Scenario,
    input_df: pd.DataFrame,
    output_df: pd.DataFrame,
    allow_empty_predictions: bool,
) -> None:
    if len(output_df) != len(input_df):
        raise IntegrationTestError(
            f"Row count mismatch [{scenario.name}]: input={len(input_df)} output={len(output_df)}"
        )

    new_cols = [c for c in output_df.columns if c not in input_df.columns]
    if not new_cols:
        raise IntegrationTestError(f"No prediction columns added for [{scenario.name}]")

    kcat_cols = [c for c in output_df.columns if "kcat" in c.lower()]
    km_cols = [
        c
        for c in output_df.columns
        if c.lower().startswith("km") or " km" in c.lower()
    ]

    target_cols: list[str] = []
    if scenario.prediction_type == "kcat":
        if not kcat_cols:
            raise IntegrationTestError(f"Could not find kcat column in [{scenario.name}]")
        target_cols = kcat_cols
    elif scenario.prediction_type == "Km":
        if not km_cols:
            raise IntegrationTestError(f"Could not find Km column in [{scenario.name}]")
        target_cols = km_cols
    elif scenario.prediction_type == "both":
        if not kcat_cols or not km_cols:
            raise IntegrationTestError(
                f"Could not find both kcat and Km columns in [{scenario.name}]"
            )
        target_cols = [kcat_cols[0], km_cols[0]]

    if not allow_empty_predictions:
        non_empty = sum(_count_non_empty(output_df[col]) for col in target_cols)
        if non_empty == 0:
            raise IntegrationTestError(
                f"All target predictions are empty in [{scenario.name}]. "
                "Use --allow-empty-predictions to relax this check."
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Pure-Python integration test for one prediction method.",
    )
    parser.add_argument(
        "--method",
        required=True,
        help="Method key, e.g. DLKcat, UniKP, KinForm-H, YourMethod.",
    )
    parser.add_argument(
        "--rows",
        type=int,
        default=2,
        help="Number of fixture rows to generate (default: 2).",
    )
    parser.add_argument(
        "--skip-dlkcat-sanity",
        action="store_true",
        help="Skip DLKcat sanity scenario.",
    )
    parser.add_argument(
        "--skip-both-scenario",
        action="store_true",
        help="If method supports both, skip prediction_type='both' scenario.",
    )
    parser.add_argument(
        "--allow-empty-predictions",
        action="store_true",
        help="Allow all-empty target predictions without failing.",
    )
    parser.add_argument(
        "--keep-artifacts",
        action="store_true",
        help="Keep generated job rows/files for debugging.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    _setup_django(repo_root)

    # Prevent Redis quota calls during pure-python integration tests.
    import api.tasks as tasks_module

    tasks_module.credit_back = lambda *_args, **_kwargs: None

    from api.methods.registry import all_methods, get as get_method

    _print_header("Method Discovery")
    methods = all_methods()
    if args.method not in methods:
        available = ", ".join(sorted(methods.keys()))
        raise IntegrationTestError(
            f"Method '{args.method}' not found. Available: {available}"
        )

    method_desc = get_method(args.method)
    _assert_descriptor_is_runnable(method_desc)
    print(
        f"OK: found {method_desc.key} (supports={method_desc.supports}, "
        f"input_format={method_desc.input_format})"
    )

    scenarios: list[tuple[Scenario, Any]] = []

    if not args.skip_dlkcat_sanity and args.method != "DLKcat" and "DLKcat" in methods:
        dlkcat_desc = get_method("DLKcat")
        _assert_descriptor_is_runnable(dlkcat_desc)
        scenarios.append(
            (
                Scenario(
                    name="DLKcat sanity / kcat",
                    prediction_type="kcat",
                    kcat_method="DLKcat",
                ),
                dlkcat_desc,
            )
        )
        print("Will run DLKcat sanity scenario first.")

    for scenario in _build_scenarios(
        method_desc, include_both=not args.skip_both_scenario
    ):
        scenarios.append((scenario, method_desc))

    _print_header("Running Scenarios")
    created_jobs: list[tuple[Any, Path]] = []
    try:
        for scenario, desc in scenarios:
            fixture_df = _build_fixture_df(desc, rows=args.rows)
            print(f"[START] {scenario.name}")

            if scenario.prediction_type == "both":
                job, job_dir, output_df = _run_both_scenario(
                    scenario=scenario,
                    kcat_desc=desc,
                    km_desc=desc,
                    input_df=fixture_df,
                )
            else:
                job, job_dir, output_df = _run_single_target_scenario(
                    scenario=scenario,
                    desc=desc,
                    input_df=fixture_df,
                )

            created_jobs.append((job, job_dir))
            _validate_output(
                scenario=scenario,
                input_df=fixture_df,
                output_df=output_df,
                allow_empty_predictions=args.allow_empty_predictions,
            )
            print(
                f"[PASS] {scenario.name} | public_id={job.public_id} "
                f"| rows={len(output_df)} | cols={len(output_df.columns)}"
            )

    finally:
        if not args.keep_artifacts:
            for job, job_dir in created_jobs:
                try:
                    job.delete()
                except Exception:
                    pass
                try:
                    shutil.rmtree(job_dir, ignore_errors=True)
                except Exception:
                    pass

    _print_header("All Checks Passed")
    print(f"Pure-Python integration test succeeded for: {args.method}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except IntegrationTestError as e:
        print(f"\n[FAIL] {e}", file=sys.stderr)
        raise SystemExit(1)
