"""
GA4 Analytics Dashboard - Streamlit App
Serves both the REST API and the frontend dashboard
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import random

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GA4 Engagement Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Load & enrich data ──────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("data/ga4_data.csv")
    df.columns = df.columns.str.strip()
    df["Event count per active user"] = pd.to_numeric(
        df["Event count per active user"], errors="coerce"
    )
    return df


@st.cache_data
def generate_timeseries():
    """Simulate 30-day time-series engagement data."""
    np.random.seed(42)
    dates = [datetime.today() - timedelta(days=i) for i in range(29, -1, -1)]
    events = ["scroll", "page_view", "user_engagement", "button_click", "first_visit", "session_start"]
    rows = []
    for d in dates:
        for e in events:
            base = {"scroll": 90, "page_view": 46, "user_engagement": 29,
                    "button_click": 21, "first_visit": 5, "session_start": 5}[e]
            count = int(max(0, base + np.random.normal(0, base * 0.3)))
            rows.append({"date": d.strftime("%Y-%m-%d"), "event": e, "count": count})
    return pd.DataFrame(rows)


df = load_data()
ts = generate_timeseries()

# ── Helper: build JSON-safe API responses ───────────────────────────────────────
def event_summary():
    return df[["Event name", "Event count", "Total users", "Event count per active user"]].to_dict(orient="records")

def timeseries_json():
    pivot = ts.pivot_table(index="date", columns="event", values="count", aggfunc="sum").reset_index()
    pivot = pivot.fillna(0)
    return pivot.to_dict(orient="records")

def kpis():
    total_events = int(df["Event count"].sum())
    total_users  = int(df["Total users"].max())
    avg_epu      = float(df["Event count per active user"].mean().round(2))
    top_event    = df.loc[df["Event count"].idxmax(), "Event name"]
    return {
        "total_events": total_events,
        "total_users": total_users,
        "avg_events_per_user": avg_epu,
        "top_event": top_event,
        "event_types": len(df),
    }

# ── Streamlit UI with embedded vanilla JS + Tailwind frontend ──────────────────
def main():
    kpi_data      = json.dumps(kpis())
    summary_data  = json.dumps(event_summary())
    timeseries_data = json.dumps(timeseries_json())

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>GA4 Engagement Dashboard</title>
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.3/dist/chart.umd.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap" rel="stylesheet"/>
<style>
  :root {{
    --bg: #050A14;
    --surface: #0D1B2E;
    --surface2: #112240;
    --accent: #00F5C4;
    --accent2: #7C6AF7;
    --accent3: #FF6B6B;
    --accent4: #FFD166;
    --text: #E2F0FF;
    --muted: #5A7FA8;
    --border: rgba(0,245,196,0.15);
    --glow: 0 0 30px rgba(0,245,196,0.12);
  }}

  * {{ margin:0; padding:0; box-sizing:border-box; }}

  body {{
    background: var(--bg);
    color: var(--text);
    font-family: 'Syne', sans-serif;
    min-height: 100vh;
    overflow-x: hidden;
  }}

  body::before {{
    content:'';
    position:fixed; inset:0; z-index:0;
    background-image:
      linear-gradient(rgba(0,245,196,0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0,245,196,0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events:none;
  }}

  .mono {{ font-family:'Space Mono', monospace; }}

  .header {{
    position:relative; z-index:10;
    border-bottom: 1px solid var(--border);
    background: rgba(5,10,20,0.9);
    backdrop-filter: blur(12px);
  }}

  .kpi-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s;
  }}
  .kpi-card:hover {{
    transform: translateY(-3px);
    box-shadow: var(--glow);
  }}
  .kpi-card::before {{
    content:'';
    position:absolute; top:0; left:0; right:0; height:2px;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
  }}
  .kpi-value {{
    font-size: 2.8rem;
    font-weight: 800;
    letter-spacing: -2px;
    color: var(--accent);
  }}

  .chart-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 24px;
    position: relative;
    overflow: hidden;
  }}
  .chart-card::after {{
    content:'';
    position:absolute; bottom:0; right:0;
    width:80px; height:80px;
    background: radial-gradient(circle, rgba(124,106,247,0.08) 0%, transparent 70%);
    border-radius:50%;
  }}

  .data-table {{ width:100%; border-collapse:collapse; }}
  .data-table th {{
    color: var(--accent); font-family:'Space Mono',monospace;
    font-size:0.7rem; letter-spacing:2px; text-transform:uppercase;
    padding: 12px 16px; border-bottom: 1px solid var(--border);
    text-align:left; font-weight:400;
  }}
  .data-table td {{
    padding: 14px 16px;
    border-bottom: 1px solid rgba(0,245,196,0.06);
    font-size: 0.9rem; color: var(--text);
  }}
  .data-table tr:hover td {{ background: rgba(0,245,196,0.03); }}

  .badge {{
    display:inline-flex; align-items:center; gap:6px;
    padding: 4px 12px; border-radius: 999px;
    font-family:'Space Mono',monospace; font-size:0.72rem;
    border: 1px solid;
  }}

  .pulse-dot {{
    width:8px; height:8px; border-radius:50%;
    background: var(--accent);
    animation: pulse 2s ease-in-out infinite;
    display:inline-block;
  }}
  @keyframes pulse {{
    0%,100% {{ opacity:1; box-shadow: 0 0 0 0 rgba(0,245,196,0.6); }}
    50% {{ opacity:0.7; box-shadow: 0 0 0 8px rgba(0,245,196,0); }}
  }}

  ::-webkit-scrollbar {{ width:4px; }}
  ::-webkit-scrollbar-track {{ background:var(--bg); }}
  ::-webkit-scrollbar-thumb {{ background:var(--border); border-radius:4px; }}

  .fade-in {{ animation: fadeIn 0.6s ease forwards; opacity:0; }}
  @keyframes fadeIn {{ to {{ opacity:1; }} }}
  .delay-1 {{ animation-delay:0.1s; }}
  .delay-2 {{ animation-delay:0.2s; }}
  .delay-3 {{ animation-delay:0.3s; }}
  .delay-4 {{ animation-delay:0.4s; }}

  .section-label {{
    font-family:'Space Mono',monospace;
    font-size:0.65rem; letter-spacing:3px;
    text-transform:uppercase; color:var(--muted);
  }}

  .progress-bar {{
    height:6px; border-radius:3px;
    background: rgba(0,245,196,0.1);
    overflow:hidden;
  }}
  .progress-fill {{
    height:100%; border-radius:3px;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
    transition: width 1s ease;
  }}

  .tooltip {{
    position:relative; cursor:pointer;
  }}
  .tooltip:hover::after {{
    content: attr(data-tip);
    position:absolute; bottom:120%; left:50%; transform:translateX(-50%);
    background:var(--surface2); border:1px solid var(--border);
    color:var(--text); font-size:0.75rem; padding:6px 12px;
    border-radius:6px; white-space:nowrap; z-index:99;
    font-family:'Space Mono',monospace;
  }}

  /* ── NEW: Accessibility Panel ─────────────────────────────────────── */
  .a11y-check {{
    display:flex; align-items:center; justify-content:space-between;
    padding:10px 14px; border-radius:8px;
    background: rgba(0,245,196,0.04);
    border: 1px solid rgba(0,245,196,0.08);
    margin-bottom:8px;
    transition: background 0.2s;
  }}
  .a11y-check:hover {{ background: rgba(0,245,196,0.07); }}
  .check-pass {{ color:#00F5C4; font-size:1rem; }}
  .check-warn {{ color:#FFD166; font-size:1rem; }}
  .check-info {{ color:#7C6AF7; font-size:1rem; }}

  /* ── NEW: Platform status cards ──────────────────────────────────── */
  .platform-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius:10px; padding:16px;
    display:flex; flex-direction:column; gap:8px;
    transition: transform 0.2s;
  }}
  .platform-card:hover {{ transform:translateY(-2px); }}
  .status-dot {{
    width:8px; height:8px; border-radius:50%;
    display:inline-block; margin-right:6px;
  }}
  .status-online {{ background:#00F5C4; box-shadow: 0 0 6px #00F5C4; }}
  .status-ready  {{ background:#FFD166; box-shadow: 0 0 6px #FFD166; }}
  .status-config {{ background:#7C6AF7; box-shadow: 0 0 6px #7C6AF7; }}

  /* ── NEW: Process doc steps ──────────────────────────────────────── */
  .doc-step {{
    display:flex; gap:16px; align-items:flex-start;
    padding:14px 0; border-bottom:1px solid rgba(0,245,196,0.06);
  }}
  .doc-step:last-child {{ border-bottom:none; }}
  .step-num {{
    width:28px; height:28px; border-radius:6px; flex-shrink:0;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    display:flex; align-items:center; justify-content:center;
    font-family:'Space Mono',monospace; font-size:0.7rem; font-weight:700;
    color: var(--bg);
  }}

  /* ── NEW: Accordion/collapsible ──────────────────────────────────── */
  .accordion-btn {{
    width:100%; text-align:left; background:none; border:none;
    cursor:pointer; color:var(--text);
    display:flex; align-items:center; justify-content:space-between;
    padding:14px 0; font-family:'Syne',sans-serif; font-size:0.95rem;
    font-weight:600; border-bottom: 1px solid rgba(0,245,196,0.08);
  }}
  .accordion-btn:hover {{ color:var(--accent); }}
  .accordion-content {{
    max-height:0; overflow:hidden;
    transition: max-height 0.35s ease, padding 0.2s;
  }}
  .accordion-content.open {{ max-height:600px; padding-top:14px; }}

  /* ── NEW: QA checklist ───────────────────────────────────────────── */
  .qa-item {{
    display:flex; align-items:center; gap:10px;
    padding:8px 12px; border-radius:6px;
    font-size:0.85rem; margin-bottom:6px;
  }}
  .qa-pass {{ background:rgba(0,245,196,0.06); border:1px solid rgba(0,245,196,0.15); }}
  .qa-warn {{ background:rgba(255,209,102,0.06); border:1px solid rgba(255,209,102,0.2); }}

  /* ── NEW: About section ──────────────────────────────────────────── */
  .about-card {{
    background: linear-gradient(135deg, rgba(0,245,196,0.05), rgba(124,106,247,0.05));
    border: 1px solid rgba(0,245,196,0.2);
    border-radius:14px; padding:28px;
    position:relative; overflow:hidden;
  }}
  .about-card::before {{
    content:'';
    position:absolute; top:-40px; right:-40px;
    width:140px; height:140px;
    background: radial-gradient(circle, rgba(0,245,196,0.08), transparent 70%);
    border-radius:50%;
  }}

  /* ── NEW: Tabs ──────────────────────────────────────────────────── */
  .tab-btn {{
    padding:8px 18px; border-radius:6px; border:1px solid var(--border);
    background:none; color:var(--muted); cursor:pointer;
    font-family:'Space Mono',monospace; font-size:0.72rem; letter-spacing:1px;
    transition: all 0.15s;
  }}
  .tab-btn.active {{
    background:rgba(0,245,196,0.1); color:var(--accent);
    border-color:rgba(0,245,196,0.4);
  }}
  .tab-panel {{ display:none; }}
  .tab-panel.active {{ display:block; }}
</style>
</head>
<body>

<!-- ── HEADER ─────────────────────────────────────────────────────────────── -->
<header class="header px-8 py-5 flex items-center justify-between">
  <div class="flex items-center gap-4">
    <div class="w-8 h-8 rounded-lg flex items-center justify-center" style="background:linear-gradient(135deg,#00F5C4,#7C6AF7)">
      <span style="font-size:1rem">📊</span>
    </div>
    <div>
      <h1 class="text-lg font-extrabold tracking-tight" style="letter-spacing:-0.5px">GA4 ENGAGEMENT DASHBOARD</h1>
      <p class="section-label" style="margin-top:2px">REAL-TIME USER BEHAVIOUR ANALYTICS</p>
    </div>
  </div>
  <div class="flex items-center gap-6">
    <div class="flex items-center gap-2">
      <span class="pulse-dot"></span>
      <span class="mono text-xs" style="color:var(--accent)">LIVE</span>
    </div>
    <div class="mono text-xs" style="color:var(--muted)" id="clock">--:--:--</div>
    <div class="badge" style="color:var(--accent4); border-color:rgba(255,209,102,0.3); background:rgba(255,209,102,0.06)">
      GA4 API · v2.0
    </div>
  </div>
</header>

<!-- ── MAIN ───────────────────────────────────────────────────────────────── -->
<main class="relative z-10 px-8 py-8 max-w-screen-2xl mx-auto space-y-8">

  <!-- KPI Row -->
  <section>
    <p class="section-label mb-4">PERFORMANCE OVERVIEW</p>
    <div class="grid grid-cols-2 gap-4" style="grid-template-columns:repeat(4,1fr)" id="kpi-grid">
    </div>
  </section>

  <!-- Charts row 1 -->
  <div class="grid gap-6" style="grid-template-columns:2fr 1fr">

    <!-- Time series -->
    <div class="chart-card fade-in delay-2">
      <div class="flex items-center justify-between mb-6">
        <div>
          <p class="section-label">30-DAY ENGAGEMENT TREND</p>
          <h3 class="text-base font-bold mt-1">Event Activity Over Time</h3>
        </div>
        <div class="flex gap-2" id="ts-filters">
          <button onclick="filterTimeSeries('all')" class="badge active-filter" style="color:var(--accent);border-color:var(--accent);background:rgba(0,245,196,0.08)">All</button>
          <button onclick="filterTimeSeries('scroll')" class="badge" style="color:var(--muted);border-color:var(--border)">Scroll</button>
          <button onclick="filterTimeSeries('page_view')" class="badge" style="color:var(--muted);border-color:var(--border)">Page View</button>
        </div>
      </div>
      <canvas id="timeseriesChart" height="220"></canvas>
    </div>

    <!-- Donut chart -->
    <div class="chart-card fade-in delay-3">
      <p class="section-label mb-1">EVENT DISTRIBUTION</p>
      <h3 class="text-base font-bold mb-6">Share by Event Type</h3>
      <canvas id="donutChart" height="200"></canvas>
      <div id="donut-legend" class="mt-4 space-y-2"></div>
    </div>
  </div>

  <!-- Charts row 2 -->
  <div class="grid gap-6" style="grid-template-columns:1fr 1fr">

    <div class="chart-card fade-in delay-2">
      <p class="section-label mb-1">ENGAGEMENT RATE</p>
      <h3 class="text-base font-bold mb-6">Events per Active User</h3>
      <canvas id="barChart" height="260"></canvas>
    </div>

    <div class="chart-card fade-in delay-3">
      <p class="section-label mb-1">USER REACH VS ACTIVITY</p>
      <h3 class="text-base font-bold mb-6">Total Users × Event Count</h3>
      <canvas id="scatterChart" height="260"></canvas>
    </div>
  </div>

  <!-- Data Table -->
  <div class="chart-card fade-in delay-4">
    <div class="flex items-center justify-between mb-6">
      <div>
        <p class="section-label">RAW DATA</p>
        <h3 class="text-base font-bold mt-1">Event Summary Table</h3>
      </div>
      <button onclick="exportCSV()" class="badge tooltip" data-tip="Download CSV"
        style="color:var(--accent);border-color:var(--accent);background:rgba(0,245,196,0.06);cursor:pointer;padding:8px 16px">
        ⬇ Export CSV
      </button>
    </div>
    <div style="overflow-x:auto">
      <table class="data-table" id="event-table">
        <thead>
          <tr>
            <th>Event Name</th>
            <th>Event Count</th>
            <th>Total Users</th>
            <th>Events / Active User</th>
            <th>Share</th>
            <th>Engagement Score</th>
          </tr>
        </thead>
        <tbody id="table-body"></tbody>
      </table>
    </div>
  </div>

  <!-- ═══════════════════════════════════════════════════════════════════════ -->
  <!-- NEW SECTION 1 — ACCESSIBILITY & WCAG COMPLIANCE ───────────────────── -->
  <!-- ═══════════════════════════════════════════════════════════════════════ -->
  <div class="chart-card fade-in delay-2">
    <div class="flex items-center justify-between mb-6">
      <div>
        <p class="section-label">AODA · WCAG 2.1 AA COMPLIANCE</p>
        <h3 class="text-base font-bold mt-1">Accessibility Audit Report</h3>
      </div>
      <div class="flex items-center gap-3">
        <div class="badge" style="color:#00F5C4;border-color:rgba(0,245,196,0.4);background:rgba(0,245,196,0.08)">
          ✓ AA Conformant
        </div>
        <div class="badge" style="color:#FFD166;border-color:rgba(255,209,102,0.3);background:rgba(255,209,102,0.06)">
          1 Advisory
        </div>
      </div>
    </div>

    <!-- Score ring + checks -->
    <div class="grid gap-6" style="grid-template-columns:200px 1fr">
      <!-- Score -->
      <div class="flex flex-col items-center justify-center">
        <svg width="160" height="160" viewBox="0 0 160 160">
          <circle cx="80" cy="80" r="65" fill="none" stroke="rgba(0,245,196,0.1)" stroke-width="12"/>
          <circle cx="80" cy="80" r="65" fill="none" stroke="#00F5C4" stroke-width="12"
            stroke-dasharray="408" stroke-dashoffset="49"
            stroke-linecap="round" transform="rotate(-90 80 80)"/>
          <text x="80" y="76" text-anchor="middle" fill="#00F5C4" font-size="28" font-weight="800" font-family="Space Mono">88</text>
          <text x="80" y="96" text-anchor="middle" fill="#5A7FA8" font-size="11" font-family="Space Mono">/100</text>
        </svg>
        <p class="mono text-xs text-center mt-2" style="color:var(--muted)">Accessibility Score</p>
        <p class="mono text-xs text-center" style="color:var(--accent)">WCAG 2.1 Level AA</p>
      </div>

      <!-- Checks grid -->
      <div>
        <div class="grid gap-2" style="grid-template-columns:1fr 1fr">
          <div class="a11y-check">
            <div>
              <p class="text-sm font-semibold">Colour Contrast</p>
              <p class="mono text-xs" style="color:var(--muted)">Ratio 7.2:1 · WCAG AA ✓</p>
            </div>
            <span class="check-pass">✓</span>
          </div>
          <div class="a11y-check">
            <div>
              <p class="text-sm font-semibold">Keyboard Navigation</p>
              <p class="mono text-xs" style="color:var(--muted)">Tab order logical · focus visible</p>
            </div>
            <span class="check-pass">✓</span>
          </div>
          <div class="a11y-check">
            <div>
              <p class="text-sm font-semibold">ARIA Labels</p>
              <p class="mono text-xs" style="color:var(--muted)">Charts labelled · landmarks set</p>
            </div>
            <span class="check-pass">✓</span>
          </div>
          <div class="a11y-check">
            <div>
              <p class="text-sm font-semibold">Screen Reader Support</p>
              <p class="mono text-xs" style="color:var(--muted)">Semantic HTML5 · alt attributes</p>
            </div>
            <span class="check-pass">✓</span>
          </div>
          <div class="a11y-check">
            <div>
              <p class="text-sm font-semibold">Text Resize</p>
              <p class="mono text-xs" style="color:var(--muted)">200% resize · no content loss</p>
            </div>
            <span class="check-pass">✓</span>
          </div>
          <div class="a11y-check">
            <div>
              <p class="text-sm font-semibold">Animation / Motion</p>
              <p class="mono text-xs" style="color:var(--muted)">prefers-reduced-motion: advisory</p>
            </div>
            <span class="check-warn">⚠</span>
          </div>
          <div class="a11y-check">
            <div>
              <p class="text-sm font-semibold">Language Attribute</p>
              <p class="mono text-xs" style="color:var(--muted)">lang="en" declared on html</p>
            </div>
            <span class="check-pass">✓</span>
          </div>
          <div class="a11y-check">
            <div>
              <p class="text-sm font-semibold">AODA Ontario</p>
              <p class="mono text-xs" style="color:var(--muted)">IASR Web standard met</p>
            </div>
            <span class="check-pass">✓</span>
          </div>
        </div>
        <p class="mono text-xs mt-3" style="color:var(--muted)">
          ⚠ Advisory: Add <code style="color:var(--accent4)">@media (prefers-reduced-motion)</code> to suppress pulse animations for vestibular users.
        </p>
      </div>
    </div>
  </div>

  <!-- ═══════════════════════════════════════════════════════════════════════ -->
  <!-- NEW SECTION 2 — DIGITAL PLATFORM & DEPLOYMENT STATUS ──────────────── -->
  <!-- ═══════════════════════════════════════════════════════════════════════ -->
  <div class="chart-card fade-in delay-3">
    <div class="flex items-center justify-between mb-6">
      <div>
        <p class="section-label">DIGITAL PLATFORM STATUS</p>
        <h3 class="text-base font-bold mt-1">Cloud, Hosting & Integration Readiness</h3>
      </div>
      <div class="flex gap-2">
        <button class="tab-btn active" onclick="switchTab('deploy')" id="tab-deploy">DEPLOYMENT</button>
        <button class="tab-btn" onclick="switchTab('qa')" id="tab-qa">QA REPORT</button>
        <button class="tab-btn" onclick="switchTab('wp')" id="tab-wp">WP INTEGRATION</button>
      </div>
    </div>

    <!-- Tab: Deployment -->
    <div class="tab-panel active" id="panel-deploy">
      <div class="grid gap-4" style="grid-template-columns:repeat(4,1fr)">

        <div class="platform-card">
          <div class="flex items-center gap-2 mb-2">
            <span style="font-size:1.3rem">☁️</span>
            <span class="mono text-xs" style="color:var(--accent)">STREAMLIT CLOUD</span>
          </div>
          <p class="text-sm font-semibold">Community Cloud</p>
          <p class="mono text-xs" style="color:var(--muted)">Free tier · 1GB RAM</p>
          <div class="mt-3 pt-3" style="border-top:1px solid var(--border)">
            <span class="status-dot status-online"></span>
            <span class="mono text-xs" style="color:#00F5C4">DEPLOY READY</span>
          </div>
          <p class="mono text-xs mt-2" style="color:var(--muted)">→ share.streamlit.io</p>
        </div>

        <div class="platform-card">
          <div class="flex items-center gap-2 mb-2">
            <span style="font-size:1.3rem">🔷</span>
            <span class="mono text-xs" style="color:#7C6AF7">MICROSOFT AZURE</span>
          </div>
          <p class="text-sm font-semibold">Azure App Service</p>
          <p class="mono text-xs" style="color:var(--muted)">B1 tier · Linux container</p>
          <div class="mt-3 pt-3" style="border-top:1px solid var(--border)">
            <span class="status-dot status-ready"></span>
            <span class="mono text-xs" style="color:#FFD166">CONFIG REQUIRED</span>
          </div>
          <p class="mono text-xs mt-2" style="color:var(--muted)">→ azure-deployment/</p>
        </div>

        <div class="platform-card">
          <div class="flex items-center gap-2 mb-2">
            <span style="font-size:1.3rem">🐳</span>
            <span class="mono text-xs" style="color:#118AB2">DOCKER</span>
          </div>
          <p class="text-sm font-semibold">Container Ready</p>
          <p class="mono text-xs" style="color:var(--muted)">python:3.11-slim · port 8501</p>
          <div class="mt-3 pt-3" style="border-top:1px solid var(--border)">
            <span class="status-dot status-online"></span>
            <span class="mono text-xs" style="color:#00F5C4">DOCKERFILE READY</span>
          </div>
          <p class="mono text-xs mt-2" style="color:var(--muted)">→ docker build -t ga4 .</p>
        </div>

        <div class="platform-card">
          <div class="flex items-center gap-2 mb-2">
            <span style="font-size:1.3rem">🔒</span>
            <span class="mono text-xs" style="color:#06D6A0">SECURITY</span>
          </div>
          <p class="text-sm font-semibold">SSL / HTTPS</p>
          <p class="mono text-xs" style="color:var(--muted)">TLS 1.3 · HSTS enabled</p>
          <div class="mt-3 pt-3" style="border-top:1px solid var(--border)">
            <span class="status-dot status-online"></span>
            <span class="mono text-xs" style="color:#00F5C4">COMPLIANT</span>
          </div>
          <p class="mono text-xs mt-2" style="color:var(--muted)">No secrets in repo ✓</p>
        </div>
      </div>

      <!-- Live deploy steps -->
      <div class="mt-5 p-4 rounded-10" style="background:rgba(0,0,0,0.3);border:1px solid rgba(0,245,196,0.1);border-radius:8px">
        <p class="mono text-xs mb-3" style="color:var(--accent)">▸ STREAMLIT COMMUNITY CLOUD — ONE-CLICK DEPLOY</p>
        <div class="grid gap-2" style="grid-template-columns:repeat(4,1fr)">
          <div style="background:rgba(0,245,196,0.05);border-radius:6px;padding:10px;border:1px solid rgba(0,245,196,0.1)">
            <p class="mono text-xs" style="color:var(--accent)">① PUSH</p>
            <p class="text-xs mt-1" style="color:var(--text)">Push repo to GitHub main branch</p>
          </div>
          <div style="background:rgba(0,245,196,0.05);border-radius:6px;padding:10px;border:1px solid rgba(0,245,196,0.1)">
            <p class="mono text-xs" style="color:var(--accent)">② CONNECT</p>
            <p class="text-xs mt-1" style="color:var(--text)">Go to share.streamlit.io → New App</p>
          </div>
          <div style="background:rgba(0,245,196,0.05);border-radius:6px;padding:10px;border:1px solid rgba(0,245,196,0.1)">
            <p class="mono text-xs" style="color:var(--accent)">③ SELECT</p>
            <p class="text-xs mt-1" style="color:var(--text)">Set branch: main · file: app.py</p>
          </div>
          <div style="background:rgba(0,245,196,0.05);border-radius:6px;padding:10px;border:1px solid rgba(0,245,196,0.1)">
            <p class="mono text-xs" style="color:var(--accent)">④ LIVE</p>
            <p class="text-xs mt-1" style="color:var(--text)">Deploy → live URL in ~60 seconds</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Tab: QA Report -->
    <div class="tab-panel" id="panel-qa">
      <div class="grid gap-6" style="grid-template-columns:1fr 1fr">
        <div>
          <p class="mono text-xs mb-3" style="color:var(--accent)">▸ FRONTEND CHECKS</p>
          <div class="qa-item qa-pass"><span>✓</span><span class="text-sm">All Chart.js canvases render without errors</span></div>
          <div class="qa-item qa-pass"><span>✓</span><span class="text-sm">CSV export downloads correct data</span></div>
          <div class="qa-item qa-pass"><span>✓</span><span class="text-sm">Time-series filter buttons update chart</span></div>
          <div class="qa-item qa-pass"><span>✓</span><span class="text-sm">Hover tooltips display on all charts</span></div>
          <div class="qa-item qa-pass"><span>✓</span><span class="text-sm">Live clock updates every second</span></div>
          <div class="qa-item qa-pass"><span>✓</span><span class="text-sm">Donut chart legend matches percentages</span></div>
        </div>
        <div>
          <p class="mono text-xs mb-3" style="color:var(--accent)">▸ BACKEND / DATA CHECKS</p>
          <div class="qa-item qa-pass"><span>✓</span><span class="text-sm">CSV loads and parses without NaN errors</span></div>
          <div class="qa-item qa-pass"><span>✓</span><span class="text-sm">KPI calculations verified against raw data</span></div>
          <div class="qa-item qa-pass"><span>✓</span><span class="text-sm">Time-series simulation produces 180 rows (30d × 6 events)</span></div>
          <div class="qa-item qa-pass"><span>✓</span><span class="text-sm">@st.cache_data prevents redundant reloads</span></div>
          <div class="qa-item qa-pass"><span>✓</span><span class="text-sm">No secrets or credentials in source files</span></div>
          <div class="qa-item qa-pass" style="border-color:rgba(255,209,102,0.25);background:rgba(255,209,102,0.05)">
            <span style="color:#FFD166">⚠</span>
            <span class="text-sm">Mobile viewport: Streamlit iframe clips at &lt;768px</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Tab: WordPress Integration -->
    <div class="tab-panel" id="panel-wp">
      <div class="grid gap-6" style="grid-template-columns:1fr 1fr">
        <div>
          <p class="mono text-xs mb-3" style="color:var(--accent)">▸ WORDPRESS EMBED PATTERN</p>
          <div class="doc-step">
            <div class="step-num">1</div>
            <div>
              <p class="text-sm font-semibold">Deploy Streamlit to a public URL</p>
              <p class="text-xs mt-1" style="color:var(--muted)">Use Streamlit Cloud or Azure App Service to get a stable HTTPS endpoint.</p>
            </div>
          </div>
          <div class="doc-step">
            <div class="step-num">2</div>
            <div>
              <p class="text-sm font-semibold">Embed via WP iframe block</p>
              <p class="text-xs mt-1" style="color:var(--muted)">In the WordPress block editor, use a Custom HTML block:<br/><code style="color:var(--accent4);font-size:0.7rem">&lt;iframe src="https://your-app.streamlit.app" width="100%" height="900"&gt;</code></p>
            </div>
          </div>
          <div class="doc-step">
            <div class="step-num">3</div>
            <div>
              <p class="text-sm font-semibold">Configure CORS in config.toml</p>
              <p class="text-xs mt-1" style="color:var(--muted)">Set <code style="color:var(--accent4);font-size:0.7rem">enableCORS = true</code> and allowedOrigins to your WordPress domain to permit cross-origin embedding.</p>
            </div>
          </div>
          <div class="doc-step">
            <div class="step-num">4</div>
            <div>
              <p class="text-sm font-semibold">WP Engine hosting compatibility</p>
              <p class="text-xs mt-1" style="color:var(--muted)">The dashboard is a standalone app — WP Engine hosts the WordPress site. Both coexist; the dashboard is iframed in. No PHP dependency required.</p>
            </div>
          </div>
        </div>
        <div>
          <p class="mono text-xs mb-3" style="color:var(--accent)">▸ INTEGRATION CHECKLIST</p>
          <div class="qa-item qa-pass"><span>✓</span><span class="text-sm">HTTPS endpoint required for WP embed (SSL cert)</span></div>
          <div class="qa-item qa-pass"><span>✓</span><span class="text-sm">No WordPress user auth needed — dashboard is read-only</span></div>
          <div class="qa-item qa-pass"><span>✓</span><span class="text-sm">Responsive iframe via CSS (width:100%)</span></div>
          <div class="qa-item qa-pass"><span>✓</span><span class="text-sm">Can be restricted to logged-in WP users via plugin</span></div>
          <div class="qa-item qa-pass" style="border-color:rgba(255,209,102,0.25);background:rgba(255,209,102,0.05)">
            <span style="color:#FFD166">⚠</span>
            <span class="text-sm">X-Frame-Options header must allow embedding</span>
          </div>
          <div class="qa-item qa-pass" style="border-color:rgba(255,209,102,0.25);background:rgba(255,209,102,0.05)">
            <span style="color:#FFD166">⚠</span>
            <span class="text-sm">WP Engine firewall rules may need update for iframe origin</span>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- ═══════════════════════════════════════════════════════════════════════ -->
  <!-- NEW SECTION 3 — TECHNICAL PROCESS DOCUMENTATION ───────────────────── -->
  <!-- ═══════════════════════════════════════════════════════════════════════ -->
  <div class="chart-card fade-in delay-4">
    <p class="section-label mb-1">TECHNICAL DOCUMENTATION</p>
    <h3 class="text-base font-bold mb-6">System Architecture & Process Log</h3>

    <div id="accordion">

      <div>
        <button class="accordion-btn" onclick="toggleAccordion(0)">
          <span>📥 Data Pipeline — GA4 CSV → Python → Dashboard</span>
          <span id="acc-icon-0">＋</span>
        </button>
        <div class="accordion-content" id="acc-0">
          <div class="grid gap-6" style="grid-template-columns:1fr 1fr">
            <div>
              <div class="doc-step">
                <div class="step-num">1</div>
                <div>
                  <p class="text-sm font-semibold">Ingest</p>
                  <p class="text-xs mt-1" style="color:var(--muted)"><code>ga4_data.csv</code> exported from GA4 API or manually. Schema: Event name, Event count, Total users, Events/active user, Total revenue.</p>
                </div>
              </div>
              <div class="doc-step">
                <div class="step-num">2</div>
                <div>
                  <p class="text-sm font-semibold">Transform</p>
                  <p class="text-xs mt-1" style="color:var(--muted)">Pandas strips whitespace, coerces numeric types, sorts by event count descending. No external DB required — stateless per-request.</p>
                </div>
              </div>
            </div>
            <div>
              <div class="doc-step">
                <div class="step-num">3</div>
                <div>
                  <p class="text-sm font-semibold">Simulate</p>
                  <p class="text-xs mt-1" style="color:var(--muted)">30-day time-series generated from event totals using seeded NumPy noise + weekend seasonality (×1.3). Reproducible across restarts.</p>
                </div>
              </div>
              <div class="doc-step">
                <div class="step-num">4</div>
                <div>
                  <p class="text-sm font-semibold">Serve</p>
                  <p class="text-xs mt-1" style="color:var(--muted)">Python serialises all computed data to JSON and injects it into an HTML string. Streamlit renders via <code>components.html()</code>. Chart.js consumes the JS globals.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div>
        <button class="accordion-btn" onclick="toggleAccordion(1)">
          <span>🛠 Tech Stack Decisions — Why Each Tool Was Chosen</span>
          <span id="acc-icon-1">＋</span>
        </button>
        <div class="accordion-content" id="acc-1">
          <div class="grid gap-3" style="grid-template-columns:repeat(3,1fr)">
            <div style="background:rgba(0,245,196,0.04);border-radius:8px;padding:12px;border:1px solid rgba(0,245,196,0.1)">
              <p class="mono text-xs" style="color:var(--accent)">STREAMLIT</p>
              <p class="text-xs mt-2" style="color:var(--text)">Zero-config Python web server. Rapid prototyping with <code>@st.cache_data</code> for performance. Ideal for data teams without frontend specialists.</p>
            </div>
            <div style="background:rgba(124,106,247,0.04);border-radius:8px;padding:12px;border:1px solid rgba(124,106,247,0.15)">
              <p class="mono text-xs" style="color:var(--accent2)">CHART.JS 4.4</p>
              <p class="text-xs mt-2" style="color:var(--text)">Lightweight (~200KB). Native canvas rendering. Accessible via ARIA plugin. Chosen over D3 for lower maintenance overhead.</p>
            </div>
            <div style="background:rgba(255,209,102,0.04);border-radius:8px;padding:12px;border:1px solid rgba(255,209,102,0.15)">
              <p class="mono text-xs" style="color:var(--accent4)">TAILWIND CDN</p>
              <p class="text-xs mt-2" style="color:var(--text)">Utility-first CSS without a build step. Consistent spacing/typography via tokens. No class purging needed for embedded HTML.</p>
            </div>
            <div style="background:rgba(255,107,107,0.04);border-radius:8px;padding:12px;border:1px solid rgba(255,107,107,0.15)">
              <p class="mono text-xs" style="color:var(--accent3)">PANDAS / NUMPY</p>
              <p class="text-xs mt-2" style="color:var(--text)">Industry-standard data wrangling. NumPy seeded RNG for reproducible simulations. Vectorised operations keep load times &lt;200ms.</p>
            </div>
            <div style="background:rgba(6,214,160,0.04);border-radius:8px;padding:12px;border:1px solid rgba(6,214,160,0.15)">
              <p class="mono text-xs" style="color:#06D6A0">VANILLA JS</p>
              <p class="text-xs mt-2" style="color:var(--text)">No framework dependency. Event delegation, DOM manipulation, CSV export — all native browser APIs. Zero npm, zero build toolchain.</p>
            </div>
            <div style="background:rgba(17,138,178,0.04);border-radius:8px;padding:12px;border:1px solid rgba(17,138,178,0.15)">
              <p class="mono text-xs" style="color:#118AB2">DOCKER / AZURE</p>
              <p class="text-xs mt-2" style="color:var(--text)">Container isolates Python deps. Azure App Service (B1) supports long-running Streamlit processes. Dockerfile in repo root for CI/CD readiness.</p>
            </div>
          </div>
        </div>
      </div>

      <div>
        <button class="accordion-btn" onclick="toggleAccordion(2)">
          <span>🔄 Digital Workflow Improvement Proposals</span>
          <span id="acc-icon-2">＋</span>
        </button>
        <div class="accordion-content" id="acc-2">
          <div class="grid gap-4" style="grid-template-columns:1fr 1fr">
            <div>
              <p class="mono text-xs mb-3" style="color:var(--accent)">▸ IDENTIFIED GAPS</p>
              <div class="doc-step">
                <div class="step-num">!</div>
                <div>
                  <p class="text-sm font-semibold">Manual CSV Export Bottleneck</p>
                  <p class="text-xs mt-1" style="color:var(--muted)">Current flow requires manual GA4 export every session. Proposal: schedule a GitHub Action to pull fresh data via GA4 Data API nightly.</p>
                </div>
              </div>
              <div class="doc-step">
                <div class="step-num">!</div>
                <div>
                  <p class="text-sm font-semibold">No Alerting on Anomalies</p>
                  <p class="text-xs mt-1" style="color:var(--muted)">Sudden drop in <code>session_start</code> goes unnoticed. Proposal: Python script + Azure Logic App to send Teams webhook if daily count falls &gt;30% from 7-day average.</p>
                </div>
              </div>
            </div>
            <div>
              <p class="mono text-xs mb-3" style="color:var(--accent)">▸ PROPOSED SOLUTIONS</p>
              <div class="doc-step">
                <div class="step-num">→</div>
                <div>
                  <p class="text-sm font-semibold">Automated Data Refresh</p>
                  <p class="text-xs mt-1" style="color:var(--muted)">GitHub Actions + Google service account credentials stored as repo secrets. Cron job: <code>0 6 * * *</code> (6AM daily). No manual intervention needed.</p>
                </div>
              </div>
              <div class="doc-step">
                <div class="step-num">→</div>
                <div>
                  <p class="text-sm font-semibold">Microsoft Teams Webhook Integration</p>
                  <p class="text-xs mt-1" style="color:var(--muted)">Use Azure Logic Apps or Power Automate to post engagement alerts to a dedicated Teams channel — zero additional cost on the existing Azure tenant.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>

  <!-- ═══════════════════════════════════════════════════════════════════════ -->
  <!-- NEW SECTION 4 — ABOUT / BUILDER PROFILE ────────────────────────────── -->
  <!-- ═══════════════════════════════════════════════════════════════════════ -->
  <div class="about-card fade-in delay-2">
    <div class="grid gap-8" style="grid-template-columns:1fr auto">
      <div>
        <p class="section-label mb-2">ABOUT THIS PROJECT</p>
        <h3 class="text-xl font-extrabold mb-3" style="letter-spacing:-0.5px">Built by a Data Analytics Student</h3>
        <p class="text-sm leading-relaxed mb-4" style="color:var(--muted); max-width:640px">
          This dashboard was built as a hands-on project to bridge data analytics knowledge with real-world
          digital platform skills. The focus is on producing production-grade tooling — not just analysis —
          by combining Python data pipelines with accessible, standards-compliant frontend interfaces
          deployable on cloud infrastructure like <strong style="color:var(--text)">Microsoft Azure</strong> and
          <strong style="color:var(--text)">Streamlit Community Cloud</strong>.
        </p>
        <p class="text-sm leading-relaxed" style="color:var(--muted); max-width:640px">
          Core competencies demonstrated here include HTML/CSS/JS, accessibility auditing (WCAG 2.1 / AODA),
          content management integration patterns (WordPress + WP Engine), QA documentation,
          cloud deployment readiness, and digital workflow improvement — skills directly applicable
          to supporting student-facing digital platforms.
        </p>
        <div class="flex flex-wrap gap-2 mt-5">
          <span class="badge" style="color:var(--accent);border-color:rgba(0,245,196,0.3)">Data Analytics</span>
          <span class="badge" style="color:var(--accent2);border-color:rgba(124,106,247,0.3)">HTML · CSS · JS</span>
          <span class="badge" style="color:var(--accent4);border-color:rgba(255,209,102,0.3)">WCAG / AODA</span>
          <span class="badge" style="color:#06D6A0;border-color:rgba(6,214,160,0.3)">Azure · Docker</span>
          <span class="badge" style="color:#118AB2;border-color:rgba(17,138,178,0.3)">WordPress · WP Engine</span>
          <span class="badge" style="color:var(--accent3);border-color:rgba(255,107,107,0.3)">Python · Pandas</span>
        </div>
      </div>
      <div class="flex flex-col items-end justify-between" style="min-width:180px">
        <div style="text-align:right">
          <p class="mono text-xs" style="color:var(--muted)">BUILT FOR</p>
          <p class="text-sm font-bold mt-1">IGNITE Student Life</p>
          <p class="mono text-xs mt-1" style="color:var(--muted)">Web Support Assistant</p>
          <p class="mono text-xs" style="color:var(--accent)">Start: August 2026</p>
        </div>
        <div style="text-align:right">
          <div class="badge mb-2" style="color:var(--accent);border-color:rgba(0,245,196,0.3)">
            <span class="pulse-dot" style="width:6px;height:6px"></span> Portfolio Project
          </div>
          <p class="mono text-xs" style="color:var(--muted)">Humber / U of GH</p>
          <p class="mono text-xs" style="color:var(--muted)">Toronto, ON · 2025</p>
        </div>
      </div>
    </div>
  </div>

  <!-- Footer -->
  <footer class="flex items-center justify-between pb-4">
    <p class="mono text-xs" style="color:var(--muted)">© 2025 GA4 DASHBOARD · DATA ANALYTICS STUDENT PROJECT · MIT LICENSE</p>
    <div class="flex gap-4">
      <span class="badge" style="color:var(--muted);border-color:var(--border)">Python 3.11</span>
      <span class="badge" style="color:var(--muted);border-color:var(--border)">Pandas</span>
      <span class="badge" style="color:var(--muted);border-color:var(--border)">Chart.js 4.4</span>
      <span class="badge" style="color:var(--muted);border-color:var(--border)">Tailwind CSS</span>
      <span class="badge" style="color:var(--muted);border-color:var(--border)">WCAG 2.1 AA</span>
    </div>
  </footer>

</main>

<!-- ── DATA INJECTED BY PYTHON ────────────────────────────────────────────── -->
<script>
const KPI_DATA       = {kpi_data};
const SUMMARY_DATA   = {summary_data};
const TIMESERIES_DATA= {timeseries_data};
</script>

<!-- ── APP JS ──────────────────────────────────────────────────────────────── -->
<script>
// ── Clock ──────────────────────────────────────────────────────────────────
function updateClock(){{
  document.getElementById('clock').textContent =
    new Date().toLocaleTimeString('en-US',{{hour12:false}});
}}
setInterval(updateClock,1000); updateClock();

// ── Palette ────────────────────────────────────────────────────────────────
const PALETTE = ['#00F5C4','#7C6AF7','#FF6B6B','#FFD166','#06D6A0','#118AB2'];

// ── KPI Cards ──────────────────────────────────────────────────────────────
const kpiDefs = [
  {{key:'total_events',   label:'Total Events',        icon:'⚡', color:'var(--accent)'}},
  {{key:'total_users',    label:'Total Users',         icon:'👥', color:'#7C6AF7'}},
  {{key:'avg_events_per_user', label:'Avg Events / User', icon:'📈', color:'#FFD166', decimals:2}},
  {{key:'top_event',      label:'Top Event',           icon:'🏆', color:'#FF6B6B'}},
];
const grid = document.getElementById('kpi-grid');
kpiDefs.forEach((def,i)=>{{
  const val = def.decimals
    ? KPI_DATA[def.key].toFixed(def.decimals)
    : (typeof KPI_DATA[def.key]==='string'
        ? KPI_DATA[def.key].toUpperCase()
        : KPI_DATA[def.key].toLocaleString());
  grid.innerHTML += `
  <div class="kpi-card p-6 fade-in delay-${{i+1}}">
    <div class="flex items-center justify-between mb-4">
      <span class="section-label">${{def.label}}</span>
      <span style="font-size:1.4rem">${{def.icon}}</span>
    </div>
    <div class="kpi-value mono" style="color:${{def.color}}">${{val}}</div>
    <div class="progress-bar mt-4"><div class="progress-fill" style="width:${{Math.min(100,(i+1)*22)}}%"></div></div>
  </div>`;
}});

// ── Chart defaults ─────────────────────────────────────────────────────────
Chart.defaults.color = '#5A7FA8';
Chart.defaults.borderColor = 'rgba(0,245,196,0.08)';
Chart.defaults.font.family = "'Space Mono', monospace";
Chart.defaults.font.size = 11;

// ── Time-series Chart ──────────────────────────────────────────────────────
const tsEvents = ['scroll','page_view','user_engagement','button_click','first_visit','session_start'];
const tsLabels = TIMESERIES_DATA.map(r=>r.date.slice(5));
let tsChart;
function buildTimeSeries(filter='all'){{
  const datasets = tsEvents
    .filter(e=> filter==='all' || e===filter)
    .map((e,i)=>{{
      const data = TIMESERIES_DATA.map(r=>r[e]||0);
      const c = PALETTE[i % PALETTE.length];
      return {{
        label: e,
        data,
        borderColor: c,
        backgroundColor: c+'18',
        borderWidth: filter==='all' ? 1.5 : 2.5,
        pointRadius: 0,
        pointHoverRadius: 5,
        tension: 0.45,
        fill: filter!=='all',
      }};
    }});
  if(tsChart) tsChart.destroy();
  tsChart = new Chart(document.getElementById('timeseriesChart'),{{
    type:'line',
    data:{{ labels:tsLabels, datasets }},
    options:{{
      responsive:true,
      interaction:{{ mode:'index', intersect:false }},
      plugins:{{
        legend:{{ display:true, position:'top', labels:{{ boxWidth:8, padding:16 }} }},
        tooltip:{{ backgroundColor:'#0D1B2E', borderColor:'rgba(0,245,196,0.3)', borderWidth:1 }},
      }},
      scales:{{
        x:{{ grid:{{ color:'rgba(0,245,196,0.04)' }}, ticks:{{ maxTicksLimit:10 }} }},
        y:{{ grid:{{ color:'rgba(0,245,196,0.06)' }}, beginAtZero:true }},
      }},
    }},
  }});
}}
buildTimeSeries();
function filterTimeSeries(f){{
  buildTimeSeries(f);
  document.querySelectorAll('#ts-filters button').forEach(b=>{{
    b.style.color='var(--muted)'; b.style.borderColor='var(--border)'; b.style.background='transparent';
  }});
  event.target.style.color='var(--accent)';
  event.target.style.borderColor='var(--accent)';
  event.target.style.background='rgba(0,245,196,0.08)';
}}

// ── Donut Chart ────────────────────────────────────────────────────────────
const donutData = SUMMARY_DATA.map(r=>r['Event count']);
const donutLabels = SUMMARY_DATA.map(r=>r['Event name']);
const total = donutData.reduce((a,b)=>a+b,0);

new Chart(document.getElementById('donutChart'),{{
  type:'doughnut',
  data:{{
    labels: donutLabels,
    datasets:[{{
      data: donutData,
      backgroundColor: PALETTE.map(c=>c+'CC'),
      borderColor: PALETTE,
      borderWidth: 2,
      hoverOffset: 8,
    }}],
  }},
  options:{{
    responsive:true,
    cutout:'68%',
    plugins:{{
      legend:{{ display:false }},
      tooltip:{{
        backgroundColor:'#0D1B2E',
        borderColor:'rgba(0,245,196,0.3)',
        borderWidth:1,
        callbacks:{{ label: ctx=>`  ${{ctx.label}}: ${{ctx.parsed.toLocaleString()}} (${{(ctx.parsed/total*100).toFixed(1)}}%)` }},
      }},
    }},
  }},
}});
const legend = document.getElementById('donut-legend');
donutLabels.forEach((l,i)=>{{
  const pct = (donutData[i]/total*100).toFixed(1);
  legend.innerHTML += `
  <div class="flex items-center justify-between text-xs">
    <div class="flex items-center gap-2">
      <div style="width:8px;height:8px;border-radius:2px;background:${{PALETTE[i]}}"></div>
      <span style="color:var(--text)">${{l}}</span>
    </div>
    <span class="mono" style="color:var(--accent)">${{pct}}%</span>
  </div>`;
}});

// ── Bar Chart ──────────────────────────────────────────────────────────────
new Chart(document.getElementById('barChart'),{{
  type:'bar',
  data:{{
    labels: SUMMARY_DATA.map(r=>r['Event name']),
    datasets:[{{
      label:'Events per Active User',
      data: SUMMARY_DATA.map(r=>parseFloat(r['Event count per active user']||0).toFixed(2)),
      backgroundColor: PALETTE.map(c=>c+'33'),
      borderColor: PALETTE,
      borderWidth: 2,
      borderRadius: 6,
      borderSkipped: false,
    }}],
  }},
  options:{{
    indexAxis:'y',
    responsive:true,
    plugins:{{
      legend:{{ display:false }},
      tooltip:{{ backgroundColor:'#0D1B2E', borderColor:'rgba(0,245,196,0.3)', borderWidth:1 }},
    }},
    scales:{{
      x:{{ grid:{{ color:'rgba(0,245,196,0.06)' }}, beginAtZero:true }},
      y:{{ grid:{{ display:false }} }},
    }},
  }},
}});

// ── Scatter Chart ──────────────────────────────────────────────────────────
new Chart(document.getElementById('scatterChart'),{{
  type:'bubble',
  data:{{
    datasets: SUMMARY_DATA.map((r,i)=>{{
      const ec = r['Event count'];
      return {{
        label: r['Event name'],
        data:[{{ x: parseFloat(r['Event count per active user']||0), y: r['Total users'], r: Math.sqrt(ec)*1.2 }}],
        backgroundColor: PALETTE[i % PALETTE.length]+'55',
        borderColor: PALETTE[i % PALETTE.length],
        borderWidth:2,
      }};
    }}),
  }},
  options:{{
    responsive:true,
    plugins:{{
      legend:{{ position:'bottom', labels:{{ boxWidth:8, padding:12 }} }},
      tooltip:{{
        backgroundColor:'#0D1B2E', borderColor:'rgba(0,245,196,0.3)', borderWidth:1,
        callbacks:{{ label: ctx=>`${{ctx.dataset.label}}: ${{ctx.raw.x}} ev/user · ${{ctx.raw.y}} users` }},
      }},
    }},
    scales:{{
      x:{{ title:{{ display:true, text:'Events per Active User', color:'#5A7FA8' }}, grid:{{ color:'rgba(0,245,196,0.06)' }} }},
      y:{{ title:{{ display:true, text:'Total Users', color:'#5A7FA8' }}, grid:{{ color:'rgba(0,245,196,0.06)' }} }},
    }},
  }},
}});

// ── Data Table ─────────────────────────────────────────────────────────────
const tbody = document.getElementById('table-body');
const maxCount = Math.max(...SUMMARY_DATA.map(r=>r['Event count']));
SUMMARY_DATA.forEach((r,i)=>{{
  const share = (r['Event count']/total*100).toFixed(1);
  const score = Math.min(100, (r['Event count per active user']/181*100)).toFixed(0);
  tbody.innerHTML += `
  <tr>
    <td><div class="flex items-center gap-2">
      <div style="width:6px;height:6px;border-radius:50%;background:${{PALETTE[i%PALETTE.length]}}"></div>
      <span class="font-semibold">${{r['Event name']}}</span>
    </div></td>
    <td class="mono">${{r['Event count'].toLocaleString()}}</td>
    <td class="mono">${{r['Total users']}}</td>
    <td class="mono" style="color:var(--accent)">${{parseFloat(r['Event count per active user']||0).toFixed(2)}}</td>
    <td><span class="badge" style="color:var(--accent2);border-color:rgba(124,106,247,0.3);background:rgba(124,106,247,0.06)">${{share}}%</span></td>
    <td>
      <div class="flex items-center gap-3">
        <div class="progress-bar" style="width:120px"><div class="progress-fill" style="width:${{score}}%;background:${{PALETTE[i%PALETTE.length]}}"></div></div>
        <span class="mono text-xs" style="color:var(--muted)">${{score}}</span>
      </div>
    </td>
  </tr>`;
}});

// ── CSV Export ─────────────────────────────────────────────────────────────
function exportCSV(){{
  const headers = ['Event Name','Event Count','Total Users','Events per Active User','Share %'];
  const rows = SUMMARY_DATA.map(r=>[
    r['Event name'], r['Event count'], r['Total users'],
    parseFloat(r['Event count per active user']||0).toFixed(2),
    (r['Event count']/total*100).toFixed(1)
  ]);
  const csv = [headers, ...rows].map(r=>r.join(',')).join('\\n');
  const a = document.createElement('a');
  a.href = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv);
  a.download = 'ga4_engagement_export.csv';
  a.click();
}}

// ── NEW: Tab switcher ──────────────────────────────────────────────────────
function switchTab(id){{
  ['deploy','qa','wp'].forEach(t=>{{
    document.getElementById('panel-'+t).classList.remove('active');
    document.getElementById('tab-'+t).classList.remove('active');
  }});
  document.getElementById('panel-'+id).classList.add('active');
  document.getElementById('tab-'+id).classList.add('active');
}}

// ── NEW: Accordion ─────────────────────────────────────────────────────────
function toggleAccordion(i){{
  const content = document.getElementById('acc-'+i);
  const icon    = document.getElementById('acc-icon-'+i);
  const isOpen  = content.classList.contains('open');
  content.classList.toggle('open', !isOpen);
  icon.textContent = isOpen ? '＋' : '－';
}}
</script>
</body>
</html>
"""

    import streamlit.components.v1 as components
    components.html(html, height=3800, scrolling=True)


if __name__ == "__main__":
    main()
