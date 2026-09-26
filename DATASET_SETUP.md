# Dataset Setup Guide ? PaySim Financial Fraud Dataset

## 1. Dataset Overview
- **Dataset Name**: PaySim Synthetic Financial Dataset for Fraud Detection
- **Creators / Citation**: E. A. Lopez-Rojas, A. Elmir, and S. Axelsson. "PaySim: A financial mobile money simulator for fraud detection", In The 28th European Modeling and Simulation Symposium (EMSS), Larnaca, Cyprus, 2016.
- **License**: Creative Commons Attribution-ShareAlike 4.0 International ([CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/))
- **Scale**: ~6.36 Million transactions, 11 features, 1 target column (isFraud).

---

## 2. Official Download Sources
You can acquire the authentic raw CSV dataset from either of the following official repositories:

1. **Kaggle**:
   - URL: [https://www.kaggle.com/datasets/ealaxi/paysim1](https://www.kaggle.com/datasets/ealaxi/paysim1)
   - Filename: PS_20174392719_1491204439457_log.csv (or renamed to paysim.csv)

2. **Automated Download via KaggleHub (Python)**:
   `python
   import kagglehub
   path = kagglehub.dataset_download('ealaxi/paysim1')
   print('Downloaded to:', path)
   `

---

## 3. Placement in Project Directory
Place the downloaded CSV in either of the following locations:

- Primary Project Location: data/raw/PS_20174392719_1491204439457_log.csv (or data/raw/paysim.csv)
- Configurable Environment Path: Set FRAUDLENS_DATA_PATH in your .env file:
  `env
  FRAUDLENS_DATA_PATH=data/raw/PS_20174392719_1491204439457_log.csv
  `

---

## 4. Verification
Run the inspection script to verify that the dataset is loaded and validated:
`ash
python -m src.data.inspect_data
`
