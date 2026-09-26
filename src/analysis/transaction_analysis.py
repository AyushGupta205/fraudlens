import pandas as pd
import numpy as np
from typing import Dict, Any

def get_transaction_statistics(df: pd.DataFrame) -> Dict[str, Any]:
    stats = {}
    for segment, subset in [('all', df), ('fraud', df[df['isFraud'] == 1]), ('legit', df[df['isFraud'] == 0])]:
        if len(subset) == 0:
            continue
        amt = subset['amount']
        stats[segment] = {
            'count': int(len(subset)),
            'mean': round(float(amt.mean()), 2),
            'std': round(float(amt.std()), 2),
            'median': round(float(amt.median()), 2),
            'min': round(float(amt.min()), 2),
            'max': round(float(amt.max()), 2),
            'p25': round(float(amt.quantile(0.25)), 2),
            'p75': round(float(amt.quantile(0.75)), 2),
            'p90': round(float(amt.quantile(0.90)), 2),
            'p99': round(float(amt.quantile(0.99)), 2),
            'skewness': round(float(amt.skew()), 4),
            'kurtosis': round(float(amt.kurt()), 4)
        }
    return stats
