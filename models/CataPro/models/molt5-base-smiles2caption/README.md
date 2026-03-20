---
license: apache-2.0
---


This model can be used to generate an input caption from a SMILES string.

## Example Usage
```python
from transformers import T5Tokenizer, T5ForConditionalGeneration

tokenizer = T5Tokenizer.from_pretrained("laituan245/molt5-base-smiles2caption", model_max_length=512)
model = T5ForConditionalGeneration.from_pretrained('laituan245/molt5-base-smiles2caption')

input_text = 'C1=CC2=C(C(=C1)[O-])NC(=CC2=O)C(=O)O'
input_ids = tokenizer(input_text, return_tensors="pt").input_ids

outputs = model.generate(input_ids, num_beams=5, max_length=512)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

## Paper

For more information, please take a look at our paper.

Paper: [Translation between Molecules and Natural Language](https://arxiv.org/abs/2204.11817)

Authors: *Carl Edwards\*, Tuan Lai\*, Kevin Ros, Garrett Honke, Heng Ji* 
