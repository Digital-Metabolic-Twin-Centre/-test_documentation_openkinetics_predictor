import os
from webKinPred.similarity_dataset_registry import SIMILARITY_DATASET_REGISTRY

# Base paths for Docker container
BASE_PATH = '/app'
DATA_PATH = '/app'

# Docker paths for conda environments (using the same names as exported)
PYTHON_PATHS = {
    'DLKcat': '/opt/conda/envs/dlkcat_env/bin/python',
    'EITLEM': '/opt/conda/envs/eitlem_env/bin/python', 
    'TurNup': '/opt/conda/envs/turnup_env/bin/python',
    'UniKP': '/opt/conda/envs/unikp/bin/python', 
    'KinForm': '/opt/conda/envs/kinform_env/bin/python',
    'esm2': '/opt/conda/envs/esm/bin/python',
    'esmc': '/opt/conda/envs/esmc/bin/python',
    't5': '/opt/conda/envs/prot_t5/bin/python',
    'pseq2sites': '/opt/conda/envs/pseq2sites/bin/python'
}

# Data paths for each model in Docker
DATA_PATHS = {
    'DLKcat': '/app/api/DLKcat/DeeplearningApproach/Data',
    'DLKcat_Results': '/app/api/DLKcat/DeeplearningApproach/Results',
    'EITLEM': '/app/api/EITLEM',
    'TurNup': '/app/api/TurNup/data',
    'UniKP': '/app/api/UniKP-main',
    "KinForm": '/app/api/KinForm/results',
    'media': '/app/media',
    'tools': '/app/tools',
}

# Prediction scripts paths (adapted for Docker container)
PREDICTION_SCRIPTS = {
    'DLKcat': '/app/api/DLKcat/DeeplearningApproach/Code/example/prediction_for_input.py',
    'EITLEM': '/app/api/EITLEM/Code/eitlem_prediction_script_batch.py',
    'TurNup': '/app/api/TurNup/code/kcat_prediction_batch.py',
    'UniKP': '/app/api/UniKP-main/run_unikp_batch.py',
    'KinForm': '/app/api/KinForm/code/main.py',
}

# MMseqs similarity datasets (adapted for Docker container)
FASTAS_DIR = "/app/fastas"
SIMILARITY_DATASETS = {
    label: {
        "label": label,
        "fasta": f"{FASTAS_DIR}/{meta['fasta_filename']}",
        "target_db": f"{FASTAS_DIR}/dbs/{meta['db_name']}",
    }
    for label, meta in SIMILARITY_DATASET_REGISTRY.items()
}

# Backward-compatible shape used by existing similarity code paths.
TARGET_DBS = {label: item["target_db"] for label, item in SIMILARITY_DATASETS.items()}

# Other config variables
# Set to None if mmseqs2 is installed directly on PATH (e.g. in Dockerfile.web).
# Set to "/opt/conda/bin/conda" if running inside the full worker image.
CONDA_PATH = None
# Per-method sequence-length limits are now defined in each method descriptor
# (api/methods/<method>.py) and derived via api.methods.registry.get_model_limits().
# Do not add MODEL_LIMITS back here.
SERVER_LIMIT = 10000
DEBUG = True
ALLOWED_FRONTEND_IPS = ["127.0.0.1", "localhost", "frontend", "backend"]

# Docker paths for experimental data
KM_CSV = '/app/media/experimental/km_experimental.csv'
KCAT_CSV = '/app/media/experimental/kcat_experimental.csv'
