# Taxonomic Entity Augmentation (TEA)

TEA is a text augmentation tool that helps prevent machine learning models from overfitting to important but repetitive content in NLP examples that use biological texts as source material. TEA targets taxonomic species names and strain names by either switching them into other valid taxonomic names automatically or by scrambling defined strain names from the text.

# Installation

You will need a Hugging Face library compatible tokenizer. You can install Transformers package from Hugging Face, which includes the required dependency. Run the following to do this:

```bash
pip install transformers
```

Next, clone this repository and run the following to install TEA as a Python package:

```bash
cd TEA
pip install .
```

# Quickstart

The package provides two general text augmentation strategies. 

To switch species:
```python
from transformers import AutoTokenizer
from tea import TEA

tokenizer = AutoTokenizer.from_pretrained('dmis-lab/biobert-base-cased-v1.2', do_lower_case=False, model_max_length=100000)
tea = TEA(tokenizer)

tea.switch('Hello E. coli!')
# => 'Hello D. cephalotes!'
```

To scramble strains:
```python
from transformers import AutoTokenizer
from tea import TEA

tokenizer = AutoTokenizer.from_pretrained('dmis-lab/biobert-base-cased-v1.2', do_lower_case=False, model_max_length=100000)
tea = TEA(tokenizer)

tea.scramble('E. coli strain HB101 is a handy laboratory strain for molecular biology laboratory work.', ['HB101'])
# => 'E. coli strain FQ414 is a handy laboratory strain for molecular biology.'

# this also works
tea.scramble('E. coli strain HB101 is a handy laboratory strain for molecular biology laboratory work.', ['strain HB101'])
# => 'E. coli strain SW565 is a handy laboratory strain for molecular biology.'
```

# Dataset generation

An example script (gen_strategy.py) is provided for example usage of TEA as part of a more advanced dataset generation pipeline. The example script assumes that [TEA_curated_data](https://github.com/tznurmin/TEA_curated_data) is cloned into the same directory.
