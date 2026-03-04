import os
import requests
from datetime import datetime, timezone
from db import get_connection

CUTOFF = datetime(2025, 12, 1, tzinfo=timezone.utc)
HEADERS = {
    'Authorization': f'token {os.environ["GITHUB_TOKEN"]}',
    'Accept': 'application/vnd.github.v3+json',
}


def upsert_user(cur, user):
    cur.execute(
        'INSERT OR IGNORE INTO users (user_id, login, type, is_bot) VALUES (?, ?, ?, ?)',
        (user['id'], user['login'], user['type'], user['type'] == 'Bot'),
    )


def fetch_prs():
    conn = get_connection()
    cur = conn.cursor()

    page = 1
    total = 0

    while True:
        resp = requests.get(
            'https://api.github.com/repos/PostHog/posthog/pulls',
            headers=HEADERS,
            params={'state': 'all', 'per_page': 100, 'sort': 'created', 'direction': 'desc', 'page': page},
        )
        resp.raise_for_status()
        prs = resp.json()

        if not prs:
            break

        stop = False
        for pr in prs:
            created = datetime.fromisoformat(pr['created_at'].replace('Z', '+00:00'))

            if created < CUTOFF:
                stop = True
                break

            user = pr['user']
            upsert_user(cur, user)

            cur.execute(
                '''INSERT OR REPLACE INTO pull_requests
                   (pr_id, pr_number, author_user_id, created_at, merged_at, closed_at, state, is_merged)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    pr['id'], pr['number'], user['id'],
                    pr['created_at'], pr.get('merged_at'), pr.get('closed_at'),
                    pr['state'], pr.get('merged_at') is not None,
                ),
            )
            total += 1

        conn.commit()
        print(f'  Page {page}: {total} PRs stored so far')

        if stop or len(prs) < 100:
            break

        page += 1

    conn.close()
    print(f'Done. Total PRs stored: {total}')
