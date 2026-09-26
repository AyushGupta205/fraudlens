-- ==============================================================================
-- FraudLens — Advanced SQL Analytics Suite (10 Queries)
-- Window Functions, Multi-Level CTEs, Running Aggregates & Anomaly Scoring
-- ==============================================================================

-- 1. CTE-Based Channel Contribution & Exposure Share with Window Aggregation
WITH ChannelFraudStats AS (
    SELECT 
        type,
        COUNT(*) AS total_tx,
        SUM(isFraud) AS fraud_tx,
        SUM(amount) AS total_vol,
        SUM(CASE WHEN isFraud = 1 THEN amount ELSE 0 END) AS fraud_vol
    FROM transactions
    GROUP BY type
)
SELECT 
    type,
    total_tx,
    fraud_tx,
    ROUND(fraud_tx * 100.0 / NULLIF(total_tx, 0), 4) AS channel_fraud_rate_pct,
    ROUND(fraud_vol, 2) AS fraud_exposure_amount,
    ROUND(fraud_vol * 100.0 / SUM(fraud_vol) OVER (), 2) AS pct_of_total_fraud_exposure,
    DENSE_RANK() OVER (ORDER BY fraud_vol DESC) AS exposure_rank
FROM ChannelFraudStats
ORDER BY exposure_rank;

-- 2. Daily Running Cumulative Fraud Exposure over 31-Day Simulation Horizon
WITH DailyFraudExposure AS (
    SELECT 
        transaction_day,
        COUNT(*) AS daily_total_tx,
        SUM(isFraud) AS daily_fraud_tx,
        ROUND(SUM(CASE WHEN isFraud = 1 THEN amount ELSE 0 END), 2) AS daily_fraud_exposure
    FROM transactions
    GROUP BY transaction_day
)
SELECT 
    transaction_day,
    daily_total_tx,
    daily_fraud_tx,
    daily_fraud_exposure,
    ROUND(SUM(daily_fraud_exposure) OVER (ORDER BY transaction_day), 2) AS cumulative_fraud_exposure,
    ROUND(SUM(daily_fraud_tx) OVER (ORDER BY transaction_day) * 100.0 / 
          (SELECT SUM(isFraud) FROM transactions), 2) AS cumulative_fraud_count_pct
FROM DailyFraudExposure
ORDER BY transaction_day;

-- 3. Top-N Highest Fraud Value Exposure Incidents with Dense Ranking
WITH RankedFraudIncidents AS (
    SELECT 
        transaction_id,
        step,
        transaction_day,
        transaction_hour,
        type,
        amount,
        nameOrig,
        nameDest,
        oldbalanceOrg,
        newbalanceOrig,
        DENSE_RANK() OVER (PARTITION BY type ORDER BY amount DESC) AS channel_amount_rank,
        ROW_NUMBER() OVER (ORDER BY amount DESC, step ASC) AS global_amount_rank
    FROM transactions
    WHERE isFraud = 1
)
SELECT 
    global_amount_rank,
    channel_amount_rank,
    transaction_id,
    step,
    type,
    amount,
    nameOrig,
    nameDest,
    oldbalanceOrg
FROM RankedFraudIncidents
WHERE global_amount_rank <= 25;

-- 4. Anomaly Detection: Transactions Exceeding 10x Global Channel Baseline Average
WITH ChannelBaselines AS (
    SELECT type, AVG(amount) AS channel_avg_amount
    FROM transactions
    GROUP BY type
)
SELECT 
    t.type,
    COUNT(*) AS total_extreme_anomalies,
    SUM(t.isFraud) AS fraud_anomalies,
    ROUND(SUM(t.isFraud) * 100.0 / COUNT(*), 4) AS anomaly_fraud_rate_pct,
    ROUND(AVG(t.amount), 2) AS avg_anomaly_amount,
    ROUND(b.channel_avg_amount, 2) AS channel_baseline_avg
FROM transactions t
JOIN ChannelBaselines b ON t.type = b.type
WHERE t.amount > (b.channel_avg_amount * 10.0)
GROUP BY t.type
ORDER BY total_extreme_anomalies DESC;

-- 5. Destination Account Concentration & Fraud Inflow Ranking (Top Mule Targets)
WITH DestInflow AS (
    SELECT 
        nameDest AS destination_account,
        COUNT(*) AS total_inflow_tx,
        SUM(isFraud) AS fraud_inflow_tx,
        ROUND(SUM(amount), 2) AS total_inflow_volume,
        ROUND(SUM(CASE WHEN isFraud = 1 THEN amount ELSE 0 END), 2) AS fraud_inflow_exposure
    FROM transactions
    WHERE isFraud = 1
    GROUP BY nameDest
)
SELECT 
    destination_account,
    total_inflow_tx,
    fraud_inflow_tx,
    fraud_inflow_exposure,
    ROUND(fraud_inflow_tx * 100.0 / total_inflow_tx, 2) AS fraud_tx_share_pct,
    DENSE_RANK() OVER (ORDER BY fraud_inflow_exposure DESC) AS dest_exposure_rank
