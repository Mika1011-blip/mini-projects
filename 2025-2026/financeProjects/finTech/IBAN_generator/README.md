# Bulk IBAN Generator (Prototype)

Tkinter desktop prototype that parses bank account fields and generates FR IBAN values.

## Main Files

- `bulk_iban_generator.py` : parser, IBAN key computation, and GUI.
- `bankaccount.txt` : sample raw input text.
- `Calculated_IBANS.csv`, `saved_iban.txt` : sample outputs.
- `BankAcc_analysis.ipynb` : exploratory notebook.

## Requirements

- Python 3.x
- `pandas`, `nltk`, `tkinter`

## Run

- `python bulk_iban_generator.py`

## Input Format

The parser expects blocks containing:

1. `Code banque`
2. `Code agence`
3. `Numero de compte bancaire`
4. `Chiffre d'indicatif national`

## Notes

- This is a beta/prototype script and contains strict assumptions on text format.
- Clean input data before generation for reliable output.
