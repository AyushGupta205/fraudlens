-- ==============================================================================
-- FraudLens — Financial Exposure & Value Analysis SQL Suite
-- Platform: FraudLens — Financial Fraud Analytics & Detection Platform
-- ==============================================================================

-- 1. Financial Exposure Summary: Total, Fraud-Labeled, and Legitimate Volume
SELECT 
    COUNT(*) AS total_transactions,
    ROUND(SUM(amount), 2) AS total_financial_volume,
    ROUND(SUM(CASE WHEN isFraud = 0 THEN amount ELSE 0 END), 2) AS legitimate_transaction_volume,
    ROUND(SUM(CASE WHEN isFraud = 1 THEN amount ELSE 0 END), 2) AS fraud_labeled_exposure,
    ROUND(SUM(CASE WHEN isFraud = 1 THEN amount ELSE 0 END) * 100.0 / SUM(amount), 4) AS fraud_exposure_share_pct,
    ROUND(AVG(CASE WHEN isFraud = 0 THEN amount ELSE NULL END), 2) AS avg_legitimate_amount,
    ROUND(AVG(CASE WHEN isFraud = 1 THEN amount ELSE NULL END), 2) AS avg_fraud_labeled_amount,
    ROUND(AVG(CASE WHEN isFraud = 1 THEN amount ELSE NULL END) / 
          NULLIF(AVG(CASE WHEN isFraud = 0 THEN amount ELSE NULL END), 0), 2) AS fraud_to_legit_mean_multiplier
FROM transactions;

-- 2. Fraud Exposure Distribution by Transaction Channel with Window Share
SELECT 
    type,
    COUNT(*) AS total_transactions,
    SUM(isFraud) AS fraud_transactions,
    ROUND(SUM(amount), 2) AS total_channel_volume,
    ROUND(SUM(CASE WHEN isFraud = 1 THEN amount ELSE 0 END), 2) AS fraud_labeled_exposure,
    ROUND(SUM(CASE WHEN isFraud = 1 THEN amount ELSE 0 END) * 100.0 / 
          SUM(SUM(CASE WHEN isFraud = 1 THEN amount ELSE 0 END)) OVER (), 2) AS share_of_total_fraud_exposure_pct,
    ROUND(AVG(CASE WHEN isFraud = 1 THEN amount ELSE NULL END), 2) AS avg_fraud_transaction_amount,
    ROUND(MAX(CASE WHEN isFraud = 1 THEN amount ELSE 0 END), 2) AS max_fraud_transaction_amount
FROM transactions
GROUP BY type
ORDER BY fraud_labeled_exposure DESC;

-- 3. High-Value Exposure Tiers Breakdown with Window Share
SELECT 
    CASE 
        WHEN amount >= 5000000.0 THEN 'Extreme Tier (>= $5.0M)'
        WHEN amount >= 1000000.0 THEN 'Major Tier ($1.0M - $5.0M)'
        WHEN amount >= 200000.0  THEN 'Substantial Tier ($200k - $1.0M)'
        WHEN amount >= 50000.0   THEN 'Mid Tier ($50k - $200k)'
        ELSE 'Micro/Low Tier (< $50k)'
    END AS financial_tier,
    COUNT(*) AS total_transactions,
    SUM(isFraud) AS fraud_transactions,
    ROUND(SUM(isFraud) * 100.0 / COUNT(*), 4) AS fraud_rate_pct,
    ROUND(SUM(amount), 2) AS total_tier_volume,
    ROUND(SUM(CASE WHEN isFraud = 1 THEN amount ELSE 0 END), 2) AS fraud_labeled_exposure,
    ROUND(SUM(CASE WHEN isFraud = 1 THEN amount ELSE 0 END) * 100.0 / 
          SUM(SUM(CASE WHEN isFraud = 1 THEN amount ELSE 0 END)) OVER (), 2) AS share_of_fraud_exposure_pct
FROM transactions
GROUP BY financial_tier
ORDER BY MIN(amount) DESC;

-- 4. Top 20 Fraud Exposure Incidents (Single-Transaction Maximums)
SELECT 
    transaction_id,
    step,
    transaction_day,
    transaction_hour,
    type,
    amount AS fraud_labeled_amount,
    nameOrig,
    nameDest,
    oldbalanceOrg,
    newbalanceOrig,
    zero_balance_origin_after_transaction AS drained_origin,
    isFlaggedFraud
FROM transactions
WHERE isFraud = 1
ORDER BY amount DESC, step ASC
LIMIT 20;
