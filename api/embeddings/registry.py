# api/embeddings/registry.py
#
# Documentation registry for all embedding models available in (or relevant
# to) the webKinPred infrastructure.
#
# ─── How to use this when adding a new prediction method ─────────────────────
#
# 1. Find the embedding keys your method uses in EMBEDDING_REGISTRY below.
# 2. If `implemented` is True, the model is already installed in the Docker
#    image inside the listed `conda_env`.  You can invoke it by:
#      a. Reading the python path from PYTHON_PATHS[<python_path_key>] in
#         webKinPred/config_docker.py.
#      b. Passing that path as a subprocess command or as an environment
#         variable to your prediction script (see how KinForm does it in
#         api/prediction_engines/kinform.py).
# 3. If `implemented` is False, you will need to add a new conda environment
#    to the Dockerfile and document it here (set `implemented` to True).
#    Follow the existing Dockerfile layers as a template.
# 4. List the embedding key(s) your method uses in the `embeddings_used`
#    field of your MethodDescriptor (api/methods/<your_method>.py).
#
# ─────────────────────────────────────────────────────────────────────────────

EMBEDDING_REGISTRY: dict[str, dict] = {

    # ── Protein embeddings ────────────────────────────────────────────────────

    "esm2": {
        "name": "ESM-2 (Meta / Fair ESM)",
        "description": (
            "Protein language model trained on UniRef50.  Produces per-residue "
            "and pooled sequence embeddings."
        ),
        "implemented": True,
        "conda_env": "esm",
        "python_path_key": "esm2",   # key in config PYTHON_PATHS
        "used_by": ["KinForm-H", "KinForm-L", "CatPred"],
        "notes": (
            "Invoked as a subprocess by KinForm.  The python path is passed via "
            "the KINFORM_ESM_PATH environment variable.  Multi-layer embeddings "
            "are extracted in a single model-load pass. CatPred uses per-residue "
            "ESM2 features, so it bridges into a method-specific cache format "
            "rather than reusing the shared mean-vector cache directly."
        ),
    },

    "esmc": {
        "name": "ESMC (ESM-3 Cambrian)",
        "description": (
            "Protein language model from the ESM-3 family.  Produces "
            "CLS-token and per-residue embeddings."
        ),
        "implemented": True,
        "conda_env": "esmc",
        "python_path_key": "esmc",
        "used_by": ["KinForm-H", "KinForm-L"],
        "notes": (
            "Invoked as a subprocess by KinForm via KINFORM_ESMC_PATH."
        ),
    },

    "prot_t5": {
        "name": "ProtT5-XL-UniRef50",
        "description": (
            "Protein T5 transformer (Elnaggar et al. 2021).  Produces "
            "per-residue embeddings commonly used for downstream tasks."
        ),
        "implemented": True,
        "conda_env": "prot_t5",
        "python_path_key": "t5",
        "used_by": ["KinForm-H", "KinForm-L", "CataPro"],
        "notes": (
            "Invoked as a subprocess by KinForm via KINFORM_T5_PATH.  "
            "UniKP and CataPro also use ProtT5 internally."
        ),
    },

    "pseq2sites": {
        "name": "Pseq2Sites",
        "description": (
            "Predicts functional/active-site residues from protein sequence.  "
            "Used as a structural-context feature by KinForm."
        ),
        "implemented": True,
        "conda_env": "pseq2sites",
        "python_path_key": "pseq2sites",
        "used_by": ["KinForm-H", "KinForm-L"],
        "notes": (
            "Invoked as a subprocess by KinForm via KINFORM_PSEQ2SITES_PATH."
        ),
    },

    # ── Substrate / molecular embeddings ─────────────────────────────────────

    "farm": {
        "name": "FARM (Functional Attribute-based Representations for Molecules)",
        "description": (
            "Molecular embedding method that encodes functional chemical "
            "attributes.  Used by KinForm for substrate representation."
        ),
        "implemented": False,
        "conda_env": "kinform_env",   # bundled inside the KinForm environment
        "python_path_key": None,
        "used_by": ["KinForm-H", "KinForm-L"],
        "notes": (
            "Bundled inside the KinForm codebase and kinform_env; not yet "
            "exposed as a standalone shared embedding."
        ),
    },

    "unimol": {
        "name": "Uni-Mol",
        "description": (
            "3D molecular representation model based on a transformer trained "
            "on molecular conformations."
        ),
        "implemented": False,
        "conda_env": None,
        "python_path_key": None,
        "used_by": [],
        "notes": (
            "Not yet installed.  To use, add a conda env to the Dockerfile "
            "and register it in PYTHON_PATHS."
        ),
    },

    "chemprop_mpnn": {
        "name": "Chemprop (Message Passing Neural Network)",
        "description": (
            "Graph neural network for molecular property prediction.  "
            "Used internally by DLKcat for substrate encoding."
        ),
        "implemented": False,
        "conda_env": "dlkcat_env",    # bundled inside the DLKcat environment
        "python_path_key": None,
        "used_by": ["DLKcat"],
        "notes": (
            "Bundled inside the DLKcat codebase and dlkcat_env; not yet "
            "exposed as a standalone shared embedding."
        ),
    },
}


def get(key: str) -> dict:
    """Return metadata for the given embedding key.  Raises KeyError if unknown."""
    if key not in EMBEDDING_REGISTRY:
        raise KeyError(
            f"Unknown embedding key '{key}'. "
            f"Available: {sorted(EMBEDDING_REGISTRY)}"
        )
    return EMBEDDING_REGISTRY[key]


def implemented_embeddings() -> dict[str, dict]:
    """Return only the embeddings that are already installed in the Docker image."""
    return {k: v for k, v in EMBEDDING_REGISTRY.items() if v["implemented"]}
