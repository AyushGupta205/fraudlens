-- ==============================================================================
-- FraudLens — Fraud Analysis SQL Suite (10 Queries)
-- ==============================================================================

-- 1. Overall Fraud KPI Summary
SELECT 
    COUNT(*) AS total_transactions,
    ROUND(SUM(amount), 2) AS total_transaction_volume,
    SUM(isFraud) AS total_fraud_transactions,
    ROUND(SUM(CASE WHEN isFraud = 1 THEN amount ELSE 0 END), 2) AS fraud_labeled_exposure,
    ROUND(SUM(isFraud) * 100.0 / COUNT(*), 4) AS overall_fraud_rate_pct,
    ROUND(SUM(CASE WHEN isFraud = 1 THEN amount ELSE 0 END) * 100.0 / SUM(amount), 4) AS fraud_volume_share_pct
FROM transactions;

-- 2. Fraud by Transaction Type
SELECT 
    type,
    COUNT(*) AS total_transactions,
    SUM(isFraud) AS fraud_transactions,
    ROUND(SUM(isFraud) * 100.0 / COUNT(*), 4) AS fraud_rate_pct,
    ROUND(SUM(amount), 2) AS total_amount,
    ROUND(SUM(CASE WHEN isFraud = 1 THEN amount ELSE 0 END), 2) AS fraud_exposure_amount,
    ROUND(SUM(CASE WHEN isFraud = 1 THEN amount ELSE 0 END) * 100.0 / NULLIF(SUM(amount), 0), 4) AS fraud_exposure_rate_pct
FROM transactions
GROUP BY type
ORDER BY fraud_transactions DESC;

-- 3. Rank Transaction Types by Fraud Rate
SELECT 
    type,
    COUNT(*) AS total_transactions,
    SUM(isFraud) AS fraud_transactions,
    ROUND(SUM(isFraud) * 100.0 / COUNT(*), 4) AS fraud_rate_pct,
    DENSE_RANK() OVER (ORDER BY (SUM(isFraud) * 1.0 / COUNT(*)) DESC) AS fraud_rate_rank
FROM transactions
GROUP BY type;

-- 4. Rank Transaction Types by Fraud Count with Window Share
SELECT 
    type,
    COUNT(*) AS total_transactions,
    SUM(isFraud) AS fraud_transactions,
    ROUND(SUM(isFraud) * 100.0 / SUM(SUM(isFraud)) OVER (), 2) AS pct_of_total_fraud_count,
    DENSE_RANK() OVER (ORDER BY SUM(isFraud) DESC) AS fraud_count_rank
FROM transactions
GROUP BY type;

-- 5. Fraud Amount Distribution Across Value Bands
SELECT 
    CASE 
        WHEN amount = 0 THEN '1. Zero Value ($0)'
        WHEN amount > 0 AND amount <= 10000 THEN '2. Micro ($0 - $10k)'
        WHEN amount > 10000 AND amount <= 100000 THEN '3. Low ($10k - $100k)'
        WHEN amount > 100000 AND amount <= 200000 THEN '4. Medium ($100k - $200k)'
        WHEN amount > 200000 AND amount <= 1000000 THEN '5. High ($200k - $1M)'
        WHEN amount > 1000000 AND amount <= 5000000 THEN '6. Very High ($1M - $5M)'
        ELSE '7. Extreme (> $5M)'
    END AS amount_band,
    COUNT(*) AS total_transactions,
    SUM(isFraud) AS fraud_transactions,
    ROUND(SUM(isFraud) * 100.0 / COUNT(*), 4) AS fraud_rate_pct,
    ROUND(SUM(CASE WHEN isFraud = 1 THEN amount ELSE 0 END), 2) AS fraud_exposure
FROM transactions
GROUP BY amount_band
ORDER BY amount_band;

