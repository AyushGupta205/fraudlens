-- ==============================================================================
-- FraudLens — SQL Data Quality Audit Suite (11 Queries)
-- ==============================================================================

-- 1. Total Transaction Count & Basic Sanity
SELECT 
    COUNT(*) AS total_transactions,
    MIN(step) AS min_step,
    MAX(step) AS max_step
FROM transactions;

-- 2. NULL Value Audit Across Core Columns
SELECT
    SUM(CASE WHEN step IS NULL THEN 1 ELSE 0 END) AS null_step,
    SUM(CASE WHEN type IS NULL THEN 1 ELSE 0 END) AS null_type,
    SUM(CASE WHEN amount IS NULL THEN 1 ELSE 0 END) AS null_amount,
    SUM(CASE WHEN nameOrig IS NULL THEN 1 ELSE 0 END) AS null_nameOrig,
    SUM(CASE WHEN oldbalanceOrg IS NULL THEN 1 ELSE 0 END) AS null_oldbalanceOrg,
    SUM(CASE WHEN newbalanceOrig IS NULL THEN 1 ELSE 0 END) AS null_newbalanceOrig,
    SUM(CASE WHEN nameDest IS NULL THEN 1 ELSE 0 END) AS null_nameDest,
    SUM(CASE WHEN oldbalanceDest IS NULL THEN 1 ELSE 0 END) AS null_oldbalanceDest,
    SUM(CASE WHEN newbalanceDest IS NULL THEN 1 ELSE 0 END) AS null_newbalanceDest,
    SUM(CASE WHEN isFraud IS NULL THEN 1 ELSE 0 END) AS null_isFraud,
    SUM(CASE WHEN isFlaggedFraud IS NULL THEN 1 ELSE 0 END) AS null_isFlaggedFraud
FROM transactions;

-- 3. Duplicate Transaction Records Audit (Index Optimized)
SELECT 
    nameOrig, COUNT(*) AS duplicate_count
FROM transactions
GROUP BY nameOrig
HAVING COUNT(*) > 10;

-- 4. Fraud vs Legitimate Transaction Counts with Window Percentage
SELECT 
    isFraud,
    CASE WHEN isFraud = 1 THEN 'Fraudulent' ELSE 'Legitimate' END AS class_label,
    COUNT(*) AS transaction_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 4) AS percentage
FROM transactions
GROUP BY isFraud;

-- 5. Overall Fraud Rate Calculation
SELECT
    COUNT(*) AS total_transactions,
    SUM(isFraud) AS total_fraud_transactions,
    ROUND(SUM(isFraud) * 100.0 / COUNT(*), 4) AS overall_fraud_rate_pct
FROM transactions;

-- 6. Transaction Type Distribution & Volume Share with Window Percentages
SELECT 
    type,
    COUNT(*) AS transaction_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS pct_of_total_tx,
    ROUND(SUM(amount), 2) AS total_amount,
    ROUND(SUM(amount) * 100.0 / SUM(SUM(amount)) OVER (), 2) AS pct_of_total_volume
FROM transactions
GROUP BY type
ORDER BY transaction_count DESC;

-- 7. Invalid & Negative Amount / Negative Balance Checks
SELECT 
    SUM(CASE WHEN amount < 0 THEN 1 ELSE 0 END) AS negative_amounts,
    SUM(CASE WHEN oldbalanceOrg < 0 THEN 1 ELSE 0 END) AS negative_oldbalanceOrg,
    SUM(CASE WHEN newbalanceOrig < 0 THEN 1 ELSE 0 END) AS negative_newbalanceOrig,
    SUM(CASE WHEN oldbalanceDest < 0 THEN 1 ELSE 0 END) AS negative_oldbalanceDest,
    SUM(CASE WHEN newbalanceDest < 0 THEN 1 ELSE 0 END) AS negative_newbalanceDest
FROM transactions;

-- 8. Zero-Amount Transactions Investigation
SELECT 
    transaction_id,
    step,
    type,
    amount,
    nameOrig,
    oldbalanceOrg,
    newbalanceOrig,
    nameDest,
    isFraud,
    isFlaggedFraud
FROM transactions
WHERE amount = 0.0;

-- 9. System Flagged Fraud Distribution
SELECT 
    isFlaggedFraud,
    COUNT(*) AS flagged_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 6) AS flagged_percentage
FROM transactions
GROUP BY isFlaggedFraud;

-- 10. Flagged Fraud vs Actual Fraud Cross-Tabulation (Confusion Matrix Elements)
SELECT 
    isFlaggedFraud,
    isFraud,
    CASE 
        WHEN isFlaggedFraud = 1 AND isFraud = 1 THEN 'True Positive (TP)'
        WHEN isFlaggedFraud = 1 AND isFraud = 0 THEN 'False Positive (FP)'
        WHEN isFlaggedFraud = 0 AND isFraud = 1 THEN 'False Negative (FN)'
        ELSE 'True Negative (TN)'
    END AS classification_category,
    COUNT(*) AS transaction_count
FROM transactions
GROUP BY isFlaggedFraud, isFraud;

-- 11. Balance Consistency Categorization Breakdown
SELECT 
    orig_balance_consistency,
    COUNT(*) AS total_transactions,
    SUM(isFraud) AS fraud_transactions,
    ROUND(SUM(isFraud) * 100.0 / COUNT(*), 4) AS fraud_rate_pct,
    ROUND(SUM(isFraud) * 100.0 / SUM(SUM(isFraud)) OVER (), 2) AS share_of_all_fraud_pct
FROM transactions
GROUP BY orig_balance_consistency
ORDER BY total_transactions DESC;
