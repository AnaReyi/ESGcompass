import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
import io
from datetime import datetime

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ESG Compass",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── PALETTE & STYLE ────────────────────────────────────────────────────────
COLORS = {
    "deep":   "#0D2B1A",
    "dark":   "#0D3D26",
    "mid":    "#1A6B3C",
    "leaf":   "#2E8B57",
    "mist":   "#A8D5B5",
    "foam":   "#DAF1DE",
    "bg":     "#F0FAF2",
    "white":  "#FFFFFF",
    "text":   "#1A2E1F",
    "subtle": "#5A8A6A",
}

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
    background-color: {COLORS['bg']};
    color: {COLORS['text']};
}}

/* Sidebar */
section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {COLORS['dark']} 0%, {COLORS['deep']} 100%);
    border-right: none;
}}
section[data-testid="stSidebar"] * {{
    color: {COLORS['foam']} !important;
}}
section[data-testid="stSidebar"] .stRadio label {{
    color: {COLORS['mist']} !important;
    font-size: 0.9rem;
    padding: 4px 0;
}}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stRadio div {{
    color: {COLORS['foam']} !important;
}}

/* Main header */
.main-header {{
    background: linear-gradient(135deg, {COLORS['dark']} 0%, {COLORS['mid']} 100%);
    border-radius: 16px;
    padding: 28px 36px;
    margin-bottom: 24px;
    color: white;
}}
.main-header h1 {{
    color: white;
    font-size: 2rem;
    font-weight: 700;
    margin: 0 0 4px 0;
    letter-spacing: -0.5px;
}}
.main-header p {{
    color: {COLORS['mist']};
    margin: 0;
    font-size: 0.95rem;
}}

/* Cards */
.esg-card {{
    background: white;
    border-radius: 14px;
    padding: 20px 24px;
    box-shadow: 0 2px 12px rgba(13,61,38,0.08);
    border: 1px solid {COLORS['foam']};
    margin-bottom: 16px;
}}
.metric-card {{
    background: linear-gradient(135deg, {COLORS['foam']} 0%, white 100%);
    border-radius: 14px;
    padding: 20px;
    text-align: center;
    border: 1px solid {COLORS['mist']};
}}
.metric-card .value {{
    font-size: 2rem;
    font-weight: 700;
    color: {COLORS['mid']};
}}
.metric-card .label {{
    font-size: 0.8rem;
    color: {COLORS['subtle']};
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: 4px;
}}

