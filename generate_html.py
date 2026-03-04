import sys
import os
import math
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'analysis'))
from compute_scores import get_top_engineers, compute_scores

MEDALS = ["🥇", "🥈", "🥉", "4", "5"]

def fmt_merge_time(hours):
    if hours is None or (isinstance(hours, float) and math.isnan(hours)):
        return "—"
    if hours < 24:
        return f"{hours:.1f}h"
    return f"{hours / 24:.1f}d"

def ordinal(n):
    if 11 <= n % 100 <= 13:
        return f"{n}th"
    return f"{n}{['th','st','nd','rd','th'][min(n % 10, 4)]}"

def generate():
    top5 = get_top_engineers(5)
    all_eng = compute_scores()
    total = len(all_eng)

    # Precompute ranks (1 = best)
    all_eng['rank_prs_merged']  = all_eng['prs_merged'].rank(ascending=False, method='min').astype(int)
    all_eng['rank_prs_per_week'] = all_eng['prs_per_week'].rank(ascending=False, method='min').astype(int)
    all_eng['rank_merge_rate']  = all_eng['merge_rate'].rank(ascending=False, method='min').astype(int)
    all_eng['rank_merge_time']  = all_eng['median_merge_time_hours'].rank(ascending=True, method='min', na_option='bottom').astype(int)

    ranks = all_eng.set_index('login')

    rows_html = ""
    for i, row in top5.iterrows():
        login = row['login']
        r = ranks.loc[login]

        detail_html = f"""
        <tr class="detail" id="detail-{i}">
          <td colspan="7">
            <div class="detail-inner">
            <div class="detail-grid">
              <div class="detail-row">
                <span class="detail-metric">PRs Merged</span>
                <span class="detail-value">{int(row['prs_merged'])}</span>
                <span class="detail-rank">{ordinal(r['rank_prs_merged'])} of {total} engineers</span>
              </div>
              <div class="detail-row">
                <span class="detail-metric">PRs / Week</span>
                <span class="detail-value">{row['prs_per_week']:.1f}</span>
                <span class="detail-rank">{ordinal(r['rank_prs_per_week'])} of {total} engineers</span>
              </div>
              <div class="detail-row">
                <span class="detail-metric">Merge Rate</span>
                <span class="detail-value">{row['merge_rate']:.0%}</span>
                <span class="detail-rank">{ordinal(r['rank_merge_rate'])} of {total} engineers</span>
              </div>
              <div class="detail-row">
                <span class="detail-metric">Median Merge Time</span>
                <span class="detail-value">{fmt_merge_time(row['median_merge_time_hours'])}</span>
                <span class="detail-rank">{ordinal(r['rank_merge_time'])} of {total} engineers</span>
              </div>
            </div>
            </div>
          </div></td>
        </tr>"""

        rows_html += f"""
        <tr class="main-row" onclick="toggle({i})">
            <td class="medal">{MEDALS[i]}</td>
            <td class="name">{login} <span class="chevron" id="chevron-{i}">›</span></td>
            <td class="score">{row['impact_score']:.1f}</td>
            <td>{int(row['prs_merged'])}</td>
            <td>{row['prs_per_week']:.1f}</td>
            <td>{row['merge_rate']:.0%}</td>
            <td>{fmt_merge_time(row['median_merge_time_hours'])}</td>
        </tr>
        {detail_html}"""

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

    tbody tr.main-row {{
      border-bottom: 1px solid #f0f0f0;
      cursor: pointer;
      transition: background 0.15s;
    }}

    tbody tr.main-row:hover {{ background: #fafafa; }}

    tbody tr.main-row.open {{ border-bottom: none; }}

    tbody td {{
      padding: 13px 12px;
      vertical-align: middle;
    }}

    tbody td:first-child {{ padding-left: 0; }}

    .medal {{ font-size: 1.1rem; width: 32px; }}

    .name {{ font-weight: 600; color: #111; }}

    .chevron {{
      display: inline-block;
      color: #bbb;
      font-size: 1rem;
      margin-left: 6px;
      transition: transform 0.2s;
    }}

    .chevron.open {{ transform: rotate(90deg); color: #888; }}

    .score {{ font-weight: 700; color: #e3500a; }}

    /* Detail row — always in DOM, animates via max-height */
    .detail {{ background: #fafafa; border-bottom: 1px solid #f0f0f0; }}

    .detail > td {{ padding: 0; }}

    .detail-inner {{
      max-height: 0;
      overflow: hidden;
      transition: max-height 0.3s ease, padding 0.3s ease;
      padding: 0 12px 0 44px;
    }}

    .detail.open .detail-inner {{
      max-height: 200px;
      padding: 12px 12px 16px 44px;
    }}

    .detail-grid {{ display: flex; flex-direction: column; gap: 6px; }}

    .detail-row {{
      display: flex;
      align-items: center;
      gap: 16px;
      font-size: 0.82rem;
    }}

    .detail-metric {{ color: #888; width: 160px; flex-shrink: 0; }}
    .detail-value {{ font-weight: 600; width: 60px; }}
    .detail-rank {{ color: #aaa; }}
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
  <script>
    function toggle(i) {{
      const detail  = document.getElementById('detail-' + i);
      const chevron = document.getElementById('chevron-' + i);
      const mainRow = detail.previousElementSibling;
      const isOpen  = detail.classList.contains('open');
      detail.classList.toggle('open', !isOpen);
      chevron.classList.toggle('open', !isOpen);
      mainRow.classList.toggle('open', !isOpen);
    }}
  </script>
</body>
</html>"""

    out_path = os.path.join(os.path.dirname(__file__), 'public', 'index.html')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f:
        f.write(html)

    print(f"Generated: {out_path}")

if __name__ == '__main__':
    generate()
