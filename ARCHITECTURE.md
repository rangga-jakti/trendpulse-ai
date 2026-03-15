# TrendPulse AI - System Architecture

## Overview
TrendPulse AI adalah platform SaaS premium untuk mendeteksi, menganalisis, dan memprediksi tren internet secara real-time menggunakan AI dan Machine Learning.

## Tech Stack
- **Backend**: Python 3.12, Django 5.x, PostgreSQL 16
- **Frontend**: TailwindCSS 3.x, Alpine.js, Chart.js 4.x, HTMX
- **AI/LLM**: Groq API (llama3-70b-8192) / OpenAI compatible
- **ML**: scikit-learn, pandas, Prophet (time-series forecasting)
- **Data Sources**: pytrends (Google Trends), NewsAPI
- **Cache**: Redis (real-time updates)
- **Task Queue**: Celery + Redis (async data fetching)

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    TrendPulse AI Platform                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  Google       │    │   NewsAPI    │    │  Social APIs │  │
│  │  Trends       │    │              │    │  (Future)    │  │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘  │
│         │                   │                   │           │
│  ┌──────▼───────────────────▼───────────────────▼───────┐  │
│  │              Data Ingestion Layer (Celery)            │  │
│  │  - Scheduled fetching every 15 minutes                │  │
│  │  - Data normalization & cleaning                      │  │
│  │  - Deduplication & storage                           │  │
│  └──────────────────────────┬────────────────────────────┘  │
│                             │                               │
│  ┌──────────────────────────▼────────────────────────────┐  │
│  │                   Django Backend                       │  │
│  │                                                        │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐  │  │
│  │  │  trends app  │  │ analytics   │  │  ai_engine   │  │  │
│  │  │  - Fetch     │  │ app         │  │  app         │  │  │
│  │  │  - Store     │  │  - Virality │  │  - LLM API   │  │  │
│  │  │  - Display   │  │  - Scoring  │  │  - Analysis  │  │  │
│  │  └─────────────┘  └─────────────┘  └──────────────┘  │  │
│  │                                                        │  │
│  │  ┌─────────────┐  ┌─────────────────────────────────┐ │  │
│  │  │  ml_engine  │  │          dashboard app          │ │  │
│  │  │  - Prophet  │  │  - Aggregated views              │ │  │
│  │  │  - Forecast │  │  - Real-time updates (HTMX)     │ │  │
│  │  │  - Predict  │  │  - Charts & Visualizations      │ │  │
│  │  └─────────────┘  └─────────────────────────────────┘ │  │
│  └──────────────────────────┬────────────────────────────┘  │
│                             │                               │
│  ┌──────────────────────────▼────────────────────────────┐  │
│  │                  PostgreSQL Database                   │  │
│  │  - TrendTopic, TrendDataPoint, NewsArticle            │  │
│  │  - ViralityScore, AIInsight, MLPrediction             │  │
│  │  - ContentIdea, UserSession                           │  │
│  └────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Django Apps Structure

### 1. `trends` app
- Models: TrendTopic, TrendDataPoint, NewsArticle
- Services: GoogleTrendsService, NewsAPIService
- Tasks: fetch_trends_task, fetch_news_task

### 2. `analytics` app
- Models: ViralityScore
- Services: ViralityEngine (scoring algorithm)

### 3. `ai_engine` app
- Models: AIInsight, ContentIdea
- Services: LLMService (Groq/OpenAI), PromptBuilder

### 4. `ml_engine` app
- Models: MLPrediction
- Services: ProphetForecaster, TrendPredictor

### 5. `dashboard` app
- Views: Main dashboard, trend detail
- API endpoints for HTMX partial updates

## ML Pipeline Design

```
Raw Data → Feature Engineering → Prophet Model → Forecast → Store
  │              │                    │              │
  ├─ interest    ├─ rolling_avg       ├─ 7d pred    ├─ MLPrediction
  ├─ news_count  ├─ growth_rate       ├─ 30d pred   └─ confidence
  └─ timestamp   └─ momentum         └─ trend dir
```

## Virality Score Formula
```
virality = (
  w1 * normalized_search_volume +
  w2 * growth_velocity +
  w3 * news_coverage_score +
  w4 * momentum_score
) * 100

Weights: w1=0.35, w2=0.30, w3=0.20, w4=0.15
```
