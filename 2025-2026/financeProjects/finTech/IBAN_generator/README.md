# Bulk IBAN Generator (Prototype)

Tkinter desktop prototype that parses account records and generates FR IBAN values.

## Main Files

- `bulk_iban_generator.py`: parsing logic, IBAN checksum computation, and GUI.
- `bankaccount.txt`: sample raw input text.
- `Calculated_IBANS.csv`, `saved_iban.txt`: sample outputs.
- `BankAcc_analysis.ipynb`: exploratory notebook.

## Requirements

- Python 3.x
- `pandas`, `nltk`, `tkinter`

## Run

- `python bulk_iban_generator.py`

## Expected Input Blocks

1. `Code banque`
2. `Code agence`
3. `Numero de compte bancaire`
4. `Chiffre d'indicatif national`

## Notes

- This is a prototype with strict assumptions on raw text format.
- Pre-cleaning input data significantly improves generation reliability.
