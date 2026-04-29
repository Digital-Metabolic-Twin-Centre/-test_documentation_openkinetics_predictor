from datetime import datetime

project = "Test Documentation Openkinetics Predictor"
author = "Digital Metabolic Twin Centre"
copyright = f"{datetime.now().year}, {author}"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "autoapi.extension",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_css_files = ["custom-wide.css"]


autoapi_type = "python"
autoapi_dirs = ["../../autoapi_include"]
autoapi_keep_files = False
autoapi_generate_api_docs = True
