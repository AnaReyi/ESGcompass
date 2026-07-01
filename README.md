# 🌿 ESG Compass — Multi-Framework ESG Intelligence Tool

A comprehensive ESG assessment and strategy tool aligned with:
**GRI · CDP · SASB · IFRS S1/S2 · S&P CSA · GRESB · SBTi / IPCC**

---

## Features

- 📊 **Multi-framework data input** — industry-specific indicators per GRI, SASB, CDP
- 🎯 **Target setting & SBTi-style validation** — validates against IPCC 1.5°C, RE100, CDP Water
- 📈 **Tailored strategies** — industry-specific improvement roadmaps (Steel, FMCG, Energy, Real Estate, etc.)
- 🌐 **SDG alignment** — maps your industry to relevant SDGs with target-level detail
- 🏛️ **Dashboard** — company leaderboard with E/S/G scores, grades, and target tracking
- 📥 **Excel template** — downloadable template per industry for offline data collection

---

## Deploying to Streamlit Cloud (Free, shareable link)

1. **Create a GitHub repo** and push these files:
   - `app.py`
   - `requirements.txt`

2. **Go to** [share.streamlit.io](https://share.streamlit.io)

3. **Sign in** with GitHub → click **"New app"**

4. Select your repo, branch (`main`), and set `app.py` as the main file

5. Click **Deploy** → you'll get a shareable URL like:
   `https://your-app-name.streamlit.app`

---

## Running Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open http://localhost:8501

---

## Framework Alignment Reference

| Framework | Coverage in Tool |
|-----------|-----------------|
| GRI Standards | GRI 200, 300, 400 series indicators; GRI 207 Tax |
| CDP | Climate, Water, Forests disclosures |
| SASB | Industry-specific material topics |
| IFRS S1/S2 | Climate-related financial disclosures |
| S&P CSA | Full E/S/G dimension scoring |
| GRESB | Real estate & infrastructure asset scoring |
| SBTi / IPCC | 1.5°C pathway target validation |
| UN SDGs | Industry-to-SDG mapping with target detail |

---

## Industry Coverage

Steel & Metals · FMCG · Energy & Utilities · Real Estate · Financial Services ·
Technology · Pharmaceuticals · Chemicals · Automotive · Agriculture · Textiles · Cement