-- 6. Parametric Amount Comparison: Fraudulent vs Legitimate
SELECT 
    isFraud,
    CASE WHEN isFraud = 1 THEN 'Fraudulent' ELSE 'Legitimate' END AS label,
    COUNT(*) AS transaction_count,
    ROUND(AVG(amount), 2) AS mean_amount,
    ROUND(MIN(amount), 2) AS min_amount,
    ROUND(MAX(amount), 2) AS max_amount,
    ROUND(SUM(amount), 2) AS total_volume
FROM transactions
GROUP BY isFraud;

-- 7. High-Value Fraud Exposure Concentration with Window Percentages
SELECT 
    CASE WHEN amount >= 200000.0 THEN 'High-Value (>= $200k)' ELSE 'Standard (< $200k)' END AS value_tier,
    COUNT(*) AS total_transactions,
    SUM(isFraud) AS fraud_transactions,
    ROUND(SUM(isFraud) * 100.0 / COUNT(*), 4) AS fraud_rate_pct,
    ROUND(SUM(isFraud) * 100.0 / SUM(SUM(isFraud)) OVER (), 2) AS share_of_all_fraud_count_pct,
    ROUND(SUM(CASE WHEN isFraud = 1 THEN amount ELSE 0 END), 2) AS fraud_exposure,
    ROUND(SUM(CASE WHEN isFraud = 1 THEN amount ELSE 0 END) * 100.0 / 
          SUM(SUM(CASE WHEN isFraud = 1 THEN amount ELSE 0 END)) OVER (), 2) AS share_of_all_fraud_exposure_pct
FROM transactions
GROUP BY value_tier;

-- 8. isFlaggedFraud Rule Effectiveness & Confusion Matrix Metrics
WITH FlagEvaluation AS (
    SELECT 
        SUM(CASE WHEN isFlaggedFraud = 1 AND isFraud = 1 THEN 1 ELSE 0 END) AS TP,
        SUM(CASE WHEN isFlaggedFraud = 1 AND isFraud = 0 THEN 1 ELSE 0 END) AS FP,
        SUM(CASE WHEN isFlaggedFraud = 0 AND isFraud = 1 THEN 1 ELSE 0 END) AS FN,
        SUM(CASE WHEN isFlaggedFraud = 0 AND isFraud = 0 THEN 1 ELSE 0 END) AS TN
    FROM transactions
)
SELECT 
    TP, FP, FN, TN,
    (TP + FP) AS total_flagged,
    (TP + FN) AS total_actual_fraud,
    ROUND(TP * 100.0 / NULLIF(TP + FP, 0), 4) AS precision_pct,
    ROUND(TP * 100.0 / NULLIF(TP + FN, 0), 4) AS recall_pct,
    ROUND(2.0 * (TP * 1.0 / NULLIF(TP + FP, 0)) * (TP * 1.0 / NULLIF(TP + FN, 0)) / 
          NULLIF((TP * 1.0 / NULLIF(TP + FP, 0)) + (TP * 1.0 / NULLIF(TP + FN, 0)), 0), 6) AS f1_score
FROM FlagEvaluation;

-- 9. Origin Account Drainage Behavior with Window Share
SELECT 
    zero_balance_origin_after_transaction AS is_account_drained,
    COUNT(*) AS total_transactions,
    SUM(isFraud) AS fraud_transactions,
    ROUND(SUM(isFraud) * 100.0 / COUNT(*), 4) AS fraud_rate_pct,
    ROUND(SUM(isFraud) * 100.0 / SUM(SUM(isFraud)) OVER (), 2) AS share_of_total_fraud_pct
FROM transactions
GROUP BY zero_balance_origin_after_transaction;

-- 10. Origin Drainage Disparity: Fraud vs Legitimate Breakdown
SELECT 
    CASE WHEN isFraud = 1 THEN 'Fraudulent' ELSE 'Legitimate' END AS class_label,
    COUNT(*) AS total_class_transactions,
    SUM(CASE WHEN zero_balance_origin_after_transaction = 1 THEN 1 ELSE 0 END) AS drainage_count,
    ROUND(SUM(CASE WHEN zero_balance_origin_after_transaction = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS drainage_rate_within_class_pct
FROM transactions
GROUP BY isFraud;
