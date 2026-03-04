import sys
import os
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ingestion'))
from db import get_connection

WEEKS_IN_WINDOW = 12.857  # 90 days

BOT_LOGINS = {'dependabot', 'github-actions', 'renovate', 'snyk-bot', 'posthog-bot'}


def load_engineer_metrics():
    conn = get_connection()

    df = pd.read_sql_query('''
        SELECT
            u.login,
            pr.is_merged,
            pr.created_at,
            pr.merged_at
        FROM pull_requests pr
        JOIN users u ON pr.author_user_id = u.user_id
        WHERE u.is_bot = 0
    ''', conn)
    conn.close()

    # Filter known bots by login pattern
    df = df[~df['login'].isin(BOT_LOGINS)]
    df = df[~df['login'].str.contains(r'\[bot\]|bot$', case=False, regex=True, na=False)]

    df['created_at'] = pd.to_datetime(df['created_at'], utc=True)
    df['merged_at'] = pd.to_datetime(df['merged_at'], utc=True)
    df['merge_time_hours'] = (df['merged_at'] - df['created_at']).dt.total_seconds() / 3600

    rows = []
    for login, group in df.groupby('login'):
        merged = group[group['is_merged'] == 1]
        prs_opened = len(group)
        prs_merged = len(merged)

        rows.append({
            'login': login,
            'prs_opened': prs_opened,
            'prs_merged': prs_merged,
            'prs_closed_unmerged': prs_opened - prs_merged,
            'merge_rate': (prs_merged + 1) / (prs_opened + 2),
            'prs_per_week': prs_merged / WEEKS_IN_WINDOW,
            'median_merge_time_hours': merged['merge_time_hours'].median() if prs_merged > 0 else None,
            'first_pr_date': group['created_at'].min(),
            'last_pr_date': group['created_at'].max(),
        })

    return pd.DataFrame(rows)
