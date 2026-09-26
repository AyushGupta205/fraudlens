-- ==============================================================================
-- FraudLens — Customer & Account Behavioral Risk SQL Suite
-- Platform: FraudLens — Financial Fraud Analytics & Detection Platform
-- ==============================================================================
-- Note: A single fraud-labeled transaction does not automatically mean an account 
-- is an attacker; accounts are categorized using objective behavioral risk scoring.
-- ==============================================================================

-- 1. Account-Level Behavioral Profile & Transparent Multi-Factor Risk Scoring (0–100)
-- Scoring Rules:
--   1. Origin Account Drainage (Liquidation to $0): +25 Points
--   2. High-Value Transaction (>= $200,000):        +20 Points
--   3. Extreme Value Transaction (>= $1,000,000):   +20 Points
--   4. High-Risk Channel (TRANSFER or CASH_OUT):    +15 Points
--   5. Unseeded Destination Target (Dest Bal = 0):  +10 Points
--   6. Confirmed Ground-Truth Label (isFraud = 1):  +10 Points
--   Total Score: SUM(Points) capped at 100.
-- Tiers:
--   - Critical: 76 – 100
--   - High:     51 – 75
--   - Medium:   26 – 50
--   - Low:       0 – 25

WITH TxScoring AS (
    SELECT 
        transaction_id,
        nameOrig AS account_id,
        amount,
        type,
        isFraud,
        zero_balance_origin_after_transaction AS is_drained,
        MIN(100, (
            (CASE WHEN zero_balance_origin_after_transaction = 1 THEN 25 ELSE 0 END) +
            (CASE WHEN amount >= 200000.0 THEN 20 ELSE 0 END) +
            (CASE WHEN amount >= 1000000.0 THEN 20 ELSE 0 END) +
            (CASE WHEN type IN ('TRANSFER', 'CASH_OUT') THEN 15 ELSE 0 END) +
            (CASE WHEN oldbalanceDest = 0.0 THEN 10 ELSE 0 END) +
            (CASE WHEN isFraud = 1 THEN 10 ELSE 0 END)
        )) AS risk_score
    FROM transactions
)
SELECT 
    account_id,
    amount AS transaction_amount,
    type AS channel,
    isFraud AS is_fraud,
    is_drained,
    risk_score,
    CASE 
        WHEN risk_score >= 76 THEN 'Critical'
        WHEN risk_score >= 51 THEN 'High'
        WHEN risk_score >= 26 THEN 'Medium'
        ELSE 'Low'
    END AS risk_category
FROM TxScoring
ORDER BY risk_score DESC, amount DESC
LIMIT 100;

-- 2. Risk Tier Aggregation & Distribution Across All Accounts
WITH TxScoring AS (
    SELECT 
        amount,
        isFraud,
        MIN(100, (
            (CASE WHEN zero_balance_origin_after_transaction = 1 THEN 25 ELSE 0 END) +
            (CASE WHEN amount >= 200000.0 THEN 20 ELSE 0 END) +
            (CASE WHEN amount >= 1000000.0 THEN 20 ELSE 0 END) +
            (CASE WHEN type IN ('TRANSFER', 'CASH_OUT') THEN 15 ELSE 0 END) +
            (CASE WHEN oldbalanceDest = 0.0 THEN 10 ELSE 0 END) +
            (CASE WHEN isFraud = 1 THEN 10 ELSE 0 END)
        )) AS risk_score
    FROM transactions
)
SELECT 
    CASE 
        WHEN risk_score >= 76 THEN 'Critical (76-100)'
        WHEN risk_score >= 51 THEN 'High (51-75)'
        WHEN risk_score >= 26 THEN 'Medium (26-50)'
        ELSE 'Low (0-25)'
    END AS risk_tier,
    COUNT(*) AS account_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM transactions), 2) AS pct_of_all_accounts,
    SUM(isFraud) AS fraud_account_count,
    ROUND(SUM(isFraud) * 100.0 / COUNT(*), 4) AS fraud_rate_within_tier_pct,
    ROUND(SUM(amount), 2) AS total_tier_volume
FROM TxScoring
GROUP BY risk_tier
ORDER BY MIN(risk_score) DESC;
