"""
Job-specific utility functions for job submission and management.
"""
import os
import pandas as pd
from typing import Dict, List, Optional, Any
from django.conf import settings
from django.utils import timezone
from api.utils import get_experimental


def validate_prediction_parameters(
    prediction_type: str,
    kcat_method: Optional[str] = None,
    km_method: Optional[str] = None,
) -> Optional[str]:
    """
    Validate prediction type and method parameters against the registry.

    Returns an error message if validation fails, None if valid.
    """
    from api.methods.registry import all_methods

    if prediction_type not in ("kcat", "Km", "both"):
        return 'Invalid prediction type. Expected "kcat", "Km", or "both".'

    registry = all_methods()

    if prediction_type in ("kcat", "both"):
        desc = registry.get(kcat_method)
        if desc is None or "kcat" not in desc.supports:
            valid = sorted(k for k, d in registry.items() if "kcat" in d.supports)
            return (
                f"Invalid kcat method '{kcat_method}'. "
                f"Available kcat methods: {', '.join(valid)}."
            )

    if prediction_type in ("Km", "both"):
        desc = registry.get(km_method)
        if desc is None or "Km" not in desc.supports:
            valid = sorted(k for k, d in registry.items() if "Km" in d.supports)
            return (
                f"Invalid KM method '{km_method}'. "
                f"Available KM methods: {', '.join(valid)}."
            )

    return None


def validate_sequence_handling_option(handle_long_seq: str) -> Optional[str]:
    """
    Validate the sequence handling option parameter.

    Returns an error message if invalid, None if valid.
    """
    if handle_long_seq not in ("truncate", "skip"):
        return 'Invalid handleLongSeq value. Expected "truncate" or "skip".'
    return None


def determine_required_columns(
    prediction_type: str,
    kcat_method: Optional[str],
    km_method: Optional[str],
) -> List[str]:
    """
    Determine the CSV columns required for the given prediction parameters.

    The result always includes "Protein Sequence".  Additional columns are
    derived from each method descriptor's col_to_kwarg mapping.
    """
    from api.methods.registry import get

    required: set[str] = {"Protein Sequence"}

    if prediction_type in ("kcat", "both") and kcat_method:
        try:
            desc = get(kcat_method)
            required.update(desc.col_to_kwarg.keys())
        except KeyError:
            pass

    if prediction_type in ("Km", "both") and km_method:
        try:
            desc = get(km_method)
            required.update(desc.col_to_kwarg.keys())
        except KeyError:
            pass

    return list(required)


def create_job_directory(public_id: str) -> str:
    """
    Create directory structure for a job.

    Returns the path to the created job directory.
    """
    job_dir = os.path.join(settings.MEDIA_ROOT, "jobs", str(public_id))
    os.makedirs(job_dir, exist_ok=True)
    return job_dir


def save_job_input_file(file, job_dir: str) -> str:
    """
    Save the input CSV file to the job directory.

    Returns the path to the saved file.
    """
    file_path = os.path.join(job_dir, "input.csv")
    file.seek(0)
    input_df = pd.read_csv(file)
    input_df.dropna(how="all", inplace=True)
    input_df.to_csv(file_path, index=False)
    return file_path


def get_experimental_results(
    use_experimental: bool,
    kcat_method: Optional[str],
    dataframe: pd.DataFrame,
    prediction_type: str,
) -> Optional[list]:
    """
    Look up experimental kinetic values when the user has opted in.

    Experimental lookup is skipped for multi-substrate methods (TurNup) since
    the experimental database is indexed by single substrates.

    Returns a list of experimental result dicts, or None.
    """
    if not use_experimental:
        return None

    # Skip for multi-substrate methods — the experimental DB only covers
    # single-substrate reactions.
    if kcat_method:
        try:
            from api.methods.registry import get
            desc = get(kcat_method)
            if desc.input_format == "multi":
                return None
        except KeyError:
            pass

    if "Substrate" not in dataframe.columns:
        return None

    return get_experimental.lookup_experimental(
        dataframe["Protein Sequence"].tolist(),
        dataframe["Substrate"].tolist(),
        param_type=prediction_type,
    )


def extract_job_parameters_from_request(request) -> Dict[str, Any]:
    """
    Extract job parameters from an HTTP request.

    Returns a parameters dictionary used by process_job_submission_from_params.
    """
    return {
        "use_experimental": request.POST.get("useExperimental") == "true",
        "prediction_type": request.POST.get("predictionType"),
        "kcat_method": request.POST.get("kcatMethod"),
        "km_method": request.POST.get("kmMethod"),
        "handle_long_sequences": request.POST.get("handleLongSequences"),
    }


def create_rate_limit_headers(
    daily_limit: int, remaining: int, ttl: int
) -> Dict[str, str]:
    """
    Create standard rate-limiting headers for HTTP responses.
    """
    return {
        "X-RateLimit-Limit": str(daily_limit),
        "X-RateLimit-Remaining": str(max(0, remaining)),
        "X-RateLimit-Reset": str(ttl),
    }


def create_job_status_response_data(job) -> Dict[str, Any]:
    """
    Create a response data dictionary for the job-status endpoint.
    """
    return {
        "public_id": job.public_id,
        "status": job.status,
        "submission_time": job.submission_time,
        "completion_time": job.completion_time,
        "server_time": timezone.now(),
        "elapsed_seconds": (
            int(max(0, (job.completion_time - job.submission_time).total_seconds()))
            if job.completion_time
            else int(max(0, (timezone.now() - job.submission_time).total_seconds()))
        ),
        "error_message": job.error_message,
        "total_molecules": job.total_molecules,
        "molecules_processed": job.molecules_processed,
        "invalid_rows": job.invalid_rows,
        "total_predictions": job.total_predictions,
        "predictions_made": job.predictions_made,
    }
