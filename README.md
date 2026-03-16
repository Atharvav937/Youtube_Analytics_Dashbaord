# 📊 YouTube Analytics Dashboard
**Infosys Springboard Internship Project**

A full-featured Streamlit web app that fetches, stores, and visualizes YouTube channel analytics using the YouTube Data API v3.

---

## 🚀 Features

| Module | What it does |
|---|---|
| **📥 Fetch Channel** | Pull channel info + all video stats via YouTube API, store to SQLite |
| **📊 Channel Analytics** | Trends, top videos, engagement charts, posting habits — date-filtered |
| **🔍 Video Explorer** | Search, sort, filter videos + CSV download |
| **⚖️ Compare Channels** | Side-by-side KPI table, overlay trend chart, box plot, radar chart |
| **🏠 Overview** | Platform-wide stats across all stored channels |

---

## 📁 File Structure

```
├── app.py           # Main Streamlit dashboard (5 pages)
├── database.py      # SQLite helpers (create, insert, query)
├── youtube_api.py   # YouTube Data API v3 wrappers
├── youtube_data.db  # SQLite database (auto-created)
└── README.md
```

---

## ⚙️ Setup

### 1. Install dependencies
```bash
pip install streamlit pandas plotly google-api-python-client
```

### 2. Add your API key
Open `youtube_api.py` and replace:
```python
API_KEY = "YOUR_YOUTUBE_API_KEY"
```
Get a key from [Google Cloud Console](https://console.cloud.google.com/) → Enable **YouTube Data API v3**.

### 3. Run the app
```bash
streamlit run app.py
```

---

## 🗄️ Database Schema

**channel**
| column | type |
|---|---|
| channel_id | TEXT PK |
| channel_name | TEXT |
| subscribers | INTEGER |
| total_views | INTEGER |
| total_videos | INTEGER |

**video**
| column | type |
|---|---|
| video_id | TEXT PK |
| channel_id | TEXT FK |
| title | TEXT |
| views | INTEGER |
| likes | INTEGER |
| comments | INTEGER |
| published_date | TEXT |
| engagement_rate | REAL |

---

## 📊 Analytics Included

- Monthly views / likes / upload frequency trends
- Top-N videos by views (colour-coded by engagement)
- Engagement rate distribution (donut chart)
- Views vs Engagement scatter plot
- Likes vs Comments bubble chart
- Day-of-week & yearly upload frequency heatmaps
- Channel comparison: radar chart, box plot, overlay trends

---

*Built with Streamlit · Plotly · SQLite · YouTube Data API v3*
