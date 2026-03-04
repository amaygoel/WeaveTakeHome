import sys
import os
import math
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'analysis'))
from compute_scores import get_top_engineers

MEDALS = ["🥇", "🥈", "🥉", "4", "5"]

def fmt_merge_time(hours):
    if hours is None or (isinstance(hours, float) and math.isnan(hours)):
        return "—"
    if hours < 24:
        return f"{hours:.1f}h"
    return f"{hours / 24:.1f}d"

def generate():
    top5 = get_top_engineers(5)

    rows_html = ""
    for i, row in top5.iterrows():
        rows_html += f"""
        <tr>
            <td class="medal">{MEDALS[i]}</td>
            <td class="name">{row['login']}</td>
            <td class="score">{row['impact_score']:.1f}</td>
            <td>{int(row['prs_merged'])}</td>
            <td>{row['prs_per_week']:.1f}</td>
            <td>{row['merge_rate']:.0%}</td>
            <td>{fmt_merge_time(row['median_merge_time_hours'])}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>PostHog Engineer Impact</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #f9f9f9;
      color: #111;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      padding: 32px 16px;
    }}

    .card {{
      background: #fff;
      border-radius: 12px;
      box-shadow: 0 2px 16px rgba(0,0,0,0.08);
      padding: 36px 40px;
      width: 100%;
      max-width: 860px;
    }}

    h1 {{
      font-size: 1.3rem;
      font-weight: 700;
      margin-bottom: 4px;
    }}

    .subtitle {{
      font-size: 0.82rem;
      color: #888;
      margin-bottom: 28px;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.9rem;
    }}

    thead th {{
      text-align: left;
      font-size: 0.75rem;
      font-weight: 600;
      color: #888;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      padding: 0 12px 10px 12px;
      border-bottom: 1px solid #eee;
    }}

    thead th:first-child {{ padding-left: 0; }}

    tbody tr {{
      border-bottom: 1px solid #f0f0f0;
    }}

    tbody tr:last-child {{
      border-bottom: none;
    }}

    tbody td {{
      padding: 13px 12px;
      vertical-align: middle;
    }}

    tbody td:first-child {{ padding-left: 0; }}

    .medal {{
      font-size: 1.1rem;
      width: 32px;
    }}

    .name {{
      font-weight: 600;
      color: #111;
    }}

    .score {{
      font-weight: 700;
      color: #e3500a;
    }}
  </style>
</head>
<body>
  <div class="card">
    <h1>Top 5 Most Impactful Engineers — PostHog</h1>
    <p class="subtitle">Data from Dec 1 2025 to Present</p>
    <table>
      <thead>
        <tr>
          <th></th>
          <th>Engineer</th>
          <th>Impact Score</th>
          <th>PRs Merged</th>
          <th>PRs / Week</th>
          <th>Merge Rate</th>
          <th>Median Merge Time</th>
        </tr>
      </thead>
      <tbody>
        {rows_html}
      </tbody>
    </table>
  </div>
</body>
</html>"""

    out_path = os.path.join(os.path.dirname(__file__), 'public', 'index.html')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f:
        f.write(html)

    print(f"Generated: {out_path}")

if __name__ == '__main__':
    generate()