/* Score badge */
.score-A {{ background: #1A6B3C; color: white; }}
.score-B {{ background: #4CAF80; color: white; }}
.score-C {{ background: #F59E0B; color: white; }}
.score-D {{ background: #EF4444; color: white; }}
.score-badge {{
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.8rem;
}}

/* Target pill */
.target-on-track {{
    background: #DCFCE7;
    color: #15803D;
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.8rem;
    font-weight: 500;
    display: inline-block;
}}
.target-at-risk {{
    background: #FEF3C7;
    color: #B45309;
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.8rem;
    font-weight: 500;
    display: inline-block;
}}
.target-lagging {{
    background: #FEE2E2;
    color: #B91C1C;
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.8rem;
    font-weight: 500;
    display: inline-block;
}}

/* Section headers */
.section-label {{
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: {COLORS['subtle']};
    font-weight: 600;
    margin-bottom: 8px;
}}

/* Framework badge */
.framework-badge {{
    display: inline-block;
    background: {COLORS['foam']};
    color: {COLORS['mid']};
    border: 1px solid {COLORS['mist']};
    border-radius: 6px;
    padding: 2px 8px;
    font-size: 0.72rem;
    font-weight: 500;
    margin: 2px;
}}

/* SDG icon */
.sdg-chip {{
    display: inline-block;
    border-radius: 8px;
    padding: 4px 10px;
    font-size: 0.75rem;
    font-weight: 600;
    margin: 2px;
    color: white;
}}

/* Strategy box */
.strategy-box {{
    background: linear-gradient(135deg, {COLORS['foam']} 0%, #E8F5EC 100%);
    border-left: 4px solid {COLORS['leaf']};
    border-radius: 0 12px 12px 0;
    padding: 14px 18px;
    margin: 8px 0;
}}

/* Alert boxes */
.alert-warning {{
    background: #FFFBEB;
    border-left: 4px solid #F59E0B;
    border-radius: 0 8px 8px 0;
    padding: 12px 16px;
    margin: 8px 0;
    font-size: 0.88rem;
}}
.alert-success {{
    background: #F0FDF4;
    border-left: 4px solid #22C55E;
    border-radius: 0 8px 8px 0;
    padding: 12px 16px;
    margin: 8px 0;
    font-size: 0.88rem;
}}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {{
    background: {COLORS['foam']};
    border-radius: 10px;
    padding: 4px;
    gap: 2px;
}}
.stTabs [data-baseweb="tab"] {{
    border-radius: 8px;
    color: {COLORS['subtle']};
    font-weight: 500;
}}
.stTabs [aria-selected="true"] {{
    background: white !important;
    color: {COLORS['mid']} !important;
}}

/* Buttons */
.stButton > button {{
    background: linear-gradient(135deg, {COLORS['mid']} 0%, {COLORS['dark']} 100%);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    padding: 8px 20px;
    transition: all 0.2s;
}}
.stButton > button:hover {{
    background: linear-gradient(135deg, {COLORS['leaf']} 0%, {COLORS['mid']} 100%);
    transform: translateY(-1px);
}}

/* Table */
.stDataFrame {{
    border-radius: 12px;
    overflow: hidden;
}}

div[data-testid="stExpander"] {{
    background: white;
    border: 1px solid {COLORS['foam']};
    border-radius: 12px;
}}
</style>
""", unsafe_allow_html=True)


# ─── DATA STRUCTURES ────────────────────────────────────────────────────────

INDUSTRIES = [
    "Steel & Metals", "FMCG / Consumer Goods", "Energy & Utilities",
    "Real Estate", "Financial Services", "Technology & IT",
    "Pharmaceuticals", "Chemicals", "Automotive", "Agriculture & Food",
    "Textiles & Apparel", "Cement & Construction"
]

FRAMEWORKS = ["GRI", "SASB", "CDP", "TCFD", "IFRS S1/S2", "S&P CSA", "GRESB", "IPCC/SBTi"]

SDG_COLORS = {
    1: "#E5243B", 2: "#DDA63A", 3: "#4C9F38", 4: "#C5192D", 5: "#FF3A21",
    6: "#26BDE2", 7: "#FCC30B", 8: "#A21942", 9: "#FD6925", 10: "#DD1367",
    11: "#FD9D24", 12: "#BF8B2E", 13: "#3F7E44", 14: "#0A97D9", 15: "#56C02B",
    16: "#00689D", 17: "#19486A"
}
SDG_NAMES = {
    1: "No Poverty", 2: "Zero Hunger", 3: "Good Health", 4: "Quality Education",
    5: "Gender Equality", 6: "Clean Water", 7: "Affordable Energy", 8: "Decent Work",
    9: "Industry & Innovation", 10: "Reduced Inequalities", 11: "Sustainable Cities",
    12: "Responsible Consumption", 13: "Climate Action", 14: "Life Below Water",
    15: "Life on Land", 16: "Peace & Justice", 17: "Partnerships"
}

INDUSTRY_SDGS = {
    "Steel & Metals": [7, 9, 12, 13, 15, 8],
    "FMCG / Consumer Goods": [2, 3, 6, 12, 13, 14, 15],
    "Energy & Utilities": [7, 9, 13, 6, 11],
    "Real Estate": [11, 13, 6, 7, 15],
    "Financial Services": [1, 8, 9, 10, 17],
    "Technology & IT": [4, 8, 9, 12, 13],
    "Pharmaceuticals": [3, 6, 12, 13],
    "Chemicals": [3, 6, 9, 12, 13, 14, 15],
    "Automotive": [7, 9, 11, 12, 13],
    "Agriculture & Food": [2, 6, 12, 13, 14, 15],
    "Textiles & Apparel": [5, 6, 8, 12, 13],
    "Cement & Construction": [9, 11, 12, 13, 15]
}

INDUSTRY_SPECIFIC_INDICATORS = {
    "Steel & Metals": {
        "E": ["Metal scrap recovery rate (%)", "Slag reuse rate (%)", "Blast furnace CO2 intensity (tCO2/t steel)",
              "Process water recycling rate (%)", "Heat recovery efficiency (%)", "Particulate matter emissions (kg/t)"],
        "S": ["Heat stress incidents", "Noise exposure compliance (%)", "Fatal accident rate",
              "Contractor safety hours", "Community grievance resolution time (days)"],
        "G": ["Board ESG oversight", "Supply chain audit coverage (%)", "Anti-corruption training (%)"]
    },
    "FMCG / Consumer Goods": {
        "E": ["Plastic packaging reduction (%)", "Recycled content in packaging (%)", "Paper/cardboard waste (%)",
              "Water use per unit of production", "Scope 3 supplier emissions", "Product carbon footprint"],
        "S": ["Fair wages in supply chain (%)", "Child labor audits passed (%)", "Women in leadership (%)"],
        "G": ["Responsible marketing compliance", "Product recall transparency", "Supplier code adherence (%)"]
    },
    "Energy & Utilities": {
        "E": ["Renewable energy share (%)", "Grid loss rate (%)", "Methane leak detection coverage (%)",
              "Flaring intensity", "Biodiversity offset ratio"],
        "S": ["Energy access programs (beneficiaries)", "Just transition commitments", "Health & safety LTI rate"],
        "G": ["Regulatory compliance rate", "Asset stranding disclosures", "Executive pay-ESG linkage (%)"]
    },
    "Real Estate": {
        "E": ["Building energy intensity (kWh/m²)", "Green certification coverage (%)", "Embodied carbon (kgCO2/m²)",
              "Water intensity (m³/m²)", "Waste diversion from landfill (%)"],
        "S": ["Tenant satisfaction score", "Affordable housing units (%)", "Community investment (% revenue)"],
        "G": ["Climate risk disclosure", "Green lease adoption (%)", "ESG-linked financing (%)"]
    },
}

# Default indicators for industries not specifically listed
DEFAULT_INDICATORS = {
    "E": ["GHG Scope 1 emissions (tCO2e)", "GHG Scope 2 emissions (tCO2e)", "GHG Scope 3 emissions (tCO2e)",
          "Energy consumption (MWh)", "Renewable energy share (%)", "Water withdrawal (m³)",
          "Water recycling rate (%)", "Waste generated (tonnes)", "Waste diverted from landfill (%)",
          "Biodiversity impact assessment"],
    "S": ["Total employees", "Women in workforce (%)", "Women in senior management (%)",
          "Employee turnover rate (%)", "Training hours per employee", "LTIFR (Lost Time Injury Frequency Rate)",
          "Community investment (USD)", "Human rights grievances"],
    "G": ["Board independence (%)", "ESG-linked executive remuneration (%)", "Anti-corruption training (%)",
          "Data privacy incidents", "Supply chain ESG audits (%)", "Whistleblower cases resolved (%)"]
}

TARGET_CATEGORIES = [
    "Net Zero / Carbon Neutral", "Science-Based Target (SBTi)", "100% Renewable Energy",
    "Water Positive / Water Neutral", "Zero Waste to Landfill", "Circular Economy",
    "Supply Chain Decarbonisation", "Biodiversity Net Positive", "Living Wage",
    "Gender Parity", "Zero Fatalities", "TCFD Alignment", "Custom"
]

# ─── SAMPLE COMPANIES (for dashboard) ───────────────────────────────────────
SAMPLE_COMPANIES = {
    "TerraSteel Ltd": {
        "industry": "Steel & Metals", "country": "India", "revenue_bn": 4.2,
        "E_score": 62, "S_score": 71, "G_score": 68, "overall": 67,
        "grade": "B", "frameworks": ["GRI", "CDP", "SASB"],
        "targets": 4, "on_track": 2, "at_risk": 1, "lagging": 1
    },
    "GreenPack FMCG": {
        "industry": "FMCG / Consumer Goods", "country": "India", "revenue_bn": 2.1,
        "E_score": 74, "S_score": 69, "G_score": 82, "overall": 75,
        "grade": "B+", "frameworks": ["GRI", "SASB", "S&P CSA"],
        "targets": 6, "on_track": 4, "at_risk": 2, "lagging": 0
    },
    "Solaris Power": {
        "industry": "Energy & Utilities", "country": "India", "revenue_bn": 8.7,
        "E_score": 85, "S_score": 73, "G_score": 76, "overall": 78,
        "grade": "A-", "frameworks": ["CDP", "TCFD", "IFRS S1/S2", "GRI"],
        "targets": 5, "on_track": 4, "at_risk": 1, "lagging": 0
    },
    "Nexus Pharma": {
        "industry": "Pharmaceuticals", "country": "India", "revenue_bn": 1.3,
        "E_score": 55, "S_score": 78, "G_score": 71, "overall": 68,
        "grade": "B", "frameworks": ["GRI", "SASB"],
        "targets": 3, "on_track": 1, "at_risk": 1, "lagging": 1
    },
    "UrbanNest REIT": {
        "industry": "Real Estate", "country": "India", "revenue_bn": 0.8,
        "E_score": 79, "S_score": 66, "G_score": 84, "overall": 76,
        "grade": "A-", "frameworks": ["GRESB", "TCFD", "GRI"],
        "targets": 4, "on_track": 3, "at_risk": 1, "lagging": 0
    },
}


# ─── UTILITY FUNCTIONS ───────────────────────────────────────────────────────

def get_indicators(industry, pillar):
    ind = INDUSTRY_SPECIFIC_INDICATORS.get(industry, {})
    base = ind.get(pillar, DEFAULT_INDICATORS[pillar])
    default = DEFAULT_INDICATORS[pillar]
    merged = list(dict.fromkeys(base + default))
    return merged

def score_to_grade(score):
    if score >= 85: return "A+"
    if score >= 78: return "A"
    if score >= 72: return "A-"
    if score >= 65: return "B+"
    if score >= 58: return "B"
    if score >= 50: return "B-"
    if score >= 42: return "C+"
    if score >= 35: return "C"
    return "D"

def grade_color(grade):
    if grade.startswith("A"): return COLORS["mid"]
    if grade.startswith("B"): return "#4CAF80"
    if grade.startswith("C"): return "#F59E0B"
    return "#EF4444"

def validate_target(target_type, target_year, current_year=2024, base_year=2019):
    issues = []
    suggestions = []
    sbti_validated = False

    years_remaining = target_year - current_year
    years_elapsed = current_year - base_year

    if target_year < 2025:
        issues.append("⚠️ Target year has already passed or is too near-term.")
    if target_year > 2070:
        issues.append("⚠️ Target year is beyond 2070 — consider interim milestones.")

    if "Net Zero" in target_type or "Carbon Neutral" in target_type:
        if target_year <= 2050:
            sbti_validated = True
            suggestions.append("✅ Target year aligns with IPCC 1.5°C pathway (net zero by 2050).")
        else:
            issues.append("⚠️ Net zero beyond 2050 does not align with IPCC 1.5°C scenario.")
        suggestions.append("📋 Ensure Scope 1, 2, and 3 emissions are covered for SBTi validation.")

    elif "SBTi" in target_type:
        if target_year - current_year >= 5 and target_year - current_year <= 10:
            sbti_validated = True
            suggestions.append("✅ Near-term SBTi targets (5–10 years) are validated against 1.5°C.")
        else:
            issues.append("⚠️ SBTi near-term targets should be 5–10 years out.")

    elif "Renewable Energy" in target_type:
        if target_year <= 2035:
            suggestions.append("✅ Aligns with RE100 and IEA Net Zero by 2050 scenario.")
        else:
            issues.append("⚠️ 100% renewable by post-2035 lags IEA and RE100 recommendations.")

    elif "Water" in target_type:
        suggestions.append("📋 CDP Water Security framework recommends targets tied to watershed stress levels.")

    return issues, suggestions, sbti_validated

def generate_strategies(industry, pillar, indicator, current_val, target_val, unit=""):
    strategies = []
    gap = None
    if current_val is not None and target_val is not None:
        try:
            gap = float(target_val) - float(current_val)
        except:
            gap = None

    # Industry-specific strategies
    industry_strategies = {
        "Steel & Metals": {
            "E": [
                "Transition from blast furnace to electric arc furnace (EAF) — reduces CO₂ intensity by ~40%.",
                "Implement hydrogen-based direct reduced iron (DRI-H₂) pilot programmes.",
                "Increase scrap metal reuse rate through automated sorting and grading systems.",
                "Deploy heat recovery systems on casting lines; target ≥85% heat recovery.",
                "Join ResponsibleSteel certification for supply chain decarbonisation."
            ],
            "S": [
                "Install wet-bulb temperature monitoring stations across plant floors for heat stress prevention.",
                "Implement mandatory heat acclimatisation protocols per NIOSH standards.",
                "Conduct third-party contractor safety audits quarterly, not annually.",
            ],
            "G": [
                "Link 20–30% of executive variable pay to verified ESG milestones.",
                "Adopt GRI 207: Tax 2019 for full tax transparency reporting.",
            ]
        },
        "FMCG / Consumer Goods": {
            "E": [
                "Adopt extended producer responsibility (EPR) programmes for post-consumer packaging recovery.",
                "Switch to mono-material packaging (monomaterial PE or PP) to improve recyclability.",
                "Eliminate virgin plastic in secondary packaging by 2027 per Ellen MacArthur Foundation targets.",
                "Map Scope 3 Category 1 (purchased goods) emissions and engage top 20 suppliers.",
                "Shift transport fleet to EVs or biofuels; reduce logistics emissions per unit."
            ],
            "S": [
                "Conduct living wage assessments in Tier 1 and Tier 2 supply chains annually.",
                "Publish gender pay gap data disaggregated by level and function.",
            ],
            "G": [
                "Implement responsible marketing governance with third-party auditing.",
                "Adopt supplier code of conduct with mandatory ESG KPIs and annual disclosure.",
            ]
        },
    }

    generic_strategies = {
        "E": [
            "Conduct a granular energy audit (ISO 50001) to identify top 3 consumption hotspots.",
            "Sign long-term renewable energy PPAs or invest in on-site solar/wind to accelerate Scope 2 reduction.",
            "Engage Tier 1 and Tier 2 suppliers through CDP Supply Chain programme for Scope 3 data.",
            "Align capital expenditure with TCFD-recommended climate transition plans.",
            "Consider internal carbon pricing (shadow price) to shift investment decisions."
        ],
        "S": [
            "Publish a time-bound pay equity roadmap with transparent methodology (per GRI 405).",
            "Introduce mandatory mental health and wellbeing programmes per ISO 45003.",
            "Establish a community advisory panel for operations in high-impact geographies.",
        ],
        "G": [
            "Strengthen board-level ESG committee with independent sustainability expertise.",
            "Link executive remuneration to science-based emissions targets (per CDP-backed guidance).",
            "Enhance supplier ESG due diligence using OECD RBC guidelines.",
        ]
    }

    # Get industry-specific if available, otherwise generic
    ind_strat = industry_strategies.get(industry, {}).get(pillar, [])
    gen_strat = generic_strategies.get(pillar, [])

    strategies = (ind_strat + gen_strat)[:5]
    return strategies, gap

def make_gauge(value, title, color, max_val=100):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": title, "font": {"size": 13, "color": COLORS["text"], "family": "Inter"}},
        number={"font": {"size": 26, "color": color, "family": "Inter"}, "suffix": ""},
        gauge={
            "axis": {"range": [0, max_val], "tickwidth": 1, "tickcolor": COLORS["mist"]},
            "bar": {"color": color, "thickness": 0.65},
            "bgcolor": COLORS["foam"],
            "borderwidth": 0,
            "steps": [
                {"range": [0, 40], "color": "#FEE2E2"},
                {"range": [40, 65], "color": "#FEF3C7"},
                {"range": [65, 85], "color": "#DCFCE7"},
                {"range": [85, 100], "color": "#BBF7D0"}
            ],
        }
    ))
    fig.update_layout(
        height=180, margin=dict(t=40, b=10, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
    )
    return fig

def make_radar(e, s, g):
    categories = ["Environment", "Social", "Governance"]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=[e, s, g, e],
        theta=categories + [categories[0]],
        fill="toself",
        fillcolor=f"rgba(26,107,60,0.2)",
        line=dict(color=COLORS["mid"], width=2),
        name="ESG Score"
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=9), gridcolor=COLORS["mist"]),
            angularaxis=dict(tickfont=dict(size=11, color=COLORS["text"])),
            bgcolor="rgba(0,0,0,0)"
        ),
        showlegend=False,
        height=220,
        margin=dict(t=20, b=20, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig

def make_target_progress(target_name, current_pct, status):
    color = {"On Track": COLORS["mid"], "At Risk": "#F59E0B", "Lagging": "#EF4444"}.get(status, COLORS["mid"])
    fig = go.Figure(go.Bar(
        x=[current_pct], y=[target_name],
        orientation="h",
        marker=dict(color=color, line=dict(width=0)),
        width=0.5
    ))
    fig.add_shape(type="line", x0=100, x1=100, y0=-0.5, y1=0.5,
                  line=dict(color=COLORS["dark"], width=2, dash="dot"))
    fig.update_layout(
        xaxis=dict(range=[0, 110], ticksuffix="%", gridcolor=COLORS["foam"]),
        yaxis=dict(showticklabels=True),
        height=90, margin=dict(t=5, b=5, l=0, r=30),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
    )
    return fig


# ─── SIDEBAR ─────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
        <div style='text-align:center; padding: 12px 0 20px 0;'>
            <div style='font-size:2rem;'>🌿</div>
            <div style='font-size:1.15rem; font-weight:700; color:#DAF1DE; letter-spacing:-0.3px;'>ESG Compass</div>
            <div style='font-size:0.72rem; color:#A8D5B5; margin-top:2px;'>Multi-Framework ESG Intelligence</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='font-size:0.65rem; text-transform:uppercase; letter-spacing:1.5px; color:#A8D5B5; margin-bottom:6px;'>NAVIGATION</div>", unsafe_allow_html=True)

    page = st.radio("", [
        "🏠  Dashboard",
        "🏢  Company Setup",
        "📊  Data Input",
        "🎯  Targets",
        "📈  Analysis & Insights",
    ], label_visibility="collapsed")

    st.markdown("---")
    st.markdown("<div style='font-size:0.65rem; text-transform:uppercase; letter-spacing:1.5px; color:#A8D5B5; margin-bottom:6px;'>ACTIVE FRAMEWORKS</div>", unsafe_allow_html=True)
    for fw in FRAMEWORKS:
        st.markdown(f"<div style='font-size:0.78rem; color:#A8D5B5; padding:2px 0;'>✓ {fw}</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"<div style='font-size:0.72rem; color:#5A8A6A; text-align:center;'>v1.0 · Built for IPCC / SBTi · GRI · CDP · SASB · IFRS S1/S2 · S&P CSA · GRESB</div>", unsafe_allow_html=True)


# ─── SESSION STATE ────────────────────────────────────────────────────────────
if "companies" not in st.session_state:
    st.session_state.companies = dict(SAMPLE_COMPANIES)
if "current_company" not in st.session_state:
    st.session_state.current_company = None
if "esg_data" not in st.session_state:
    st.session_state.esg_data = {}
if "targets" not in st.session_state:
    st.session_state.targets = {}


# ════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ════════════════════════════════════════════════════════════
if "Dashboard" in page:
    st.markdown("""
        <div class='main-header'>
            <h1>🌿 ESG Compass — Dashboard</h1>
            <p>Multi-framework ESG performance intelligence · GRI · CDP · SASB · IFRS S1/S2 · S&P CSA · GRESB · SBTi aligned</p>
        </div>
    """, unsafe_allow_html=True)

    companies = st.session_state.companies

    # Summary metrics
    all_scores = [c["overall"] for c in companies.values()]
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class='metric-card'>
            <div class='value'>{len(companies)}</div>
            <div class='label'>Companies Tracked</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        avg = round(sum(all_scores) / len(all_scores), 1) if all_scores else 0
        st.markdown(f"""<div class='metric-card'>
            <div class='value'>{avg}</div>
            <div class='label'>Avg ESG Score</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        total_targets = sum(c["targets"] for c in companies.values())
        on_track = sum(c["on_track"] for c in companies.values())
        st.markdown(f"""<div class='metric-card'>
            <div class='value'>{on_track}/{total_targets}</div>
            <div class='label'>Targets On Track</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        a_count = sum(1 for c in companies.values() if c["grade"].startswith("A"))
        st.markdown(f"""<div class='metric-card'>
            <div class='value'>{a_count}</div>
            <div class='label'>A-Grade Companies</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Company table
    st.markdown("<div class='section-label'>ALL COMPANIES</div>", unsafe_allow_html=True)
    selected_company = None

    for name, data in companies.items():
        grade_col = grade_color(data["grade"])
        e_bar = f"width:{data['E_score']}%; background:{COLORS['mid']};"
        s_bar = f"width:{data['S_score']}%; background:#4CAF80;"
        g_bar = f"width:{data['G_score']}%; background:#A8D5B5;"

        frameworks_html = " ".join([f"<span class='framework-badge'>{fw}</span>" for fw in data.get("frameworks", [])])

        on_pct = round(data["on_track"] / data["targets"] * 100) if data["targets"] else 0
        target_status = "🟢 On Track" if on_pct >= 67 else ("🟡 Mixed" if on_pct >= 34 else "🔴 Lagging")

        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"""
            <div class='esg-card' style='cursor:pointer;'>
                <div style='display:flex; align-items:center; gap:12px; margin-bottom:10px;'>
                    <div style='font-size:1.05rem; font-weight:700; color:{COLORS["text"]};'>{name}</div>
                    <div style='background:{grade_col}; color:white; border-radius:6px; padding:2px 10px; font-size:0.8rem; font-weight:700;'>{data["grade"]}</div>
                    <div style='font-size:0.8rem; color:{COLORS["subtle"]};'>{data["industry"]} · {data["country"]}</div>
                    <div style='margin-left:auto; font-size:0.8rem;'>{target_status}</div>
                </div>
                <div style='display:grid; grid-template-columns:1fr 1fr 1fr; gap:8px; margin-bottom:10px;'>
                    <div>
                        <div style='font-size:0.7rem; color:{COLORS["subtle"]}; margin-bottom:3px;'>E — {data["E_score"]}</div>
                        <div style='background:{COLORS["foam"]}; border-radius:4px; height:7px;'><div style='{e_bar} height:7px; border-radius:4px;'></div></div>
                    </div>
                    <div>
                        <div style='font-size:0.7rem; color:{COLORS["subtle"]}; margin-bottom:3px;'>S — {data["S_score"]}</div>
                        <div style='background:{COLORS["foam"]}; border-radius:4px; height:7px;'><div style='{s_bar} height:7px; border-radius:4px;'></div></div>
                    </div>
                    <div>
                        <div style='font-size:0.7rem; color:{COLORS["subtle"]}; margin-bottom:3px;'>G — {data["G_score"]}</div>
                        <div style='background:{COLORS["foam"]}; border-radius:4px; height:7px;'><div style='{g_bar} height:7px; border-radius:4px;'></div></div>
                    </div>
                </div>
                <div>{frameworks_html}</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            if st.button(f"View Details", key=f"view_{name}"):
                st.session_state.current_company = name
                st.rerun()

    # Scatter chart: E score vs S score, sized by overall
    st.markdown("<div class='section-label' style='margin-top:24px;'>ESG LANDSCAPE · ENVIRONMENT vs SOCIAL</div>", unsafe_allow_html=True)
    df_plot = pd.DataFrame([
        {"Company": k, "E Score": v["E_score"], "S Score": v["S_score"],
         "Overall": v["overall"], "Industry": v["industry"]}
        for k, v in companies.items()
    ])
    fig_scatter = px.scatter(df_plot, x="E Score", y="S Score", size="Overall",
                             color="Industry", hover_name="Company",
                             size_max=40, color_discrete_sequence=[
                                 COLORS["mid"], "#4CAF80", COLORS["mist"], "#1A6B3C", "#A8D5B5"
                             ])
    fig_scatter.update_layout(
        height=320, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=COLORS["bg"],
        xaxis=dict(range=[40, 100], gridcolor=COLORS["foam"]),
        yaxis=dict(range=[55, 90], gridcolor=COLORS["foam"]),
        margin=dict(t=20, b=40, l=40, r=20), font=dict(family="Inter")
    )
    st.plotly_chart(fig_scatter, use_container_width=True)


# ════════════════════════════════════════════════════════════
# PAGE: COMPANY SETUP
# ════════════════════════════════════════════════════════════
elif "Company Setup" in page:
    st.markdown("""
        <div class='main-header'>
            <h1>🏢 Company Setup</h1>
            <p>Register your company and configure its profile for ESG benchmarking</p>
        </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["➕ New Company", "📋 Existing Companies"])

    with tab1:
        st.markdown("<div class='esg-card'>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            company_name = st.text_input("Company Name *", placeholder="e.g. TerraSteel Ltd")
            industry = st.selectbox("Industry *", INDUSTRIES)
            country = st.text_input("Country", placeholder="e.g. India")
            revenue = st.number_input("Annual Revenue (USD Billion)", min_value=0.0, step=0.1)
        with col2:
            report_year = st.selectbox("Reporting Year", [2024, 2023, 2022, 2021])
            employees = st.number_input("Total Employees", min_value=0, step=100)
            headquarters = st.text_input("Headquarters City")
            selected_frameworks = st.multiselect("Reporting Frameworks", FRAMEWORKS, default=["GRI", "CDP"])

        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("Register Company →"):
            if company_name:
                st.session_state.companies[company_name] = {
                    "industry": industry, "country": country, "revenue_bn": revenue,
                    "E_score": 0, "S_score": 0, "G_score": 0, "overall": 0,
                    "grade": "—", "frameworks": selected_frameworks,
                    "targets": 0, "on_track": 0, "at_risk": 0, "lagging": 0,
                    "employees": employees, "report_year": report_year
                }
                st.session_state.current_company = company_name
                st.success(f"✅ {company_name} registered successfully! Proceed to Data Input.")
            else:
                st.error("Company name is required.")

    with tab2:
        for name, data in st.session_state.companies.items():
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"**{name}** · {data['industry']} · {data['country']}")
            with col2:
                grade_col = grade_color(data["grade"])
                st.markdown(f"<span style='background:{grade_col}; color:white; border-radius:5px; padding:2px 8px; font-size:0.8rem;'>{data['grade']}</span>", unsafe_allow_html=True)
            with col3:
                if st.button("Select", key=f"sel_{name}"):
                    st.session_state.current_company = name
                    st.success(f"Active company: {name}")


# ════════════════════════════════════════════════════════════
# PAGE: DATA INPUT
# ════════════════════════════════════════════════════════════
elif "Data Input" in page:
    st.markdown("""
        <div class='main-header'>
            <h1>📊 ESG Data Input</h1>
            <p>Enter your ESG performance data — aligned with GRI, SASB, CDP, IFRS S1/S2, S&P CSA, GRESB</p>
        </div>
    """, unsafe_allow_html=True)

    companies_list = list(st.session_state.companies.keys())
    default_idx = companies_list.index(st.session_state.current_company) if st.session_state.current_company in companies_list else 0
    active_company = st.selectbox("Active Company", companies_list, index=default_idx)
    st.session_state.current_company = active_company
    company_data = st.session_state.companies.get(active_company, {})
    industry = company_data.get("industry", INDUSTRIES[0])

    st.markdown(f"""
        <div class='esg-card' style='margin-bottom:16px;'>
            <div style='display:flex; gap:12px; align-items:center;'>
                <div style='font-weight:600;'>{active_company}</div>
                <div style='color:{COLORS["subtle"]}; font-size:0.85rem;'>{industry}</div>
                {''.join(f"<span class='framework-badge'>{fw}</span>" for fw in company_data.get('frameworks', []))}
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Excel upload
    st.markdown("<div class='section-label'>UPLOAD DATA (EXCEL TEMPLATE)</div>", unsafe_allow_html=True)
    
    col_up, col_dl = st.columns([2, 1])
    with col_dl:
        # Generate template
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            for pillar, pname in [("E", "Environmental"), ("S", "Social"), ("G", "Governance")]:
                indicators = get_indicators(industry, pillar)
                df_template = pd.DataFrame({
                    "Indicator": indicators,
                    "Unit": ["—"] * len(indicators),
                    "Current Year Value": [""] * len(indicators),
                    "Prior Year Value": [""] * len(indicators),
                    "Methodology / Notes": [""] * len(indicators),
                    "GRI Disclosure Ref": [""] * len(indicators),
                    "SASB Ref": [""] * len(indicators),
                })
                df_template.to_excel(writer, sheet_name=pname, index=False)
        output.seek(0)
        st.download_button(
            "⬇️ Download Template",
            data=output,
            file_name=f"ESG_Template_{active_company.replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    with col_up:
        uploaded_file = st.file_uploader("Upload completed template (.xlsx)", type=["xlsx"])
        if uploaded_file:
            try:
                xl = pd.read_excel(uploaded_file, sheet_name=None)
                parsed_data = {}
                for sheet_name, df in xl.items():
                    pillar = sheet_name[0]  # E, S, G from sheet name
                    if "Indicator" in df.columns and "Current Year Value" in df.columns:
                        parsed_data[sheet_name] = df
                st.session_state.esg_data[active_company] = parsed_data
                st.success(f"✅ Data uploaded for {active_company}!")
            except Exception as e:
                st.error(f"Error reading file: {e}")

    st.markdown("---")
    st.markdown("<div class='section-label'>OR ENTER DATA MANUALLY</div>", unsafe_allow_html=True)

    tab_e, tab_s, tab_g = st.tabs(["🌍 Environmental", "👥 Social", "🏛️ Governance"])

    if active_company not in st.session_state.esg_data:
        st.session_state.esg_data[active_company] = {}

    def render_data_tab(pillar, tab_name, icon):
        indicators = get_indicators(industry, pillar)
        if tab_name not in st.session_state.esg_data[active_company]:
            st.session_state.esg_data[active_company][tab_name] = {}

        scores = []
        for i, indicator in enumerate(indicators):
            col1, col2, col3 = st.columns([3, 1.5, 1.5])
            with col1:
                st.markdown(f"<div style='font-size:0.88rem; font-weight:500; padding-top:8px;'>{indicator}</div>", unsafe_allow_html=True)
            with col2:
                val = st.number_input("Current", key=f"{pillar}_{i}_cur", label_visibility="collapsed",
                                      value=float(st.session_state.esg_data[active_company][tab_name].get(indicator, {}).get("current", 0) or 0))
            with col3:
                val_prev = st.number_input("Prior", key=f"{pillar}_{i}_prev", label_visibility="collapsed",
                                           value=float(st.session_state.esg_data[active_company][tab_name].get(indicator, {}).get("prior", 0) or 0))
            st.session_state.esg_data[active_company][tab_name][indicator] = {"current": val, "prior": val_prev}
            if val > 0:
                scores.append(min(100, round(val)))

        return scores

    with tab_e:
        st.markdown(f"<div style='font-size:0.75rem; color:{COLORS['subtle']}; margin-bottom:12px;'>Industry-specific indicators for <b>{industry}</b> · GRI 300 series · CDP Climate/Water/Forests · IFRS S2</div>", unsafe_allow_html=True)
        col_h1, col_h2, col_h3 = st.columns([3, 1.5, 1.5])
        col_h1.markdown("<div class='section-label'>INDICATOR</div>", unsafe_allow_html=True)
        col_h2.markdown("<div class='section-label'>CURRENT YEAR</div>", unsafe_allow_html=True)
        col_h3.markdown("<div class='section-label'>PRIOR YEAR</div>", unsafe_allow_html=True)
        render_data_tab("E", "Environmental", "🌍")

    with tab_s:
        st.markdown(f"<div style='font-size:0.75rem; color:{COLORS['subtle']}; margin-bottom:12px;'>GRI 400 series · SASB Social Capital · S&P CSA · IFRS S1</div>", unsafe_allow_html=True)
        col_h1, col_h2, col_h3 = st.columns([3, 1.5, 1.5])
        col_h1.markdown("<div class='section-label'>INDICATOR</div>", unsafe_allow_html=True)
        col_h2.markdown("<div class='section-label'>CURRENT YEAR</div>", unsafe_allow_html=True)
        col_h3.markdown("<div class='section-label'>PRIOR YEAR</div>", unsafe_allow_html=True)
        render_data_tab("S", "Social", "👥")

    with tab_g:
        st.markdown(f"<div style='font-size:0.75rem; color:{COLORS['subtle']}; margin-bottom:12px;'>GRI 200 series · SASB Leadership & Governance · S&P CSA · GRESB</div>", unsafe_allow_html=True)
        col_h1, col_h2, col_h3 = st.columns([3, 1.5, 1.5])
        col_h1.markdown("<div class='section-label'>INDICATOR</div>", unsafe_allow_html=True)
        col_h2.markdown("<div class='section-label'>CURRENT YEAR</div>", unsafe_allow_html=True)
        col_h3.markdown("<div class='section-label'>PRIOR YEAR</div>", unsafe_allow_html=True)
        render_data_tab("G", "Governance", "🏛️")

    if st.button("💾 Save Data & Calculate Scores"):
        # Simple scoring: % of indicators filled with non-zero values
        filled_e = sum(1 for v in st.session_state.esg_data[active_company].get("Environmental", {}).values() if v.get("current", 0))
        filled_s = sum(1 for v in st.session_state.esg_data[active_company].get("Social", {}).values() if v.get("current", 0))
        filled_g = sum(1 for v in st.session_state.esg_data[active_company].get("Governance", {}).values() if v.get("current", 0))

        total_e = len(get_indicators(industry, "E"))
        total_s = len(get_indicators(industry, "S"))
        total_g = len(get_indicators(industry, "G"))

        e_score = min(95, 30 + round((filled_e / max(total_e, 1)) * 65))
        s_score = min(95, 30 + round((filled_s / max(total_s, 1)) * 65))
        g_score = min(95, 30 + round((filled_g / max(total_g, 1)) * 65))
        overall = round((e_score + s_score + g_score) / 3)

        st.session_state.companies[active_company].update({
            "E_score": e_score, "S_score": s_score, "G_score": g_score,
            "overall": overall, "grade": score_to_grade(overall)
        })
        st.success(f"✅ Scores updated — E: {e_score} | S: {s_score} | G: {g_score} | Overall: {overall} ({score_to_grade(overall)})")


# ════════════════════════════════════════════════════════════
# PAGE: TARGETS
# ════════════════════════════════════════════════════════════
elif "Targets" in page:
    st.markdown("""
        <div class='main-header'>
            <h1>🎯 ESG Targets</h1>
            <p>Set, validate, and track your sustainability commitments — SBTi · IPCC · CDP · RE100 aligned</p>
        </div>
    """, unsafe_allow_html=True)

    companies_list = list(st.session_state.companies.keys())
    default_idx = companies_list.index(st.session_state.current_company) if st.session_state.current_company in companies_list else 0
    active_company = st.selectbox("Active Company", companies_list, index=default_idx)
    st.session_state.current_company = active_company
    company_data = st.session_state.companies.get(active_company, {})
    industry = company_data.get("industry", INDUSTRIES[0])

    if active_company not in st.session_state.targets:
        st.session_state.targets[active_company] = []

    # Add target form
    st.markdown("<div class='section-label'>ADD NEW TARGET</div>", unsafe_allow_html=True)
    with st.expander("➕ Add Target", expanded=len(st.session_state.targets[active_company]) == 0):
        col1, col2, col3 = st.columns(3)
        with col1:
            t_name = st.text_input("Target Name *", placeholder="e.g. Net Zero Operations")
            t_category = st.selectbox("Category", TARGET_CATEGORIES)
            t_pillar = st.selectbox("ESG Pillar", ["E — Environmental", "S — Social", "G — Governance"])
        with col2:
            t_indicator = st.text_input("KPI / Indicator", placeholder="e.g. Scope 1+2 emissions (tCO2e)")
            t_baseline = st.number_input("Baseline Value", step=0.01)
            t_baseline_year = st.selectbox("Baseline Year", [2019, 2020, 2021, 2022, 2023])
        with col3:
            t_target_val = st.number_input("Target Value", step=0.01)
            t_target_year = st.number_input("Target Year", min_value=2025, max_value=2070, value=2035, step=1)
            t_current_val = st.number_input("Current Achievement", step=0.01)

        t_sbti = st.checkbox("Submit for SBTi-style validation")
        t_notes = st.text_area("Notes / Scope clarification", height=60)

        if st.button("Validate & Add Target →"):
            issues, suggestions, sbti_ok = validate_target(t_category, int(t_target_year))

            # Calculate progress %
            if t_baseline != t_target_val and t_baseline != 0:
                progress_pct = round(abs((t_current_val - t_baseline) / (t_target_val - t_baseline)) * 100, 1)
            else:
                progress_pct = 0

            years_remaining = int(t_target_year) - 2024
            expected_pct = round(((2024 - t_baseline_year) / max(1, int(t_target_year) - t_baseline_year)) * 100, 1)
            status = "On Track" if progress_pct >= expected_pct * 0.9 else ("At Risk" if progress_pct >= expected_pct * 0.5 else "Lagging")

            target_entry = {
                "name": t_name, "category": t_category, "pillar": t_pillar[0],
                "indicator": t_indicator, "baseline": t_baseline, "baseline_year": t_baseline_year,
                "target_val": t_target_val, "target_year": int(t_target_year),
                "current": t_current_val, "progress_pct": progress_pct,
                "status": status, "sbti_validated": sbti_ok,
                "issues": issues, "suggestions": suggestions, "notes": t_notes
            }
            st.session_state.targets[active_company].append(target_entry)

            # Update company counts
            all_t = st.session_state.targets[active_company]
            st.session_state.companies[active_company]["targets"] = len(all_t)
            st.session_state.companies[active_company]["on_track"] = sum(1 for t in all_t if t["status"] == "On Track")
            st.session_state.companies[active_company]["at_risk"] = sum(1 for t in all_t if t["status"] == "At Risk")
            st.session_state.companies[active_company]["lagging"] = sum(1 for t in all_t if t["status"] == "Lagging")

            if issues:
                for iss in issues:
                    st.warning(iss)
            for sug in suggestions:
                st.info(sug)
            if sbti_ok:
                st.success("✅ Target validated — aligned with SBTi / IPCC 1.5°C pathway.")
            st.success(f"Target '{t_name}' added · Status: {status} · Progress: {progress_pct}%")

    # Show existing targets
    targets = st.session_state.targets.get(active_company, [])
    if targets:
        st.markdown(f"<div class='section-label' style='margin-top:20px;'>TARGETS ({len(targets)})</div>", unsafe_allow_html=True)
        for i, t in enumerate(targets):
            status_class = {"On Track": "target-on-track", "At Risk": "target-at-risk", "Lagging": "target-lagging"}.get(t["status"], "")
            sbti_badge = "<span style='background:#1A6B3C; color:white; border-radius:4px; padding:2px 7px; font-size:0.7rem; font-weight:600; margin-left:6px;'>SBTi ✓</span>" if t.get("sbti_validated") else ""

            with st.expander(f"{'🟢' if t['status']=='On Track' else '🟡' if t['status']=='At Risk' else '🔴'} {t['name']} — {t['category']} · {t['target_year']}"):
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    st.markdown(f"""
                        <div>
                            <div style='font-size:0.85rem; color:{COLORS["subtle"]}; margin-bottom:4px;'>{t["indicator"]}</div>
                            <div style='font-size:0.85rem;'>Baseline: <b>{t["baseline"]}</b> ({t["baseline_year"]}) → Target: <b>{t["target_val"]}</b> ({t["target_year"]})</div>
                            <div style='font-size:0.85rem; margin-top:4px;'>Current: <b>{t["current"]}</b> &nbsp;|&nbsp; Progress: <b>{t["progress_pct"]}%</b></div>
                        </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.plotly_chart(make_target_progress(t["name"], t["progress_pct"], t["status"]), use_container_width=True)
                with col3:
                    st.markdown(f"<br><span class='{status_class}'>{t['status']}</span>{sbti_badge}", unsafe_allow_html=True)

                if t.get("suggestions"):
                    for s in t["suggestions"]:
                        st.markdown(f"<div class='alert-success'>{s}</div>", unsafe_allow_html=True)
                if t.get("issues"):
                    for iss in t["issues"]:
                        st.markdown(f"<div class='alert-warning'>{iss}</div>", unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class='esg-card' style='text-align:center; padding:40px; color:#5A8A6A;'>
                <div style='font-size:2rem; margin-bottom:8px;'>🎯</div>
                <div style='font-weight:600;'>No targets set yet</div>
                <div style='font-size:0.85rem; margin-top:4px;'>Use the form above to add your first sustainability target.</div>
            </div>
        """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# PAGE: ANALYSIS & INSIGHTS
# ════════════════════════════════════════════════════════════
elif "Analysis" in page:
    st.markdown("""
        <div class='main-header'>
            <h1>📈 Analysis & Insights</h1>
            <p>Tailored strategies, gap analysis, SDG alignment, and peer benchmarking</p>
        </div>
    """, unsafe_allow_html=True)

    companies_list = list(st.session_state.companies.keys())
    default_idx = companies_list.index(st.session_state.current_company) if st.session_state.current_company in companies_list else 0
    active_company = st.selectbox("Active Company", companies_list, index=default_idx)
    st.session_state.current_company = active_company
    company_data = st.session_state.companies.get(active_company, {})
    industry = company_data.get("industry", INDUSTRIES[0])

    e_score = company_data.get("E_score", 0)
    s_score = company_data.get("S_score", 0)
    g_score = company_data.get("G_score", 0)
    overall = company_data.get("overall", 0)
    grade = company_data.get("grade", "—")

    # Score overview
    st.markdown("<div class='section-label'>ESG COMPASS SCORE</div>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns([1.5, 1, 1, 1])

    with col1:
        st.plotly_chart(make_radar(e_score or 60, s_score or 65, g_score or 70), use_container_width=True)
    with col2:
        gc = grade_color(grade)
        st.markdown(f"""
            <div class='metric-card'>
                <div class='value' style='color:{gc};'>{grade}</div>
                <div class='label'>Overall Grade</div>
                <div style='font-size:1.4rem; font-weight:700; color:{COLORS["mid"]}; margin-top:6px;'>{overall}</div>
                <div style='font-size:0.72rem; color:{COLORS["subtle"]};'>/ 100</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.plotly_chart(make_gauge(e_score or 60, "Environment", COLORS["mid"]), use_container_width=True)
    with col4:
        st.plotly_chart(make_gauge(s_score or 65, "Social", "#4CAF80"), use_container_width=True)

    # Framework alignment
    st.markdown("<div class='section-label' style='margin-top:12px;'>FRAMEWORK ALIGNMENT</div>", unsafe_allow_html=True)
    fw_scores = {
        "GRI": min(100, (e_score + s_score + g_score) // 3 + 5),
        "CDP": min(100, e_score + 3),
        "SASB": min(100, (e_score + g_score) // 2 + 4),
        "IFRS S1/S2": min(100, e_score - 3),
        "S&P CSA": min(100, overall + 2),
        "GRESB": min(100, (e_score + g_score) // 2),
        "SBTi": min(100, e_score - 8),
    }
    fw_df = pd.DataFrame(list(fw_scores.items()), columns=["Framework", "Alignment Score"])
    fig_fw = px.bar(fw_df, x="Framework", y="Alignment Score",
                    color="Alignment Score",
                    color_continuous_scale=[[0, "#FEE2E2"], [0.4, "#FEF3C7"], [0.7, "#DCFCE7"], [1, COLORS["mid"]]],
                    range_color=[0, 100])
    fig_fw.update_layout(height=220, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                         showlegend=False, margin=dict(t=10, b=40, l=10, r=10),
                         yaxis=dict(range=[0, 105], gridcolor=COLORS["foam"]),
                         coloraxis_showscale=False)
    st.plotly_chart(fig_fw, use_container_width=True)

    # SDG Mapping
    st.markdown("<div class='section-label' style='margin-top:8px;'>SDG ALIGNMENT</div>", unsafe_allow_html=True)
    relevant_sdgs = INDUSTRY_SDGS.get(industry, [13, 12, 6, 8, 9])
    sdg_html = ""
    for sdg_num in relevant_sdgs:
        color = SDG_COLORS.get(sdg_num, "#999")
        name = SDG_NAMES.get(sdg_num, f"SDG {sdg_num}")
        sdg_html += f"<span class='sdg-chip' style='background:{color};'>SDG {sdg_num}: {name}</span>"
    st.markdown(f"<div style='margin-bottom:16px;'>{sdg_html}</div>", unsafe_allow_html=True)

    # SDG detail
    with st.expander("📌 SDG Impact Mapping Detail"):
        for sdg_num in relevant_sdgs:
            color = SDG_COLORS.get(sdg_num, "#999")
            name = SDG_NAMES.get(sdg_num, "")
            sdg_targets = {
                13: "Targets 13.1, 13.2, 13.3 — Climate action, TCFD disclosure, GHG reduction",
                12: "Targets 12.2, 12.4, 12.5 — Sustainable consumption, chemical management, waste reduction",
                6:  "Targets 6.3, 6.4 — Water quality, water use efficiency",
                8:  "Targets 8.5, 8.7, 8.8 — Decent work, forced labour, occupational safety",
                9:  "Targets 9.4 — Cleaner industrial processes, innovation",
                15: "Targets 15.1, 15.5 — Biodiversity, ecosystem conservation",
                7:  "Targets 7.2, 7.3 — Renewable energy, energy efficiency",
                11: "Targets 11.3, 11.6 — Inclusive urbanisation, air quality",
            }
            detail = sdg_targets.get(sdg_num, f"Relevant SDG targets for SDG {sdg_num}")
            st.markdown(f"""
                <div style='display:flex; align-items:flex-start; gap:12px; padding:8px 0; border-bottom:1px solid {COLORS["foam"]};'>
                    <span class='sdg-chip' style='background:{color}; white-space:nowrap;'>SDG {sdg_num}</span>
                    <div>
                        <div style='font-weight:600; font-size:0.85rem;'>{name}</div>
                        <div style='font-size:0.8rem; color:{COLORS["subtle"]};'>{detail}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    # Target gap analysis
    targets = st.session_state.targets.get(active_company, [])
    if targets:
        st.markdown("<div class='section-label' style='margin-top:20px;'>TARGET GAP ANALYSIS</div>", unsafe_allow_html=True)
        for t in targets:
            strats, gap = generate_strategies(industry, t.get("pillar", "E"), t.get("indicator", ""), t.get("current"), t.get("target_val"))
            status_color = {"On Track": "#15803D", "At Risk": "#B45309", "Lagging": "#B91C1C"}.get(t["status"], COLORS["mid"])

            with st.expander(f"{'🟢' if t['status']=='On Track' else '🟡' if t['status']=='At Risk' else '🔴'}  {t['name']} — {t['progress_pct']}% complete"):
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.markdown(f"""
                        <div class='metric-card'>
                            <div class='value' style='color:{status_color};'>{t["progress_pct"]}%</div>
                            <div class='label'>Progress</div>
                            <div style='font-size:0.8rem; color:{COLORS["subtle"]}; margin-top:6px;'>{t["status"]}</div>
                            <div style='font-size:0.75rem; color:{COLORS["subtle"]}; margin-top:2px;'>{2024} of {t["target_year"]}</div>
                        </div>
                    """, unsafe_allow_html=True)

                with col2:
                    if gap is not None:
                        st.markdown(f"<div style='font-size:0.85rem; margin-bottom:8px;'>Gap to close: <b>{abs(gap):.1f}</b> units from current {t['current']} to target {t['target_val']}</div>", unsafe_allow_html=True)

                    st.markdown("<div class='section-label'>RECOMMENDED STRATEGIES</div>", unsafe_allow_html=True)
                    for j, strat in enumerate(strats, 1):
                        st.markdown(f"<div class='strategy-box'><b>{j}.</b> {strat}</div>", unsafe_allow_html=True)

    # Peer benchmarking
    st.markdown("<div class='section-label' style='margin-top:24px;'>INDUSTRY PEER BENCHMARKING</div>", unsafe_allow_html=True)
    peer_companies = {k: v for k, v in st.session_state.companies.items() if v.get("industry") == industry}
    if len(peer_companies) > 1:
        fig_peer = go.Figure()
        for cname, cdata in peer_companies.items():
            color = COLORS["mid"] if cname == active_company else COLORS["mist"]
            width = 3 if cname == active_company else 1.5
            fig_peer.add_trace(go.Scatterpolar(
                r=[cdata["E_score"], cdata["S_score"], cdata["G_score"], cdata["E_score"]],
                theta=["Environment", "Social", "Governance", "Environment"],
                name=cname,
                line=dict(color=color, width=width),
                fill="toself" if cname == active_company else None,
                fillcolor=f"rgba(26,107,60,0.15)" if cname == active_company else None
            ))
        fig_peer.update_layout(
            polar=dict(radialaxis=dict(range=[0, 100], gridcolor=COLORS["mist"])),
            height=300, paper_bgcolor="rgba(0,0,0,0)", margin=dict(t=30, b=10)
        )
        st.plotly_chart(fig_peer, use_container_width=True)
    else:
        st.info("Add more companies in the same industry to enable peer benchmarking.")

    # Industry-specific improvement tips
    st.markdown("<div class='section-label' style='margin-top:16px;'>INDUSTRY-SPECIFIC IMPROVEMENT ROADMAP</div>", unsafe_allow_html=True)

    road_tips = {
        "Steel & Metals": [
            ("🔥 Transition to EAF + Green Hydrogen", "Electric Arc Furnaces using green H₂ can reduce steelmaking CO₂ by up to 95%. Align with ResponsibleSteel standard."),
            ("♻️ Closed-Loop Scrap Strategy", "Target >85% scrap recovery. Implement automated sorting and partner with urban miners for end-of-life metal recovery."),
            ("🌡️ Heat Stress Protocol", "Deploy wet-bulb globe temperature (WBGT) monitoring per ISO 7933. Mandatory NIOSH acclimatisation schedules."),
        ],
        "FMCG / Consumer Goods": [
            ("📦 Packaging Circularity", "Adopt monomaterial design for all primary packaging by 2027. Partner with PROs under EPR regulations."),
            ("🌾 Regenerative Sourcing", "Implement regenerative agriculture criteria for top 5 raw material categories (palm, soy, cocoa, paper, dairy)."),
            ("🤝 Supply Chain Living Wage", "Conduct gap analysis in Tier 1 suppliers vs ILO living wage benchmarks. Publish corrective action timelines."),
        ],
    }

    default_road = [
        ("🌡️ Climate Transition Plan", "Develop a TCFD-aligned transition plan with 1.5°C scenario modelling. Submit Scope 1+2 to SBTi by 2025."),
        ("💧 Water Stewardship", "Conduct facility-level water risk assessment using WRI Aqueduct. Set context-based water targets for high-stress sites."),
        ("🏛️ ESG Governance", "Establish a board-level Sustainability Committee. Link 20%+ of executive remuneration to verified ESG milestones."),
    ]

    tips = road_tips.get(industry, default_road)
    for title, body in tips:
        st.markdown(f"""
            <div class='strategy-box'>
                <div style='font-weight:600; font-size:0.9rem; margin-bottom:4px;'>{title}</div>
                <div style='font-size:0.84rem; color:{COLORS["text"]};'>{body}</div>
            </div>
        """, unsafe_allow_html=True)
