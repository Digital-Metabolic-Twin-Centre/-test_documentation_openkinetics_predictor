# api/embeddings/__init__.py
#
# This package documents the shared embedding infrastructure available in the
# webKinPred Docker image.  When adding a new prediction method, check
# api/embeddings/registry.py to see which protein and substrate embedding
# models are already installed — you may be able to reuse them without
# adding a new conda environment.
