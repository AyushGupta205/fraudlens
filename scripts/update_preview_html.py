"""
Update powerbi_dashboard_preview.html to include Page 8: Executive Risk Dashboard
"""

import os

preview_file = "reports/powerbi_dashboard_preview.html"

def update_preview():
    with open(preview_file, "r", encoding="utf-8") as f:
        content = f.read()

    if "8. Executive Risk Dashboard" in content:
        print("Page 8 is already present in preview HTML.")
        return

    # 1. Add tab button
    old_nav = "</nav>"
    new_nav = '  <button class="tab-btn" onclick="switchPage(\'p8\')">8. Executive Risk Dashboard (New)</button>\n</nav>'
    content = content.replace(old_nav, new_nav, 1)

    # 2. Add Page 8 container
    p8_html = """
  <!-- PAGE 8: EXECUTIVE RISK DASHBOARD -->
  <div id="p8" class="page">
    <div style="background:var(--navy); color:#fff; padding:18px 26px; border-radius:8px; margin-bottom:20px; display:flex; justify-content:space-between; align-items:center;">
      <div>
        <h2 style="font-size:24px; font-weight:700;">FraudLens</h2>
        <div style="color:#93C5FD; font-size:15px; font-weight:600; margin-top:2px;">Financial Fraud Analytics &amp; Risk Intelligence</div>
        <div style="color:#CBD5E1; font-size:12px; margin-top:3px;">PaySim Transaction Monitoring | Executive Risk Dashboard</div>
      </div>
      <div style="display:flex; gap:12px;">
        <span class="badge" style="background:#1E293B; border:1px solid #3B82F6; color:#93C5FD; padding:6px 12px; border-radius:4px; font-size:12px;">Filter | Channel: ALL</span>
        <span class="badge" style="background:#1E293B; border:1px solid #3B82F6; color:#93C5FD; padding:6px 12px; border-radius:4px; font-size:12px;">Filter | Status: ALL</span>
        <span class="badge" style="background:#1E293B; border:1px solid #3B82F6; color:#93C5FD; padding:6px 12px; border-radius:4px; font-size:12px;">Filter | Risk: ALL</span>
      </div>
    </div>

    <!-- 6 KPI Cards -->
    <div class="kpi-row">
      <div class="kpi-card">
        <div class="kpi-title">Transactions</div>
        <div class="kpi-value">6.36M</div>
        <div class="kpi-sub">6,362,620 transacted rows</div>
      </div>
      <div class="kpi-card kpi-blue">
        <div class="kpi-title">Transaction Volume</div>
        <div class="kpi-value">$1.144T</div>
        <div class="kpi-sub">$1,144,392,944,759.77</div>
      </div>
      <div class="kpi-card kpi-crimson">
        <div class="kpi-title">Fraud Transactions</div>
        <div class="kpi-value">8,213</div>
        <div class="kpi-sub">Confirmed incidents</div>
      </div>
      <div class="kpi-card kpi-crimson">
        <div class="kpi-title">Fraud Exposure</div>
        <div class="kpi-value">$12.06B</div>
        <div class="kpi-sub">$12,056,415,427.84</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-title">Fraud Rate</div>
        <div class="kpi-value">0.1291%</div>
        <div class="kpi-sub">Macro portfolio rate</div>
      </div>
      <div class="kpi-card kpi-crimson">
        <div class="kpi-title">Origin Drainage</div>
        <div class="kpi-value">97.55%</div>
        <div class="kpi-sub">8,012 / 8,213 emptied to $0.00</div>
      </div>
    </div>

    <!-- Main Visuals Grid -->
    <div class="grid-2">
      <div class="chart-card">
        <div class="chart-title">Fraud Exposure by Channel (Gross Volume vs Exposure)</div>
        <div class="chart-wrap"><canvas id="p8_chart_channels"></canvas></div>
      </div>
      <div class="chart-card">
        <div class="chart-title">Daily Fraud Exposure &amp; 7-Day Trailing Average (31 Days)</div>
        <div class="chart-wrap"><canvas id="p8_chart_daily"></canvas></div>
      </div>
    </div>

    <div class="grid-2">
      <div class="chart-card">
        <div class="chart-title">Fraud Concentration by Amount Band</div>
        <div class="chart-wrap"><canvas id="p8_chart_bands"></canvas></div>
      </div>
      <div class="chart-card">
        <div class="chart-title">Account Risk Distribution (Critical, High, Medium, Low)</div>
        <div class="chart-wrap"><canvas id="p8_chart_risk"></canvas></div>
      </div>
    </div>

    <!-- Bottom Section: Heuristic Audit + Insight Panel -->
    <div class="grid-2">
      <div class="table-card">
        <div class="chart-title">Legacy Heuristic Audit (isFlaggedFraud)</div>
        <div style="font-size:13px; font-weight:700; color:var(--crimson); margin-bottom:12px;">
          Legacy isFlaggedFraud heuristic detected 16 of 8,213 fraud-labeled transactions.
        </div>
        <table class="data-table">
          <thead>
            <tr><th>Metric Type</th><th>True Fraud</th><th>True Legitimate</th><th>Heuristic Evaluation</th></tr>
          </thead>
          <tbody>
            <tr><td><strong>Flagged as Fraud (Rule &gt; $200k)</strong></td><td style="color:var(--emerald);font-weight:700;">16 (TP)</td><td>0 (FP)</td><td>Precision: 100.00%</td></tr>
            <tr><td><strong>Not Flagged as Fraud</strong></td><td style="color:var(--crimson);font-weight:700;">8,197 (FN - Missed)</td><td>6,354,407 (TN)</td><td>Recall: 0.1948%</td></tr>
          </tbody>
        </table>
        <div class="callout-box alert" style="margin-top:14px; margin-bottom:0;">
          <strong>Key Audit Finding:</strong> The legacy heuristic missed <strong>99.81% of fraud cases</strong>. Deterministic thresholds cannot adapt to synthetic account drainage attacks.
        </div>
      </div>

      <div class="chart-card">
        <div class="chart-title">Executive Insight Panel — Validated Ground Truth</div>
        <div style="display:flex; flex-direction:column; gap:10px; font-size:13px; line-height:1.5;">
          <div><strong style="color:var(--crimson);">&bull; Fraud Exposure:</strong> <strong>$12.06B</strong> (concentrated 100% in TRANSFER &amp; CASH_OUT)</div>
          <div><strong style="color:var(--navy);">&bull; Fraud Rate:</strong> <strong>0.1291%</strong> (8,213 ground-truth incidents)</div>
          <div><strong style="color:var(--crimson);">&bull; Origin Drainage:</strong> <strong>97.55%</strong> (8,012 accounts emptied to $0.00)</div>
          <div><strong style="color:var(--blue);">&bull; Cohen's d:</strong> <strong>2.1422</strong> (Extreme statistical effect size)</div>
          <div><strong style="color:var(--blue);">&bull; Statistical Significance:</strong> <strong>p &lt; 10⁻¹⁵</strong> (Welch's t-test confirms disparate distribution)</div>
        </div>
        <div class="callout-box" style="margin-top:16px; margin-bottom:0;">
          <strong>Strategic Recommendation:</strong> Deploy supervised ML (Random Forest PR-AUC: 0.9988 / XGBoost PR-AUC: 0.9987), reducing false alerts by 87.9% while capturing 99.76% of fraud exposure.
        </div>
      </div>
    </div>
  </div>
"""

    content = content.replace("</main>", p8_html + "\n</main>", 1)

    # 3. Add JS initializers
    js_init = """
  // Page 8 charts
  new Chart(document.getElementById('p8_chart_channels'), {
    type: 'bar',
    data: {
      labels: ['TRANSFER', 'CASH_OUT', 'PAYMENT', 'CASH_IN', 'DEBIT'],
      datasets: [
        { label: 'Gross Volume ($B)', data: [485.2, 394.4, 28.0, 236.4, 0.227], backgroundColor: '#2563EB' },
        { label: 'Fraud Exposure ($B)', data: [6.07, 5.99, 0, 0, 0], backgroundColor: '#DC2626' }
      ]
    },
    options: { responsive: true, maintainAspectRatio: false }
  });

  new Chart(document.getElementById('p8_chart_daily'), {
    type: 'line',
    data: {
      labels: Array.from({length: 31}, (_, i) => 'Day ' + (i+1)),
      datasets: [
        { label: 'Daily Fraud ($M)', data: [380, 410, 390, 420, 370, 400, 450, 390, 410, 380, 430, 400, 390, 410, 420, 380, 390, 410, 430, 390, 400, 380, 410, 390, 420, 400, 390, 410, 380, 400, 420], borderColor: '#DC2626', borderWidth: 2, fill: false },
        { label: '7-Day Trailing Avg ($M)', data: [380, 395, 393, 400, 394, 395, 403, 404, 404, 403, 404, 409, 407, 401, 406, 404, 403, 404, 406, 405, 406, 405, 405, 405, 407, 405, 405, 405, 405, 405, 406], borderColor: '#0F172A', borderWidth: 3, borderDash: [5, 5], fill: false }
      ]
    },
    options: { responsive: true, maintainAspectRatio: false }
  });

  new Chart(document.getElementById('p8_chart_bands'), {
    type: 'bar',
    data: {
      labels: ['<10k', '10k-100k', '100k-500k', '500k-1M', '1M-5M', '5M+'],
      datasets: [{ label: 'Fraud Exposure ($M)', data: [0.35, 126.8, 1215.4, 2184.2, 5840.1, 2689.6], backgroundColor: '#DC2626' }]
    },
    options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false }
  });

  new Chart(document.getElementById('p8_chart_risk'), {
    type: 'doughnut',
    data: {
      labels: ['Critical (67,252)', 'High (605,922)', 'Medium (1.49M)', 'Low (4.20M)'],
      datasets: [{ data: [67252, 605922, 1493438, 4196008], backgroundColor: ['#DC2626', '#EA580C', '#F59E0B', '#10B981'] }]
    },
    options: { responsive: true, maintainAspectRatio: false }
  });
"""
    content = content.replace("};", js_init + "\n};", 1)

    with open(preview_file, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[SUCCESS] Updated {preview_file} with Page 8.")

if __name__ == "__main__":
    update_preview()
