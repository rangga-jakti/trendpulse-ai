# TrendPulse AI

> Real-time Indonesian internet trend radar powered by AI & ML

[![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python)](https://python.org)
[![Django](https://img.shields.io/badge/Django-5.0-green?style=flat-square&logo=django)](https://djangoproject.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)
[![Groq](https://img.shields.io/badge/LLM-Groq%20LLaMA%203.3-orange?style=flat-square)](https://groq.com)

---

## Features

| Feature | Description |
|--------|-------------|
| **Real-time Radar** | Live trending topics from Google Trends Indonesia |
| **Breaking Trends** | Instant detection of sudden viral spikes |
| **AI Analysis** | Groq LLaMA 3.3-70B explains why topics trend |
| **ML Prediction** | Prophet forecasts trend trajectory 7-30 days ahead |
| **Content Ideas** | AI-generated ideas for YouTube, TikTok, Blog & Business |
| **Live News** | Related news fetched from Google News RSS |
| **Virality Score** | 0-100 score based on search volume, growth & momentum |
| **Export CSV** | Download all trend data for deeper analysis |
| **Auth System** | Login & register with full user management |

---

## Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL
- Groq API key (free at [console.groq.com](https://console.groq.com))
- NewsAPI key (free at [newsapi.org](https://newsapi.org))

### Installation

```bash
# 1. Clone repo
git clone https://github.com/yourusername/trendpulse-ai.git
cd trendpulse-ai

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment variables
cp .env.example .env
# Edit .env with your credentials

# 5. Setup database
python manage.py migrate

# 6. Create superuser
python manage.py createsuperuser

# 7. Fetch initial data
python manage.py fetch_trends

# 8. Run server
python manage.py runserver
```

Open http://127.0.0.1:8000 🎉

---

## ⚙️ Environment Variables

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=trendpulse_db
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432
GROQ_API_KEY=gsk_...
NEWS_API_KEY=...
MAX_TRENDS_PER_FETCH=50
LLM_MODEL=llama-3.3-70b-versatile
```

---

## Tech Stack

**Backend:** Python 3.12, Django 5.0, PostgreSQL  
**AI/ML:** Groq LLaMA 3.3-70B, Prophet, scikit-learn  
**Data:** Google Trends RSS, Google News RSS, NewsAPI  
**Frontend:** TailwindCSS, Alpine.js, Chart.js, HTMX  

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">Built for the Indonesian digital ecosystem</p>