FROM DestInflow
ORDER BY dest_exposure_rank
LIMIT 25;

-- 6. Hourly Time-Step Velocity & Rate Disparity Analysis
WITH HourlyRollup AS (
    SELECT 
        transaction_hour,
        COUNT(*) AS hourly_tx_count,
        SUM(isFraud) AS hourly_fraud_count,
        ROUND(SUM(amount), 2) AS hourly_total_volume,
        ROUND(SUM(CASE WHEN isFraud = 1 THEN amount ELSE 0 END), 2) AS hourly_fraud_volume
    FROM transactions
    GROUP BY transaction_hour
)
SELECT 
    transaction_hour,
    hourly_tx_count,
    hourly_fraud_count,
    ROUND(hourly_fraud_count * 100.0 / hourly_tx_count, 4) AS hourly_fraud_rate_pct,
    ROUND(hourly_fraud_volume, 2) AS hourly_fraud_volume,
    ROUND(AVG(hourly_tx_count) OVER (), 2) AS global_avg_hourly_volume,
    RANK() OVER (ORDER BY (hourly_fraud_count * 1.0 / hourly_tx_count) DESC) AS risk_hour_rank
FROM HourlyRollup
ORDER BY transaction_hour;

-- 7. Account Liquidation Behavior Breakdown across Balance Tiers
WITH BalanceTiers AS (
    SELECT 
        CASE 
            WHEN oldbalanceOrg <= 10000 THEN '1. Low ($0 - $10k)'
            WHEN oldbalanceOrg <= 100000 THEN '2. Medium ($10k - $100k)'
            WHEN oldbalanceOrg <= 1000000 THEN '3. High ($100k - $1.0M)'
            ELSE '4. Extreme (> $1.0M)'
        END AS balance_tier,
        oldbalanceOrg,
        amount,
        isFraud,
        zero_balance_origin_after_transaction
    FROM transactions
    WHERE oldbalanceOrg > 0
)
SELECT 
    balance_tier,
    COUNT(*) AS total_tx,
    SUM(isFraud) AS fraud_tx,
    SUM(zero_balance_origin_after_transaction) AS drained_tx,
    ROUND(SUM(isFraud) * 100.0 / COUNT(*), 4) AS fraud_rate_pct,
    ROUND(SUM(CASE WHEN isFraud = 1 THEN zero_balance_origin_after_transaction ELSE 0 END) * 100.0 / 
          NULLIF(SUM(isFraud), 0), 2) AS fraud_drainage_compliance_pct
FROM BalanceTiers
GROUP BY balance_tier
ORDER BY balance_tier;

-- 8. High-Risk Multi-Hop Pair Profile (Same-Amount Origin Drain and Destination Flow)
WITH SuspectDrainage AS (
    SELECT 
        step,
        type,
        amount,
        nameOrig,
        nameDest,
        oldbalanceOrg,
        newbalanceOrig,
        oldbalanceDest,
        newbalanceDest,
        isFraud,
        isFlaggedFraud
    FROM transactions
    WHERE type IN ('TRANSFER', 'CASH_OUT') 
      AND zero_balance_origin_after_transaction = 1
      AND oldbalanceDest = 0.0
)
SELECT 
    type,
    COUNT(*) AS pattern_match_count,
    SUM(isFraud) AS confirmed_fraud_count,
    ROUND(SUM(isFraud) * 100.0 / COUNT(*), 4) AS pattern_precision_pct,
    ROUND(SUM(amount), 2) AS total_pattern_volume
FROM SuspectDrainage
GROUP BY type;

-- 9. Top Fraud Exposure Origin Accounts Ranking
WITH OriginFraudExposure AS (
    SELECT 
        nameOrig AS origin_account,
        type,
        amount,
        step,
        isFlaggedFraud
    FROM transactions
    WHERE isFraud = 1
)
SELECT 
    origin_account,
    type,
    amount AS fraud_exposure_amount,
    step,
    isFlaggedFraud,
    DENSE_RANK() OVER (ORDER BY amount DESC) AS fraud_exposure_rank
FROM OriginFraudExposure
ORDER BY fraud_exposure_rank, step ASC
LIMIT 25;

-- 10. Overall SQL Performance & Summary Verification Metric
SELECT 
    COUNT(*) AS verified_total_rows,
    SUM(isFraud) AS verified_fraud_rows,
    SUM(isFlaggedFraud) AS verified_flagged_rows,
    ROUND(SUM(amount), 2) AS verified_total_volume,
    ROUND(SUM(CASE WHEN isFraud = 1 THEN amount ELSE 0 END), 2) AS verified_fraud_exposure
FROM transactions;
