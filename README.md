# Taxonomic Entity Augmentation (TEA)

TEA is a text augmentation tool that helps prevent machine learning models from overfitting to important but repetitive content in NLP examples that use biological texts as source material. TEA targets taxonomic species names and strain names by either switching them into other valid taxonomic names automatically or by scrambling defined strain names from the text.

# Installation

Hugging Face library compatible tokenizer is currently the only dependency.

```bash
pip install transformers
```

Clone this repository and run the following to install TEA:

```bash
pip install .
```
