# CatPred

This directory is reserved for the CatPred integration.

Expected contents:
- a checkout of the CatPred repository rooted at `models/CatPred/`
- the adapter entrypoint at `models/CatPred/catpred/integration/webkinpred_adapter.py`

Local development can instead point webKinPred at an external CatPred checkout:

```bash
export WEBKINPRED_CATPRED_ROOT="/absolute/path/to/CatPred"
export WEBKINPRED_CATPRED_PYTHON="/absolute/path/to/CatPred/.venv/bin/python"
```

Docker/runtime notes:
- `webKinPred/config_docker.py` defaults to `/app/models/CatPred`
- the CatPred subprocess descriptor sets `CATPRED_REPO_ROOT`, `CATPRED_MEDIA_PATH`, and `CATPRED_TOOLS_PATH`
- CatPred kcat/Km use per-residue ESM2 features and cache them under
  `media/sequence_info/esm2_last/per_residue/{seq_id}.pt`
