# api/methods/catpred.py
#
# Method descriptor for CatPred.

from api.methods.base import MethodDescriptor, SubprocessEngineConfig


descriptor = MethodDescriptor(
    key="CatPred",
    display_name="CatPred",
    authors=(
        "Veda Sheersh Boorla, Somtirtha Santra, Costas D. Maranas"
    ),
    publication_title=(
        "CatPred: A comprehensive framework for deep learning in vitro enzyme kinetic parameters"
    ),
    citation_url="https://www.nature.com/articles/s41467-025-57215-9",
    repo_url="https://github.com/maranasgroup/CatPred",
    more_info=(
        "CatPred currently integrates kcat and Km through a local CPU inference "
        "adapter. Ki remains outside the current webKinPred target model."
    ),

    supports=["kcat", "Km"],
    input_format="single",
    output_cols={
        "kcat": "kcat (1/s)",
        "Km": "KM (mM)",
    },
    max_seq_len=2048,
    col_to_kwarg={"Substrate": "substrates"},
    target_kwargs={
        "kcat": {"kinetics_type": "KCAT"},
        "Km": {"kinetics_type": "KM"},
    },
    subprocess=SubprocessEngineConfig(
        python_path_key="CatPred",
        script_key="CatPred",
        data_path_env={
            "CATPRED_REPO_ROOT": "CatPred",
            "CATPRED_MEDIA_PATH": "media",
            "CATPRED_TOOLS_PATH": "tools",
            "PYTHONPATH": "CatPred",
        },
        extra_env={
            "PROTEIN_EMBED_USE_CPU": "1",
        },
    ),
    embeddings_used=["esm2"],
)
