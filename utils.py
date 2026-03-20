import re
import pandas as pd

def map_quality(val):
    s = str(val).lower()
    if any(x in s for x in ['appr', 'pass']): return 'Approved'
    if any(x in s for x in ['rew', 'repro']): return 'Rework'
    if any(x in s for x in ['can', 'rej']): return 'Cancelled'
    return 'Others'

def map_portal(val):
    s = str(val).lower()
    if 'live' in s: return 'Live'
    if 'com' in s: return 'Committed'
    if any(x in s for x in ['can', 'rej']): return 'Cancelled'
    return 'Others'

def format_with_pct(val_df, total_series):
    display_df = val_df.copy()
    for col in val_df.columns:
        pcts = (val_df[col] / total_series * 100).fillna(0)
        display_df[col] = [
            f"{int(v):,} ({p:.1f}%)" if v > 0 else "-" 
            for v, p in zip(val_df[col], pcts)
        ]
    return display_df

def calculate_standardized_revenue(val):
    s = str(val).lower()
    match = re.search(r'£?\s*(\d+(?:\.\d+)?)', s)
    if match:
        amount = float(match.group(1))
        if 'inc' not in s: 
            amount = amount * 1.20
        return amount
    return 0.0
