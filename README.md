# 📊 GA4 Engagement Dashboard

> A production-ready analytics dashboard built with **Streamlit**, **Chart.js**, **Tailwind CSS**, and **Python** — visualising Google Analytics 4 engagement data with a dark, cyber-themed UI.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io/cloud)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-FF4B4B?logo=streamlit)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🖥️ Live Demo

Deploy instantly on **Streamlit Community Cloud** → [Deploy Guide](#-deployment)

---

## ✨ Features

| Feature | Details |
|---|---|
| **KPI Cards** | Total events, users, avg events/user, top event |
| **Time-Series Chart** | 30-day simulated engagement trend with filter buttons |
| **Donut Chart** | Event distribution with custom legend |
| **Horizontal Bar** | Events per active user by event type |
| **Bubble Chart** | User reach × activity scatter |
| **Data Table** | Sortable table with engagement score bars |
| **CSV Export** | One-click download of processed data |
| **Dark Theme** | Cyber/terminal aesthetic with Tailwind CSS |

---

## 🏗️ Project Structure

```
ga4-dashboard/
├── app.py                  # Streamlit entry point
├── requirements.txt        # Python dependencies
├── data/
│   └── ga4_data.csv        # GA4 export (replace with real data)
├── backend/
│   └── ga4_analysis.py     # Standalone analytics + chart generation
├── .streamlit/
│   └── config.toml         # Streamlit theme config
└── README.md
```

---

## 🚀 Quickstart (Local)

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/ga4-dashboard.git
cd ga4-dashboard

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the dashboard
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

---

## ☁️ Deployment

### Streamlit Community Cloud (Free)

1. Push this repo to **GitHub**
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Select your repo, branch `main`, file `app.py`
4. Click **Deploy** — live in ~60 seconds ✅

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
docker build -t ga4-dashboard .
docker run -p 8501:8501 ga4-dashboard
```

---

## 🔌 Using Real GA4 Data

Replace `data/ga4_data.csv` with an export from the GA4 Data API:

```python
# backend/ga4_analysis.py already supports the GA4 API — swap in your credentials:
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric

client = BetaAnalyticsDataClient()  # set GOOGLE_APPLICATION_CREDENTIALS env var
request = RunReportRequest(
    property=f"properties/YOUR_PROPERTY_ID",
    date_ranges=[DateRange(start_date="30daysAgo", end_date="today")],
    dimensions=[Dimension(name="eventName")],
    metrics=[
        Metric(name="eventCount"),
        Metric(name="totalUsers"),
        Metric(name="eventCountPerUser"),
    ],
)
response = client.run_report(request)
```

---

## 🛠️ Tech Stack

- **Python 3.11** — backend analytics
- **Streamlit 1.35** — web server & component rendering
- **Pandas / NumPy** — data processing & simulation
- **Matplotlib / Seaborn** — static chart generation (standalone script)
- **Chart.js 4.4** — interactive frontend charts
- **Tailwind CSS (CDN)** — utility-first styling
- **Vanilla JS** — zero-framework interactivity
- **Google Fonts** — Syne + Space Mono typography

---

## 📈 Key Insights from the Data

- **Scroll** dominates at **47.9%** of total events — users engage deeply with content
- **Page View** accounts for **24.6%** — healthy traffic but scroll/view ratio suggests long sessions
- **User Engagement** at **15.5%** indicates active interaction beyond passive browsing
- **Button Click** at **11%** shows moderate CTA conversion — room to optimise
- `first_visit` and `session_start` parity (both 9 users) confirms single-session new users

---

## 📁 Data Format

The CSV must follow this schema:

```csv
Event name,Event count,Total users,Event count per active user,Total revenue
scroll,903,5,180.6,0
page_view,463,10,46.3,0
```

---

## 📄 License

MIT © 2025
# user-engagement-monitoring-analysis
# user-engament-analysis
