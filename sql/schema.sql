-- FraudLens Database Schema (SQLite Analytical Schema)
-- Platform: FraudLens — Financial Fraud Analytics & Detection Platform

DROP TABLE IF EXISTS transactions;

CREATE TABLE transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    step INTEGER NOT NULL,
    type VARCHAR(20) NOT NULL,
    amount REAL NOT NULL,
    nameOrig VARCHAR(50) NOT NULL,
    oldbalanceOrg REAL NOT NULL,
    newbalanceOrig REAL NOT NULL,
    nameDest VARCHAR(50) NOT NULL,
    oldbalanceDest REAL NOT NULL,
    newbalanceDest REAL NOT NULL,
    isFraud INTEGER NOT NULL DEFAULT 0,
    isFlaggedFraud INTEGER NOT NULL DEFAULT 0,
    transaction_hour INTEGER NOT NULL,
    transaction_day INTEGER NOT NULL,
    origin_balance_change REAL NOT NULL,
    destination_balance_change REAL NOT NULL,
    orig_balance_error REAL NOT NULL,
    dest_balance_error REAL NOT NULL,
    orig_balance_consistency VARCHAR(50) NOT NULL,
    amount_to_origin_balance_ratio REAL NOT NULL,
    amount_to_destination_balance_ratio REAL NOT NULL,
    zero_balance_origin_after_transaction INTEGER NOT NULL,
    zero_balance_destination_after_transaction INTEGER NOT NULL
);

-- Performance Indexes for High-Speed Analytical Queries
CREATE INDEX IF NOT EXISTS idx_tx_step ON transactions(step);
CREATE INDEX IF NOT EXISTS idx_tx_type ON transactions(type);
CREATE INDEX IF NOT EXISTS idx_tx_nameOrig ON transactions(nameOrig);
CREATE INDEX IF NOT EXISTS idx_tx_nameDest ON transactions(nameDest);
CREATE INDEX IF NOT EXISTS idx_tx_isFraud ON transactions(isFraud);
CREATE INDEX IF NOT EXISTS idx_tx_isFlaggedFraud ON transactions(isFlaggedFraud);
CREATE INDEX IF NOT EXISTS idx_tx_type_isFraud ON transactions(type, isFraud);
CREATE INDEX IF NOT EXISTS idx_tx_drainage ON transactions(zero_balance_origin_after_transaction);
CREATE INDEX IF NOT EXISTS idx_tx_hour ON transactions(transaction_hour);
CREATE INDEX IF NOT EXISTS idx_tx_amount ON transactions(amount);
