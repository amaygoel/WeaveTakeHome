import sys
import os
import math
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from compute_metrics import load_engineer_metrics


def compute_scores(min_prs=2):
    df = load_engineer_metrics()

    # Require minimum activity to appear in rankings
    df = df[df['prs_opened'] >= min_prs].copy()

    # Log-normalize prs_merged so volume alone can't dominate,
    # letting merge_rate and cycle time meaningfully influence the ranking
    df['delivery_score'] = (
        2.0 * df['prs_merged'].apply(lambda x: math.log1p(x))
        + 3.0 * df['merge_rate']
    )

    # prs_per_week is redundant with prs_merged — velocity is pure cycle time
    df['velocity_score'] = (
        1 / (1 + df['median_merge_time_hours'].fillna(float('inf')))
    )

    df['impact_score'] = (
        0.5 * df['delivery_score']
        + 0.5 * df['velocity_score']
    ).round(2)

    return df.sort_values('impact_score', ascending=False).reset_index(drop=True)


def get_top_engineers(n=5):
    return compute_scores().head(n)


if __name__ == '__main__':
    top = get_top_engineers()
    cols = ['login', 'impact_score', 'prs_merged', 'prs_opened', 'merge_rate', 'prs_per_week', 'median_merge_time_hours']
    print(top[cols].to_string(index=False))
