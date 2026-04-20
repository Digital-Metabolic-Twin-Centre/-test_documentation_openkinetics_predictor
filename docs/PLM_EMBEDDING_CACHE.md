# PLM Embedding Cache Guide

Use this guide if your method uses protein language model embeddings.

Goal: reuse the sequence cache so repeated sequences do not recompute embeddings.

## 1. Cache Key Rule

Always cache by `seq_id`, not by raw sequence text.

Resolve IDs once per batch with `seqmap`, then read/write cache artifacts by `seq_id`.

## 2. Shared Cache Layout (Current)

- UniKP / CataPro ProtT5 mean vectors:
  - `media/sequence_info/prot_t5_last/mean_vecs/{seq_id}.npy`
- TurNup ESM1b vectors:
  - `media/sequence_info/esm1b_turnup/{seq_id}.npy`
- EITLEM ESM1v full matrices (not pooled means):
  - `media/sequence_info/esm1v/{seq_id}.npy`
- KinForm multi-layer mean+weighted vectors:
  - `media/sequence_info/esm2_layer_26/{mean_vecs,weighted_vecs}/{seq_id}.npy`
  - `media/sequence_info/esm2_layer_29/{mean_vecs,weighted_vecs}/{seq_id}.npy`
  - `media/sequence_info/esmc_layer_24/{mean_vecs,weighted_vecs}/{seq_id}.npy`
  - `media/sequence_info/esmc_layer_32/{mean_vecs,weighted_vecs}/{seq_id}.npy`
  - `media/sequence_info/prot_t5_layer_19/{mean_vecs,weighted_vecs}/{seq_id}.npy`
  - `media/sequence_info/prot_t5_last/{mean_vecs,weighted_vecs}/{seq_id}.npy`

## 3. GPU Offload Profiles (v1)

The shared planner maps method/target to one profile and step-level missing work.

Supported v1 GPU profiles:

- `kinform_full`
  - `kinform_pseq2sites`
  - `kinform_esm2_layers`
  - `kinform_esmc_layers`
  - `kinform_prott5_layers`
- `prot_t5_mean` (CataPro, UniKP)
- `turnup_esm1b`

Not supported in v1:

- EITLEM GPU offload (full-matrix artifact path, deferred)
- CatPred GPU offload (phase 2)

## 4. Sparse Computation Rule

Do not recompute an entire profile if only part is missing.

For KinForm specifically:

- Missing work is computed per step and per sequence ID.
- If a sequence has ProtT5 cached but missing ESM2, only ESM2 step is requested.
- If a sequence has all embeddings cached, it is excluded from GPU work entirely.

## 5. Reuse Pattern (Load or Generate)

```python
from pathlib import Path
import numpy as np

def get_cached_or_compute(seq_ids, sequences, emb_dir):
    emb_dir.mkdir(parents=True, exist_ok=True)
    out = []
    for seq_id, seq in zip(seq_ids, sequences):
        fp = emb_dir / f"{seq_id}.npy"
        if fp.exists():
            vec = np.load(fp)
        else:
            vec = compute_embedding(seq)  # method-specific inference
            np.save(fp, vec)
        out.append(vec)
    return out
```

## 6. Adding a New PLM Cache

1. Add runtime env support (Dockerfile/config paths).
2. Add an entry in `api/embeddings/registry.py`.
3. Add method mapping in the shared embedding planner (`method -> profile`).
4. Define step-level missing criteria and required cache paths.
5. Ensure your prediction path can run with partial cache already present.
