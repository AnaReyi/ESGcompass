import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json, io, math
from datetime import datetime

CURRENT_YEAR = datetime.now().year

st.set_page_config(page_title="ESG Compass", page_icon="🌿", layout="wide", initial_sidebar_state="expanded")

# ─── PALETTE ────────────────────────────────────────────────────────────────
C = {"deep":"#0D2B1A","dark":"#0D3D26","mid":"#1A6B3C","leaf":"#2E8B57",
     "mist":"#A8D5B5","foam":"#DAF1DE","bg":"#F0FAF2","white":"#FFFFFF",
     "text":"#1A2E1F","subtle":"#5A8A6A"}

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html,body,[class*="css"]{{font-family:'Inter',sans-serif;background:{C['bg']};color:{C['text']};}}
section[data-testid="stSidebar"]{{background:linear-gradient(180deg,{C['dark']} 0%,{C['deep']} 100%);}}
section[data-testid="stSidebar"] *{{color:{C['foam']} !important;}}
section[data-testid="stSidebar"] .stRadio label{{color:{C['mist']} !important;font-size:.9rem;}}
.main-header{{background:linear-gradient(135deg,{C['dark']} 0%,{C['mid']} 100%);border-radius:16px;padding:28px 36px;margin-bottom:24px;}}
.main-header h1{{color:white;font-size:2rem;font-weight:700;margin:0 0 4px 0;}}
.main-header p{{color:{C['mist']};margin:0;font-size:.95rem;}}
.esg-card{{background:white;border-radius:14px;padding:20px 24px;box-shadow:0 2px 12px rgba(13,61,38,.08);border:1px solid {C['foam']};margin-bottom:16px;}}
.metric-card{{background:linear-gradient(135deg,{C['foam']} 0%,white 100%);border-radius:14px;padding:20px;text-align:center;border:1px solid {C['mist']};}}
.metric-card .value{{font-size:2rem;font-weight:700;color:{C['mid']};}}
.metric-card .label{{font-size:.8rem;color:{C['subtle']};text-transform:uppercase;letter-spacing:.5px;margin-top:4px;}}
.section-label{{font-size:.7rem;text-transform:uppercase;letter-spacing:1.5px;color:{C['subtle']};font-weight:600;margin-bottom:8px;}}
.framework-badge{{display:inline-block;background:{C['foam']};color:{C['mid']};border:1px solid {C['mist']};border-radius:6px;padding:2px 8px;font-size:.72rem;font-weight:500;margin:2px;}}
.sdg-chip{{display:inline-block;border-radius:8px;padding:4px 10px;font-size:.75rem;font-weight:600;margin:2px;color:white;}}
.strategy-box{{background:linear-gradient(135deg,{C['foam']} 0%,#E8F5EC 100%);border-left:4px solid {C['leaf']};border-radius:0 12px 12px 0;padding:14px 18px;margin:8px 0;}}
.alert-warning{{background:#FFFBEB;border-left:4px solid #F59E0B;border-radius:0 8px 8px 0;padding:12px 16px;margin:8px 0;font-size:.88rem;}}
.alert-success{{background:#F0FDF4;border-left:4px solid #22C55E;border-radius:0 8px 8px 0;padding:12px 16px;margin:8px 0;font-size:.88rem;}}
.alert-error{{background:#FEF2F2;border-left:4px solid #EF4444;border-radius:0 8px 8px 0;padding:12px 16px;margin:8px 0;font-size:.88rem;}}
.gap-positive{{color:#15803D;font-weight:600;}}
.gap-negative{{color:#B91C1C;font-weight:600;}}
.stTabs [data-baseweb="tab-list"]{{background:{C['foam']};border-radius:10px;padding:4px;gap:2px;}}
.stTabs [data-baseweb="tab"]{{border-radius:8px;color:{C['subtle']};font-weight:500;}}
.stTabs [aria-selected="true"]{{background:white !important;color:{C['mid']} !important;}}
.stButton>button{{background:linear-gradient(135deg,{C['mid']} 0%,{C['dark']} 100%);color:white;border:none;border-radius:8px;font-weight:600;padding:8px 20px;}}
.stButton>button:hover{{background:linear-gradient(135deg,{C['leaf']} 0%,{C['mid']} 100%);transform:translateY(-1px);}}
div[data-testid="stExpander"]{{background:white;border:1px solid {C['foam']};border-radius:12px;}}
.dq-badge-assured{{background:#DCFCE7;color:#15803D;border-radius:20px;padding:3px 12px;font-size:.78rem;font-weight:600;}}
.dq-badge-unassured{{background:#FEF3C7;color:#B45309;border-radius:20px;padding:3px 12px;font-size:.78rem;font-weight:600;}}
.dq-badge-partial{{background:#FEE2E2;color:#B91C1C;border-radius:20px;padding:3px 12px;font-size:.78rem;font-weight:600;}}
</style>""", unsafe_allow_html=True)

# ─── CONSTANTS ───────────────────────────────────────────────────────────────
INDUSTRIES = ["Steel & Metals","FMCG / Consumer Goods","Energy & Utilities","Real Estate",
               "Financial Services","Technology & IT","Pharmaceuticals","Chemicals",
               "Automotive","Agriculture & Food","Textiles & Apparel","Cement & Construction"]

FRAMEWORKS = ["GRI","SASB","CDP","TCFD","IFRS S1/S2","S&P CSA","GRESB","SBTi/IPCC"]

SDG_COLORS = {1:"#E5243B",2:"#DDA63A",3:"#4C9F38",4:"#C5192D",5:"#FF3A21",6:"#26BDE2",
              7:"#FCC30B",8:"#A21942",9:"#FD6925",10:"#DD1367",11:"#FD9D24",12:"#BF8B2E",
              13:"#3F7E44",14:"#0A97D9",15:"#56C02B",16:"#00689D",17:"#19486A"}
SDG_NAMES = {1:"No Poverty",2:"Zero Hunger",3:"Good Health",4:"Quality Education",
             5:"Gender Equality",6:"Clean Water",7:"Affordable Energy",8:"Decent Work",
             9:"Industry & Innovation",10:"Reduced Inequalities",11:"Sustainable Cities",
             12:"Responsible Consumption",13:"Climate Action",14:"Life Below Water",
             15:"Life on Land",16:"Peace & Justice",17:"Partnerships"}

INDUSTRY_SDGS = {
    "Steel & Metals":[7,9,12,13,15,8],"FMCG / Consumer Goods":[2,3,6,12,13,14,15],
    "Energy & Utilities":[7,9,13,6,11],"Real Estate":[11,13,6,7,15],
    "Financial Services":[1,8,9,10,17],"Technology & IT":[4,8,9,12,13],
    "Pharmaceuticals":[3,6,12,13],"Chemicals":[3,6,9,12,13,14,15],
    "Automotive":[7,9,11,12,13],"Agriculture & Food":[2,6,12,13,14,15],
    "Textiles & Apparel":[5,6,8,12,13],"Cement & Construction":[9,11,12,13,15]
}

# ─── COMPREHENSIVE INDICATOR LIBRARY ────────────────────────────────────────
INDICATOR_LIBRARY = {
    "Steel & Metals": {
        "E": [
            {"name":"Scope 1 GHG emissions","unit":"tCO2e","gri":"305-1","sasb":"EM-IS-110a.1","csa":"Climate Strategy","min_val":0,"max_val":50000000,"sbti":True,"benchmark_avg":2800000,"benchmark_top":950000},
            {"name":"Scope 2 GHG emissions","unit":"tCO2e","gri":"305-2","sasb":"EM-IS-110a.1","csa":"Climate Strategy","min_val":0,"max_val":10000000,"sbti":True,"benchmark_avg":620000,"benchmark_top":180000},
            {"name":"Scope 3 GHG emissions","unit":"tCO2e","gri":"305-3","sasb":"EM-IS-110a.1","csa":"Climate Strategy","min_val":0,"max_val":100000000,"sbti":True,"benchmark_avg":8500000,"benchmark_top":2100000},
            {"name":"Carbon intensity of steel production","unit":"tCO2e/t steel","gri":"305-4","sasb":"EM-IS-110a.2","csa":"Climate Strategy","min_val":0,"max_val":5,"sbti":True,"benchmark_avg":1.85,"benchmark_top":0.6},
            {"name":"Total energy consumption","unit":"GJ","gri":"302-1","sasb":"EM-IS-130a.1","csa":"Operational Eco-Efficiency","min_val":0,"max_val":500000000,"benchmark_avg":18000000,"benchmark_top":5000000},
            {"name":"Renewable energy share","unit":"%","gri":"302-1","sasb":"EM-IS-130a.1","csa":"Climate Strategy","min_val":0,"max_val":100,"benchmark_avg":12,"benchmark_top":45},
            {"name":"Total water withdrawal","unit":"m³","gri":"303-3","sasb":"EM-IS-140a.1","csa":"Water Related Risks","min_val":0,"max_val":500000000,"benchmark_avg":8500000,"benchmark_top":2200000},
            {"name":"Water recycling rate","unit":"%","gri":"303-3","sasb":"EM-IS-140a.1","csa":"Water Related Risks","min_val":0,"max_val":100,"benchmark_avg":72,"benchmark_top":91},
            {"name":"Metal scrap recovery rate","unit":"%","gri":"306-4","sasb":"EM-IS-150a.1","csa":"Circular Economy","min_val":0,"max_val":100,"benchmark_avg":58,"benchmark_top":82},
            {"name":"Slag utilisation rate","unit":"%","gri":"306-2","sasb":"EM-IS-150a.1","csa":"Operational Eco-Efficiency","min_val":0,"max_val":100,"benchmark_avg":76,"benchmark_top":96},
            {"name":"Particulate matter emissions","unit":"kg/t steel","gri":"305-7","sasb":"EM-IS-120a.1","csa":"Operational Eco-Efficiency","min_val":0,"max_val":10,"benchmark_avg":0.8,"benchmark_top":0.2},
            {"name":"Hazardous waste generated","unit":"tonnes","gri":"306-3","sasb":"EM-IS-150a.1","csa":"Operational Eco-Efficiency","min_val":0,"max_val":5000000,"benchmark_avg":45000,"benchmark_top":8000},
        ],
        "S": [
            {"name":"Lost Time Injury Frequency Rate (LTIFR)","unit":"per 1M hrs","gri":"403-9","sasb":"EM-IS-320a.1","csa":"H&S","min_val":0,"max_val":20,"benchmark_avg":2.1,"benchmark_top":0.4},
            {"name":"Fatalities","unit":"number","gri":"403-9","sasb":"EM-IS-320a.1","csa":"H&S","min_val":0,"max_val":50,"benchmark_avg":1,"benchmark_top":0},
            {"name":"Heat stress incidents","unit":"number","gri":"403-10","sasb":"EM-IS-320a.1","csa":"H&S","min_val":0,"max_val":500,"benchmark_avg":12,"benchmark_top":0},
            {"name":"Women in total workforce","unit":"%","gri":"405-1","sasb":"—","csa":"Human Capital Dev","min_val":0,"max_val":100,"benchmark_avg":9,"benchmark_top":22},
            {"name":"Women in management","unit":"%","gri":"405-1","sasb":"—","csa":"Human Capital Dev","min_val":0,"max_val":100,"benchmark_avg":11,"benchmark_top":28},
            {"name":"Training hours per employee","unit":"hrs/year","gri":"404-1","sasb":"—","csa":"Human Capital Dev","min_val":0,"max_val":500,"benchmark_avg":32,"benchmark_top":68},
            {"name":"Community grievances resolved (%)","unit":"%","gri":"413-1","sasb":"EM-MM-210a.2","csa":"Local Communities","min_val":0,"max_val":100,"benchmark_avg":74,"benchmark_top":97},
            {"name":"Supplier ESG audits coverage","unit":"%","gri":"414-2","sasb":"EM-IS-430a.1","csa":"Supply Chain Mgmt","min_val":0,"max_val":100,"benchmark_avg":38,"benchmark_top":85},
        ],
        "G": [
            {"name":"Board independence","unit":"%","gri":"2-9","sasb":"—","csa":"Corporate Governance","min_val":0,"max_val":100,"benchmark_avg":52,"benchmark_top":78},
            {"name":"Women on board","unit":"%","gri":"405-1","sasb":"—","csa":"Corporate Governance","min_val":0,"max_val":100,"benchmark_avg":22,"benchmark_top":40},
            {"name":"ESG-linked executive pay","unit":"%","gri":"2-19","sasb":"—","csa":"Corporate Governance","min_val":0,"max_val":100,"benchmark_avg":18,"benchmark_top":38},
            {"name":"Anti-corruption training completion","unit":"%","gri":"205-2","sasb":"—","csa":"Business Ethics","min_val":0,"max_val":100,"benchmark_avg":82,"benchmark_top":100},
            {"name":"Data privacy incidents","unit":"number","gri":"418-1","sasb":"—","csa":"Risk Management","min_val":0,"max_val":100,"benchmark_avg":1,"benchmark_top":0},
        ]
    },
    "FMCG / Consumer Goods": {
        "E": [
            {"name":"Scope 1+2 GHG emissions","unit":"tCO2e","gri":"305-1,305-2","sasb":"CG-HP-110a.1","csa":"Climate Strategy","min_val":0,"max_val":10000000,"sbti":True,"benchmark_avg":420000,"benchmark_top":95000},
            {"name":"Scope 3 GHG emissions (FLAG)","unit":"tCO2e","gri":"305-3","sasb":"CG-HP-110a.1","csa":"Climate Strategy","min_val":0,"max_val":50000000,"sbti":True,"benchmark_avg":3200000,"benchmark_top":680000},
            {"name":"Recycled content in plastic packaging","unit":"%","gri":"301-2","sasb":"CG-HP-410a.1","csa":"Packaging","min_val":0,"max_val":100,"benchmark_avg":19,"benchmark_top":48},
            {"name":"Packaging recyclability rate","unit":"%","gri":"301-3","sasb":"CG-HP-410a.1","csa":"Packaging","min_val":0,"max_val":100,"benchmark_avg":62,"benchmark_top":91},
            {"name":"Virgin plastic use","unit":"tonnes","gri":"301-1","sasb":"CG-HP-410a.1","csa":"Packaging","min_val":0,"max_val":5000000,"benchmark_avg":85000,"benchmark_top":18000},
            {"name":"Water use intensity","unit":"litres/kg product","gri":"303-5","sasb":"FB-PF-140a.1","csa":"Water Related Risks","min_val":0,"max_val":1000,"benchmark_avg":4.2,"benchmark_top":1.8},
            {"name":"Sustainably-sourced palm oil (RSPO)","unit":"%","gri":"308-1","sasb":"FB-AG-430a.2","csa":"Supply Chain Mgmt","min_val":0,"max_val":100,"benchmark_avg":72,"benchmark_top":100},
            {"name":"Manufacturing waste to landfill","unit":"%","gri":"306-5","sasb":"CG-HP-150a.1","csa":"Operational Eco-Efficiency","min_val":0,"max_val":100,"benchmark_avg":8,"benchmark_top":0},
        ],
        "S": [
            {"name":"LTIFR","unit":"per 1M hrs","gri":"403-9","sasb":"—","csa":"H&S","min_val":0,"max_val":10,"benchmark_avg":0.9,"benchmark_top":0.2},
            {"name":"Women in management","unit":"%","gri":"405-1","sasb":"—","csa":"Human Capital Dev","min_val":0,"max_val":100,"benchmark_avg":38,"benchmark_top":52},
            {"name":"Supplier living wage coverage","unit":"%","gri":"2-30","sasb":"CG-HP-430a.1","csa":"Supply Chain Mgmt","min_val":0,"max_val":100,"benchmark_avg":28,"benchmark_top":72},
            {"name":"Child/forced labour audits passed","unit":"%","gri":"408-1","sasb":"CG-HP-430a.2","csa":"Supply Chain Mgmt","min_val":0,"max_val":100,"benchmark_avg":88,"benchmark_top":100},
        ],
        "G": [
            {"name":"Board independence","unit":"%","gri":"2-9","sasb":"—","csa":"Corporate Governance","min_val":0,"max_val":100,"benchmark_avg":58,"benchmark_top":80},
            {"name":"ESG-linked executive pay","unit":"%","gri":"2-19","sasb":"—","csa":"Corporate Governance","min_val":0,"max_val":100,"benchmark_avg":21,"benchmark_top":40},
            {"name":"Consumer data breaches","unit":"number","gri":"418-1","sasb":"CG-HP-220a.1","csa":"Risk Management","min_val":0,"max_val":50,"benchmark_avg":1,"benchmark_top":0},
        ]
    }
}

DEFAULT_INDICATORS = {
    "E": [
        {"name":"Scope 1 GHG emissions","unit":"tCO2e","gri":"305-1","sasb":"—","csa":"Climate Strategy","min_val":0,"max_val":50000000,"sbti":True,"benchmark_avg":None,"benchmark_top":None},
        {"name":"Scope 2 GHG emissions","unit":"tCO2e","gri":"305-2","sasb":"—","csa":"Climate Strategy","min_val":0,"max_val":10000000,"sbti":True,"benchmark_avg":None,"benchmark_top":None},
        {"name":"Scope 3 GHG emissions","unit":"tCO2e","gri":"305-3","sasb":"—","csa":"Climate Strategy","min_val":0,"max_val":100000000,"sbti":True,"benchmark_avg":None,"benchmark_top":None},
        {"name":"Total energy consumption","unit":"GJ","gri":"302-1","sasb":"—","csa":"Operational Eco-Efficiency","min_val":0,"max_val":500000000,"benchmark_avg":None,"benchmark_top":None},
        {"name":"Renewable energy share","unit":"%","gri":"302-1","sasb":"—","csa":"Climate Strategy","min_val":0,"max_val":100,"benchmark_avg":None,"benchmark_top":None},
        {"name":"Total water withdrawal","unit":"m³","gri":"303-3","sasb":"—","csa":"Water Related Risks","min_val":0,"max_val":500000000,"benchmark_avg":None,"benchmark_top":None},
        {"name":"Water recycling rate","unit":"%","gri":"303-3","sasb":"—","csa":"Water Related Risks","min_val":0,"max_val":100,"benchmark_avg":None,"benchmark_top":None},
        {"name":"Total waste generated","unit":"tonnes","gri":"306-3","sasb":"—","csa":"Operational Eco-Efficiency","min_val":0,"max_val":5000000,"benchmark_avg":None,"benchmark_top":None},
        {"name":"Waste diverted from landfill","unit":"%","gri":"306-4","sasb":"—","csa":"Operational Eco-Efficiency","min_val":0,"max_val":100,"benchmark_avg":None,"benchmark_top":None},
    ],
    "S": [
        {"name":"Total employees","unit":"number","gri":"2-7","sasb":"—","csa":"Human Capital Dev","min_val":0,"max_val":5000000,"benchmark_avg":None,"benchmark_top":None},
        {"name":"Women in workforce","unit":"%","gri":"405-1","sasb":"—","csa":"Human Capital Dev","min_val":0,"max_val":100,"benchmark_avg":None,"benchmark_top":None},
        {"name":"Women in management","unit":"%","gri":"405-1","sasb":"—","csa":"Human Capital Dev","min_val":0,"max_val":100,"benchmark_avg":None,"benchmark_top":None},
        {"name":"LTIFR","unit":"per 1M hrs","gri":"403-9","sasb":"—","csa":"H&S","min_val":0,"max_val":50,"benchmark_avg":None,"benchmark_top":None},
        {"name":"Fatalities","unit":"number","gri":"403-9","sasb":"—","csa":"H&S","min_val":0,"max_val":100,"benchmark_avg":None,"benchmark_top":None},
        {"name":"Training hours per employee","unit":"hrs/year","gri":"404-1","sasb":"—","csa":"Human Capital Dev","min_val":0,"max_val":500,"benchmark_avg":None,"benchmark_top":None},
        {"name":"Employee turnover rate","unit":"%","gri":"401-1","sasb":"—","csa":"Human Capital Dev","min_val":0,"max_val":100,"benchmark_avg":None,"benchmark_top":None},
        {"name":"Community investment","unit":"USD","gri":"413-1","sasb":"—","csa":"Local Communities","min_val":0,"max_val":1000000000,"benchmark_avg":None,"benchmark_top":None},
    ],
    "G": [
        {"name":"Board independence","unit":"%","gri":"2-9","sasb":"—","csa":"Corporate Governance","min_val":0,"max_val":100,"benchmark_avg":None,"benchmark_top":None},
        {"name":"Women on board","unit":"%","gri":"405-1","sasb":"—","csa":"Corporate Governance","min_val":0,"max_val":100,"benchmark_avg":None,"benchmark_top":None},
        {"name":"ESG-linked executive pay","unit":"%","gri":"2-19","sasb":"—","csa":"Corporate Governance","min_val":0,"max_val":100,"benchmark_avg":None,"benchmark_top":None},
        {"name":"Anti-corruption training completion","unit":"%","gri":"205-2","sasb":"—","csa":"Business Ethics","min_val":0,"max_val":100,"benchmark_avg":None,"benchmark_top":None},
        {"name":"Supply chain ESG audits","unit":"%","gri":"414-2","sasb":"—","csa":"Supply Chain Mgmt","min_val":0,"max_val":100,"benchmark_avg":None,"benchmark_top":None},
        {"name":"Data privacy incidents","unit":"number","gri":"418-1","sasb":"—","csa":"Risk Management","min_val":0,"max_val":100,"benchmark_avg":None,"benchmark_top":None},
    ]
}

TARGET_CATEGORIES = ["Net Zero / Carbon Neutral","Science-Based Target (SBTi)","100% Renewable Energy",
    "Water Positive / Water Neutral","Zero Waste to Landfill","Circular Economy",
    "Supply Chain Decarbonisation","Biodiversity Net Positive","Living Wage",
    "Gender Parity","Zero Fatalities","TCFD Alignment","Custom"]

SAMPLE_COMPANIES = {
    "TerraSteel Ltd":{"industry":"Steel & Metals","country":"India","revenue_bn":4.2,"E_score":62,"S_score":71,"G_score":68,"overall":67,"grade":"B","frameworks":["GRI","CDP","SASB"],"targets":4,"on_track":2,"at_risk":1,"lagging":1},
    "GreenPack FMCG":{"industry":"FMCG / Consumer Goods","country":"India","revenue_bn":2.1,"E_score":74,"S_score":69,"G_score":82,"overall":75,"grade":"B+","frameworks":["GRI","SASB","S&P CSA"],"targets":6,"on_track":4,"at_risk":2,"lagging":0},
    "Solaris Power":{"industry":"Energy & Utilities","country":"India","revenue_bn":8.7,"E_score":85,"S_score":73,"G_score":76,"overall":78,"grade":"A-","frameworks":["CDP","TCFD","IFRS S1/S2","GRI"],"targets":5,"on_track":4,"at_risk":1,"lagging":0},
}

# ─── HELPERS ─────────────────────────────────────────────────────────────────
def get_indicators(industry, pillar):
    lib = INDICATOR_LIBRARY.get(industry, {})
    return lib.get(pillar, DEFAULT_INDICATORS.get(pillar, []))

def score_to_grade(s):
    for threshold, grade in [(85,"A+"),(78,"A"),(72,"A-"),(65,"B+"),(58,"B"),(50,"B-"),(42,"C+"),(35,"C")]:
        if s >= threshold: return grade
    return "D"

def grade_color(g):
    if g.startswith("A"): return C["mid"]
    if g.startswith("B"): return "#4CAF80"
    if g.startswith("C"): return "#F59E0B"
    return "#EF4444"

def calc_expected_progress(baseline_year, target_year, current_year=None):
    cy = current_year or CURRENT_YEAR
    total = max(1, target_year - baseline_year)
    elapsed = max(0, cy - baseline_year)
    return min(100, round(elapsed / total * 100, 1))

def calc_actual_progress(baseline, target, current):
    try:
        b, t, c = float(baseline), float(target), float(current)
        if abs(t - b) < 1e-9: return 0
        return round(abs(c - b) / abs(t - b) * 100, 1)
    except: return 0

def get_status(actual_pct, expected_pct):
    if actual_pct >= expected_pct * 0.90: return "On Track"
    if actual_pct >= expected_pct * 0.50: return "At Risk"
    return "Lagging"

def validate_target(category, target_year, baseline_year):
    issues, suggestions, sbti_ok = [], [], False
    years_to_target = target_year - CURRENT_YEAR
    if target_year <= CURRENT_YEAR:
        issues.append("Target year has already passed.")
    if years_to_target > 30:
        issues.append("Target year is beyond 30 years out — consider interim milestones every 5 years.")
    if "Net Zero" in category or "Carbon Neutral" in category:
        if target_year <= 2050: sbti_ok = True; suggestions.append("✅ Aligns with IPCC 1.5°C net-zero-by-2050 pathway.")
        else: issues.append("Net zero beyond 2050 does not align with IPCC 1.5°C scenario.")
        suggestions.append("Ensure Scope 1, 2, and 3 covered. Residual emissions must be offset by verified removals (not offsets alone).")
    elif "SBTi" in category:
        if 5 <= years_to_target <= 15: sbti_ok = True; suggestions.append("✅ Timeframe consistent with SBTi near-term (5-10yr) or long-term validation.")
        else: issues.append("SBTi near-term targets should be 5-10 years from submission.")
        suggestions.append("Minimum 4.2% absolute reduction per year (cross-sector 1.5°C pathway) or use SDA method for heavy industry.")
    elif "Renewable Energy" in category:
        if target_year <= 2035: suggestions.append("✅ Aligns with RE100 and IEA NZE scenario trajectory.")
        else: issues.append("100% renewable post-2035 lags IEA Net Zero Emissions scenario.")
    elif "Water" in category:
        suggestions.append("Set context-based target using WRI Aqueduct for facility-level water stress. Flat % reductions score lower with CDP Water.")
    elif "Zero Waste" in category:
        if target_year <= 2030: suggestions.append("✅ Aligns with Ellen MacArthur / CGF zero waste commitments.")
    if CURRENT_YEAR - baseline_year > 5:
        issues.append(f"Baseline year ({baseline_year}) is over 5 years old. Consider restating to a more recent year for credibility.")
    return issues, suggestions, sbti_ok

def annual_reduction_needed(baseline, target, baseline_year, target_year):
    try:
        years = target_year - CURRENT_YEAR
        if years <= 0: return None
        gap = float(target) - float(baseline)
        already = float(0)
        return round(gap / years, 2)
    except: return None

def flag_value(val, indicator_meta):
    flags = []
    try:
        v = float(val)
        mn, mx = indicator_meta.get("min_val", 0), indicator_meta.get("max_val", 1e12)
        if v < mn: flags.append(f"Value below minimum plausible ({mn:,})")
        if v > mx: flags.append(f"Value exceeds maximum plausible ({mx:,.0f}) — please verify")
        if indicator_meta.get("unit") == "%" and (v < 0 or v > 100): flags.append("Percentage must be between 0 and 100")
    except: pass
    return flags

def make_gauge(value, title, color, max_val=100):
    fig = go.Figure(go.Indicator(mode="gauge+number",value=value,
        title={"text":title,"font":{"size":12,"color":C["text"],"family":"Inter"}},
        number={"font":{"size":24,"color":color,"family":"Inter"}},
        gauge={"axis":{"range":[0,max_val]},"bar":{"color":color,"thickness":.65},
               "bgcolor":C["foam"],"borderwidth":0,
               "steps":[{"range":[0,40],"color":"#FEE2E2"},{"range":[40,65],"color":"#FEF3C7"},
                        {"range":[65,85],"color":"#DCFCE7"},{"range":[85,100],"color":"#BBF7D0"}]}))
    fig.update_layout(height=170,margin=dict(t=40,b=10,l=20,r=20),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
    return fig

def make_radar(e,s,g):
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=[e,s,g,e],theta=["Environment","Social","Governance","Environment"],
        fill="toself",fillcolor="rgba(26,107,60,0.2)",line=dict(color=C["mid"],width=2)))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True,range=[0,100]),bgcolor="rgba(0,0,0,0)"),
        showlegend=False,height=200,margin=dict(t=20,b=20,l=20,r=20),paper_bgcolor="rgba(0,0,0,0)")
    return fig

def make_target_vs_actual_chart(t):
    baseline = t.get("baseline", 0)
    target_val = t.get("target_val", 0)
    current = t.get("current", 0)
    baseline_year = t.get("baseline_year", 2020)
    target_year = t.get("target_year", 2030)
    expected_pct = calc_expected_progress(baseline_year, target_year)
    total_change = target_val - baseline
    expected_val = round(baseline + (total_change * expected_pct / 100), 2)
    status_colors = {"On Track": C["mid"], "At Risk": "#F59E0B", "Lagging": "#EF4444"}
    sc = status_colors.get(t.get("status", "On Track"), C["mid"])
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Baseline", x=["Baseline", "Current (Actual)", "Expected Now", "Target"], y=[baseline, None, None, None],
        marker_color=C["mist"], opacity=0.7))
    fig.add_trace(go.Bar(name="Current (Actual)", x=["Baseline", "Current (Actual)", "Expected Now", "Target"], y=[None, current, None, None],
        marker_color=sc))
    fig.add_trace(go.Bar(name="Expected by now", x=["Baseline", "Current (Actual)", "Expected Now", "Target"], y=[None, None, expected_val, None],
        marker_color="#93C5FD", opacity=0.85))
    fig.add_trace(go.Bar(name=f"Target ({target_year})", x=["Baseline", "Current (Actual)", "Expected Now", "Target"], y=[None, None, None, target_val],
        marker_color=C["dark"], opacity=0.9))
    fig.update_layout(barmode="group", height=240, margin=dict(t=20,b=20,l=40,r=20),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=-0.25, font=dict(size=10)),
        yaxis=dict(gridcolor=C["foam"], title=t.get("indicator","Value")),
        font=dict(family="Inter", size=11))
    return fig

def make_sdg_heatmap(company_name, companies, esg_data_store):
    company = companies.get(company_name, {})
    industry = company.get("industry", "")
    sdgs = INDUSTRY_SDGS.get(industry, [13,12,6,8])
    indicators = get_indicators(industry, "E") + get_indicators(industry, "S") + get_indicators(industry, "G")
    esg_data = esg_data_store.get(company_name, {})
    rows, values, colors_list = [], [], []
    for sdg in sdgs:
        rows.append(f"SDG {sdg}: {SDG_NAMES.get(sdg,'')}")
        score = company.get("overall", 0)
        if score >= 75: values.append(3); colors_list.append(SDG_COLORS.get(sdg, "#999"))
        elif score >= 55: values.append(2); colors_list.append(SDG_COLORS.get(sdg, "#999"))
        else: values.append(1); colors_list.append("#FCA5A5")
    fig = go.Figure(go.Bar(x=values, y=rows, orientation="h",
        marker=dict(color=colors_list, line=dict(width=0)), width=0.6))
    fig.update_layout(height=max(200, len(sdgs)*40+60), xaxis=dict(range=[0,4],tickvals=[1,2,3],
        ticktext=["Needs work","Progressing","Strong"],gridcolor=C["foam"]),
        yaxis=dict(tickfont=dict(size=10)),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=10,b=20,l=10,r=10), font=dict(family="Inter",size=10))
    return fig

# ─── SESSION STATE ────────────────────────────────────────────────────────────
if "companies" not in st.session_state: st.session_state.companies = dict(SAMPLE_COMPANIES)
if "current_company" not in st.session_state: st.session_state.current_company = None
if "esg_data" not in st.session_state: st.session_state.esg_data = {}
if "targets" not in st.session_state: st.session_state.targets = {}
if "dq" not in st.session_state: st.session_state.dq = {}

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""<div style='text-align:center;padding:12px 0 20px 0;'>
        <div style='font-size:2rem;'>🌿</div>
        <div style='font-size:1.15rem;font-weight:700;color:#DAF1DE;'>ESG Compass</div>
        <div style='font-size:.72rem;color:#A8D5B5;margin-top:2px;'>Multi-Framework ESG Intelligence</div>
    </div>""", unsafe_allow_html=True)
    page = st.radio("", ["🏠  Dashboard","🏢  Company Setup","📊  Data Input","🎯  Targets","📈  Analysis & Insights"], label_visibility="collapsed")
    st.markdown("---")
    if st.session_state.current_company:
        st.markdown(f"<div style='font-size:.72rem;color:#A8D5B5;'>Active company</div><div style='font-size:.9rem;font-weight:600;color:#DAF1DE;'>{st.session_state.current_company}</div>", unsafe_allow_html=True)
        st.markdown("---")
    for fw in FRAMEWORKS:
        st.markdown(f"<div style='font-size:.78rem;color:#A8D5B5;padding:2px 0;'>✓ {fw}</div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"<div style='font-size:.65rem;color:#5A8A6A;text-align:center;'>v2.0 · GRI·CDP·SASB·IFRS·CSA·GRESB·SBTi</div>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# DASHBOARD
# ════════════════════════════════════════════════════════════
if "Dashboard" in page:
    st.markdown("<div class='main-header'><h1>🌿 ESG Compass</h1><p>Multi-framework ESG performance intelligence · GRI · CDP · SASB · IFRS S1/S2 · S&P CSA · GRESB · SBTi</p></div>", unsafe_allow_html=True)
    companies = st.session_state.companies
    all_scores = [c["overall"] for c in companies.values()]
    c1,c2,c3,c4 = st.columns(4)
    with c1: st.markdown(f"<div class='metric-card'><div class='value'>{len(companies)}</div><div class='label'>Companies</div></div>", unsafe_allow_html=True)
    with c2:
        avg = round(sum(all_scores)/len(all_scores),1) if all_scores else 0
        st.markdown(f"<div class='metric-card'><div class='value'>{avg}</div><div class='label'>Avg ESG Score</div></div>", unsafe_allow_html=True)
    with c3:
        tot = sum(c["targets"] for c in companies.values()); ot = sum(c["on_track"] for c in companies.values())
        st.markdown(f"<div class='metric-card'><div class='value'>{ot}/{tot}</div><div class='label'>Targets On Track</div></div>", unsafe_allow_html=True)
    with c4:
        ac = sum(1 for c in companies.values() if c["grade"].startswith("A"))
        st.markdown(f"<div class='metric-card'><div class='value'>{ac}</div><div class='label'>A-Grade Companies</div></div>", unsafe_allow_html=True)

    st.markdown("<br><div class='section-label'>ALL COMPANIES</div>", unsafe_allow_html=True)
    # indicator coverage column
    selected_view = None
    for name, data in companies.items():
        gc = grade_color(data["grade"])
        # indicator fill rate
        esg_d = st.session_state.esg_data.get(name, {})
        total_ind = sum(len(get_indicators(data.get("industry",""), p)) for p in ["E","S","G"])
        filled_ind = 0
        for pillar_data in esg_d.values():
            if isinstance(pillar_data, dict):
                filled_ind += sum(1 for v in pillar_data.values() if isinstance(v,dict) and v.get("current",0))
        cov_pct = round(filled_ind/max(total_ind,1)*100) if total_ind else 0
        on_pct = round(data["on_track"]/data["targets"]*100) if data["targets"] else 0
        target_status = "🟢" if on_pct>=67 else ("🟡" if on_pct>=34 else "🔴")
        fws = " ".join([f"<span class='framework-badge'>{fw}</span>" for fw in data.get("frameworks",[])])
        col1, col2 = st.columns([4,1])
        with col1:
            st.markdown(f"""<div class='esg-card'>
              <div style='display:flex;align-items:center;gap:10px;margin-bottom:10px;'>
                <div style='font-size:1rem;font-weight:700;'>{name}</div>
                <div style='background:{gc};color:white;border-radius:6px;padding:2px 10px;font-size:.8rem;font-weight:700;'>{data["grade"]}</div>
                <div style='font-size:.8rem;color:{C["subtle"]};'>{data.get("industry","")} · {data.get("country","")}</div>
                <div style='margin-left:auto;font-size:.8rem;'>{target_status} {data["on_track"]}/{data["targets"]} targets</div>
              </div>
              <div style='display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:8px;margin-bottom:8px;'>
                <div><div style='font-size:.7rem;color:{C["subtle"]};margin-bottom:3px;'>E — {data["E_score"]}</div>
                  <div style='background:{C["foam"]};border-radius:4px;height:6px;'><div style='width:{data["E_score"]}%;background:{C["mid"]};height:6px;border-radius:4px;'></div></div></div>
                <div><div style='font-size:.7rem;color:{C["subtle"]};margin-bottom:3px;'>S — {data["S_score"]}</div>
                  <div style='background:{C["foam"]};border-radius:4px;height:6px;'><div style='width:{data["S_score"]}%;background:#4CAF80;height:6px;border-radius:4px;'></div></div></div>
                <div><div style='font-size:.7rem;color:{C["subtle"]};margin-bottom:3px;'>G — {data["G_score"]}</div>
                  <div style='background:{C["foam"]};border-radius:4px;height:6px;'><div style='width:{data["G_score"]}%;background:#A8D5B5;height:6px;border-radius:4px;'></div></div></div>
                <div><div style='font-size:.7rem;color:{C["subtle"]};margin-bottom:3px;'>Coverage — {cov_pct}%</div>
                  <div style='background:{C["foam"]};border-radius:4px;height:6px;'><div style='width:{cov_pct}%;background:#93C5FD;height:6px;border-radius:4px;'></div></div></div>
              </div><div>{fws}</div></div>""", unsafe_allow_html=True)
        with col2:
            if st.button("View Details", key=f"vd_{name}"):
                st.session_state.current_company = name
                st.rerun()

    # scatter
    st.markdown("<div class='section-label' style='margin-top:24px;'>ESG LANDSCAPE</div>", unsafe_allow_html=True)
    df_p = pd.DataFrame([{"Company":k,"E":v["E_score"],"S":v["S_score"],"Overall":v["overall"],"Industry":v.get("industry","")} for k,v in companies.items()])
    if not df_p.empty:
        fig_s = px.scatter(df_p,x="E",y="S",size="Overall",color="Industry",hover_name="Company",size_max=40,
            color_discrete_sequence=[C["mid"],"#4CAF80",C["mist"],"#1A6B3C","#A8D5B5"])
        fig_s.update_layout(height=300,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor=C["bg"],
            xaxis=dict(range=[0,105],gridcolor=C["foam"]),yaxis=dict(range=[0,105],gridcolor=C["foam"]),
            margin=dict(t=20,b=40,l=40,r=20),font=dict(family="Inter"))
        st.plotly_chart(fig_s, use_container_width=True)

# ════════════════════════════════════════════════════════════
# COMPANY SETUP
# ════════════════════════════════════════════════════════════
elif "Company Setup" in page:
    st.markdown("<div class='main-header'><h1>🏢 Company Setup</h1><p>Register and manage companies</p></div>", unsafe_allow_html=True)
    tab1,tab2 = st.tabs(["➕ New Company","📋 Existing Companies"])
    with tab1:
        col1,col2 = st.columns(2)
        with col1:
            cn = st.text_input("Company Name *")
            ind = st.selectbox("Industry *", INDUSTRIES)
            country = st.text_input("Country", "India")
            rev = st.number_input("Revenue (USD Billion)", 0.0, step=0.1)
        with col2:
            ry = st.selectbox("Reporting Year", list(range(CURRENT_YEAR-1, CURRENT_YEAR-6, -1)))
            emp = st.number_input("Employees", 0, step=100)
            fws = st.multiselect("Reporting Frameworks", FRAMEWORKS, default=["GRI","CDP"])
        if st.button("Register Company →"):
            if cn:
                st.session_state.companies[cn] = {"industry":ind,"country":country,"revenue_bn":rev,"E_score":0,"S_score":0,"G_score":0,"overall":0,"grade":"—","frameworks":fws,"targets":0,"on_track":0,"at_risk":0,"lagging":0,"employees":emp,"report_year":ry}
                st.session_state.current_company = cn
                st.success(f"✅ {cn} registered.")
            else: st.error("Company name required.")
    with tab2:
        for name, data in st.session_state.companies.items():
            c1,c2,c3 = st.columns([3,1,1])
            with c1: st.markdown(f"**{name}** · {data.get('industry','')} · {data.get('country','')}")
            with c2: st.markdown(f"<span style='background:{grade_color(data['grade'])};color:white;border-radius:5px;padding:2px 8px;font-size:.8rem;'>{data['grade']}</span>", unsafe_allow_html=True)
            with c3:
                if st.button("Select", key=f"sel_{name}"):
                    st.session_state.current_company = name
                    st.success(f"Active: {name}")

# ════════════════════════════════════════════════════════════
# DATA INPUT
# ════════════════════════════════════════════════════════════
elif "Data Input" in page:
    st.markdown("<div class='main-header'><h1>📊 ESG Data Input</h1><p>Industry-specific indicators · GRI · SASB · CDP · IFRS S1/S2 · S&P CSA · GRESB · BRSR</p></div>", unsafe_allow_html=True)
    cl = list(st.session_state.companies.keys())
    di = cl.index(st.session_state.current_company) if st.session_state.current_company in cl else 0
    ac = st.selectbox("Active Company", cl, index=di)
    st.session_state.current_company = ac
    cd = st.session_state.companies.get(ac, {})
    industry = cd.get("industry", INDUSTRIES[0])
    if ac not in st.session_state.esg_data: st.session_state.esg_data[ac] = {}
    if ac not in st.session_state.dq: st.session_state.dq[ac] = {"assured":False,"assurance_level":"None","coverage_pct":0,"assurer":""}

    # Data quality layer
    st.markdown("<div class='section-label'>DATA QUALITY DECLARATION</div>", unsafe_allow_html=True)
    with st.expander("📋 Data Quality & Assurance", expanded=False):
        dq = st.session_state.dq[ac]
        col1,col2,col3,col4 = st.columns(4)
        with col1: dq["assured"] = st.checkbox("Externally assured", dq.get("assured",False))
        with col2: dq["assurance_level"] = st.selectbox("Assurance level", ["None","Limited","Reasonable"], index=["None","Limited","Reasonable"].index(dq.get("assurance_level","None")))
        with col3: dq["assurer"] = st.text_input("Assurance provider", dq.get("assurer",""))
        with col4: dq["coverage_pct"] = st.number_input("Data coverage (% of operations)", 0, 100, int(dq.get("coverage_pct",0)))
        st.session_state.dq[ac] = dq
        badge = "dq-badge-assured" if dq["assured"] and dq["coverage_pct"]>=80 else ("dq-badge-partial" if dq["coverage_pct"]>=50 else "dq-badge-unassured")
        label = "Externally Assured" if dq["assured"] else ("Partial Coverage" if dq["coverage_pct"]>=50 else "Low Coverage / Unassured")
        st.markdown(f"<span class='{badge}'>{label} · {dq['coverage_pct']}% coverage</span>", unsafe_allow_html=True)

    # Template download (comprehensive, all pillars, framework-mapped)
    st.markdown("<div class='section-label' style='margin-top:12px;'>DOWNLOADABLE TEMPLATE</div>", unsafe_allow_html=True)
    col_dl, col_up = st.columns([1,2])
    with col_dl:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            for pillar, pname in [("E","Environmental"),("S","Social"),("G","Governance")]:
                inds = get_indicators(industry, pillar)
                rows = []
                for ind_meta in inds:
                    rows.append({"Indicator": ind_meta["name"],"Unit": ind_meta["unit"],
                        "GRI Disclosure": ind_meta.get("gri","—"),"SASB Code": ind_meta.get("sasb","—"),
                        "S&P CSA Criterion": ind_meta.get("csa","—"),
                        "Current Year Value": "","Prior Year Value": "",
                        "Assurance Status (Yes/No)":"","Coverage (% of operations)":"",
                        "Methodology / Notes":"","Min. Plausible": ind_meta.get("min_val",""),
                        "Max. Plausible": ind_meta.get("max_val",""),
                        "Industry Avg Benchmark": ind_meta.get("benchmark_avg",""),
                        "Top Quartile Benchmark": ind_meta.get("benchmark_top","")})
                pd.DataFrame(rows).to_excel(writer, sheet_name=pname[:31], index=False)
            # Instructions sheet
            inst = pd.DataFrame([
                {"Field":"Current Year Value","Guidance":f"Report for the most recent complete fiscal year (reporting year: {cd.get('report_year', CURRENT_YEAR-1)})"},
                {"Field":"Unit","Guidance":"Units are pre-set per GRI/SASB standards. Do not change."},
                {"Field":"Assurance Status","Guidance":"Enter Yes if this specific indicator has been externally assured."},
                {"Field":"Coverage","Guidance":"Enter % of operations/revenue covered by this data point."},
                {"Field":"Benchmarks","Guidance":"Pre-filled industry averages (source: S&P CSA aggregates, GRI benchmark data). Use for self-assessment only."},
                {"Field":"Currency","Guidance":"All monetary values in USD. Convert using year-average exchange rate."},
                {"Field":"Emissions","Guidance":"All GHG in metric tonnes CO2 equivalent (tCO2e). Use GHG Protocol methodologies."},
                {"Field":"Intensity","Guidance":"Where intensity metrics apply, the tool will calculate automatically from absolute + production data."}
            ])
            inst.to_excel(writer, sheet_name="Instructions", index=False)
        output.seek(0)
        st.download_button("⬇️ Download Template", data=output,
            file_name=f"ESGCompass_{ac.replace(' ','_')}_Template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    with col_up:
        uf = st.file_uploader("Upload completed template (.xlsx)", type=["xlsx"])
        if uf:
            try:
                xl = pd.read_excel(uf, sheet_name=None)
                parsed = {}
                for sname, df in xl.items():
                    if "Indicator" in df.columns and "Current Year Value" in df.columns:
                        pillar_key = {"Environmental":"E","Social":"S","Governance":"G"}.get(sname, sname)
                        parsed[pillar_key] = {}
                        for _, row in df.iterrows():
                            if pd.notna(row.get("Indicator")) and pd.notna(row.get("Current Year Value")):
                                parsed[pillar_key][row["Indicator"]] = {"current": row["Current Year Value"], "prior": row.get("Prior Year Value",0)}
                st.session_state.esg_data[ac] = parsed
                st.success(f"✅ Data uploaded for {ac}")
            except Exception as e: st.error(f"Error reading file: {e}")

    st.markdown("---")
    st.markdown("<div class='section-label'>MANUAL DATA ENTRY</div>", unsafe_allow_html=True)

    # Production volume for intensity calcs
    with st.expander("⚙️ Production / Activity Data (for intensity calculations)"):
        col1,col2,col3 = st.columns(3)
        with col1: prod_vol = st.number_input("Production volume (tonnes/units)", 0.0, step=1000.0, key=f"prod_{ac}")
        with col2: prod_unit = st.selectbox("Production unit", ["tonnes","MWh generated","m² floor area","units sold","million litres"], key=f"pu_{ac}")
        with col3: revenue_usd = st.number_input("Revenue (USD)", 0.0, step=1000000.0, key=f"rev_{ac}")
        if prod_vol > 0:
            st.markdown(f"<div class='alert-success'>Intensity denominators set: {prod_vol:,.0f} {prod_unit} · USD {revenue_usd:,.0f}</div>", unsafe_allow_html=True)

    tab_e, tab_s, tab_g = st.tabs(["🌍 Environmental","👥 Social","🏛️ Governance"])

    def render_pillar_tab(pillar, tab_name):
        inds = get_indicators(industry, pillar)
        if pillar not in st.session_state.esg_data[ac]:
            st.session_state.esg_data[ac][pillar] = {}
        filled = 0
        for i, ind_meta in enumerate(inds):
            iname = ind_meta["name"]
            unit = ind_meta["unit"]
            stored = st.session_state.esg_data[ac][pillar].get(iname, {})
            cur_val = float(stored.get("current", 0) or 0)
            prior_val = float(stored.get("prior", 0) or 0)
            with st.expander(f"{'✅' if cur_val else '○'}  {iname}  [{unit}]  ·  GRI {ind_meta.get('gri','—')}  ·  SASB {ind_meta.get('sasb','—')}  ·  CSA: {ind_meta.get('csa','—')}"):
                col1,col2,col3 = st.columns(3)
                with col1:
                    new_cur = st.number_input(f"Current year ({cd.get('report_year', CURRENT_YEAR-1)})", value=cur_val, key=f"{pillar}_{i}_c", step=0.01)
                with col2:
                    new_prior = st.number_input(f"Prior year ({cd.get('report_year', CURRENT_YEAR-1)-1})", value=prior_val, key=f"{pillar}_{i}_p", step=0.01)
                with col3:
                    if new_prior and new_cur:
                        yoy = round((new_cur - new_prior) / max(abs(new_prior), 0.001) * 100, 1)
                        col_yoy = "#15803D" if yoy < 0 and pillar == "E" else ("#15803D" if yoy > 0 and pillar in ["S","G"] else "#B91C1C")
                        st.markdown(f"<div style='padding-top:28px;font-size:.85rem;'>YoY: <b style='color:{col_yoy};'>{yoy:+.1f}%</b></div>", unsafe_allow_html=True)
                # Value flags
                flags = flag_value(new_cur, ind_meta)
                for fl in flags:
                    st.markdown(f"<div class='alert-warning'>⚠️ {fl}<br><small>Please confirm this value and note evidence in the Methodology field.</small></div>", unsafe_allow_html=True)
                # Benchmarks
                ba, bt = ind_meta.get("benchmark_avg"), ind_meta.get("benchmark_top")
                if ba is not None:
                    st.markdown(f"<div style='font-size:.78rem;color:{C['subtle']};margin-top:4px;'>📊 Industry avg: <b>{ba:,}</b> · Top quartile: <b>{bt:,}</b> {unit}</div>", unsafe_allow_html=True)
                    if new_cur > 0 and ba > 0:
                        vs_avg = round((new_cur - ba)/abs(ba)*100, 1)
                        direction = "below" if vs_avg < 0 else "above"
                        col_dir = C["mid"] if (vs_avg < 0 and unit not in ["%"]) or (vs_avg > 0 and unit == "%") else "#B91C1C"
                        st.markdown(f"<div style='font-size:.78rem;color:{col_dir};'>{abs(vs_avg):.1f}% {direction} industry average</div>", unsafe_allow_html=True)
                # Intensity calc
                if prod_vol > 0 and new_cur > 0 and unit not in ["%","number","hrs/year"]:
                    intensity = round(new_cur / prod_vol, 4)
                    st.markdown(f"<div style='font-size:.78rem;color:{C['subtle']};'>Intensity: <b>{intensity:,}</b> {unit}/{prod_unit}</div>", unsafe_allow_html=True)
                # Action insight
                targets_for_co = st.session_state.targets.get(ac, [])
                for t in targets_for_co:
                    if t.get("indicator","").lower() in iname.lower() or iname.lower() in t.get("indicator","").lower():
                        needed = annual_reduction_needed(t.get("baseline",0), t.get("target_val",0), t.get("baseline_year",2020), t.get("target_year",2030))
                        if needed is not None:
                            st.markdown(f"<div class='alert-success'>🎯 To meet target by {t['target_year']}: change by <b>{needed:+,.2f} {unit}/year</b></div>", unsafe_allow_html=True)
                st.session_state.esg_data[ac][pillar][iname] = {"current": new_cur, "prior": new_prior}
                if new_cur: filled += 1
        return filled, len(inds)

    with tab_e:
        f, t = render_pillar_tab("E", "Environmental")
        st.markdown(f"<div style='font-size:.8rem;color:{C['subtle']};margin-top:8px;'>{f}/{t} indicators filled ({round(f/max(t,1)*100)}% coverage)</div>", unsafe_allow_html=True)
    with tab_s:
        f, t = render_pillar_tab("S", "Social")
        st.markdown(f"<div style='font-size:.8rem;color:{C['subtle']};margin-top:8px;'>{f}/{t} indicators filled ({round(f/max(t,1)*100)}% coverage)</div>", unsafe_allow_html=True)
    with tab_g:
        f, t = render_pillar_tab("G", "Governance")
        st.markdown(f"<div style='font-size:.8rem;color:{C['subtle']};margin-top:8px;'>{f}/{t} indicators filled ({round(f/max(t,1)*100)}% coverage)</div>", unsafe_allow_html=True)

    if st.button("💾 Save & Recalculate Scores"):
        total_filled = total_ind = 0
        scores = {}
        for pillar in ["E","S","G"]:
            inds = get_indicators(industry, pillar)
            f_p = sum(1 for v in st.session_state.esg_data[ac].get(pillar,{}).values() if isinstance(v,dict) and v.get("current",0))
            total_filled += f_p
            total_ind += len(inds)
            # Score: base 30 + coverage bonus (up to 40) + benchmark performance bonus (up to 25)
            cov_score = round((f_p / max(len(inds),1)) * 40)
            # Benchmark bonus
            bench_score = 0
            for ind_meta in inds:
                val = st.session_state.esg_data[ac].get(pillar,{}).get(ind_meta["name"],{}).get("current",0)
                ba, bt = ind_meta.get("benchmark_avg"), ind_meta.get("benchmark_top")
                if val and ba and bt and val > 0:
                    unit = ind_meta.get("unit","")
                    if unit == "%":
                        if val >= bt: bench_score += 2
                        elif val >= ba: bench_score += 1
                    else:
                        if val <= bt: bench_score += 2
                        elif val <= ba: bench_score += 1
            bench_bonus = min(25, bench_score)
            scores[pillar] = min(95, 30 + cov_score + bench_bonus)
        overall = round((scores["E"]*0.4 + scores["S"]*0.35 + scores["G"]*0.25))
        st.session_state.companies[ac].update({"E_score":scores["E"],"S_score":scores["S"],"G_score":scores["G"],"overall":overall,"grade":score_to_grade(overall)})
        st.success(f"✅ Scores recalculated — E:{scores['E']} · S:{scores['S']} · G:{scores['G']} · Overall:{overall} ({score_to_grade(overall)}) · {total_filled}/{total_ind} indicators filled ({round(total_filled/max(total_ind,1)*100)}%)")

# ════════════════════════════════════════════════════════════
# TARGETS
# ════════════════════════════════════════════════════════════
elif "Targets" in page:
    st.markdown("<div class='main-header'><h1>🎯 ESG Targets</h1><p>Set, validate, and track sustainability commitments · SBTi · IPCC · CDP · RE100</p></div>", unsafe_allow_html=True)
    cl = list(st.session_state.companies.keys())
    di = cl.index(st.session_state.current_company) if st.session_state.current_company in cl else 0
    ac = st.selectbox("Active Company", cl, index=di)
    st.session_state.current_company = ac
    cd = st.session_state.companies.get(ac, {})
    industry = cd.get("industry", INDUSTRIES[0])
    if ac not in st.session_state.targets: st.session_state.targets[ac] = []

    # Build indicator name list for dropdowns
    all_ind_names = []
    for pillar in ["E","S","G"]:
        all_ind_names += [m["name"] for m in get_indicators(industry, pillar)]

    # ADD TARGET
    with st.expander("➕ Add New Target", expanded=len(st.session_state.targets[ac])==0):
        col1,col2,col3 = st.columns(3)
        with col1:
            t_cat = st.selectbox("Target Category", TARGET_CATEGORIES)
            t_name = st.text_input("Target Name *", placeholder="e.g. Net Zero Operations by 2050")
            t_pillar = st.selectbox("ESG Pillar", ["E — Environmental","S — Social","G — Governance"])
        with col2:
            t_indicator = st.selectbox("Linked KPI / Indicator", ["(select or type)"] + all_ind_names)
            if t_indicator == "(select or type)":
                t_indicator = st.text_input("Or type custom KPI", placeholder="e.g. Scope 1+2 emissions (tCO2e)")
            t_unit = st.text_input("Unit", placeholder="e.g. tCO2e")
            baseline_years = list(range(CURRENT_YEAR-1, 2005, -1))
            t_baseline_year = st.selectbox("Baseline Year", baseline_years)
            t_baseline = st.number_input("Baseline Value", step=0.01)
        with col3:
            t_target_val = st.number_input("Target Value", step=0.01)
            target_years = list(range(CURRENT_YEAR+1, 2076))
            t_target_year = st.selectbox("Target Year", target_years, index=target_years.index(2030) if 2030 in target_years else 0)
            t_current = st.number_input("Current Achievement (latest)", step=0.01)
        t_sbti = st.checkbox("Flag for SBTi-style validation")
        t_notes = st.text_area("Scope / Notes", height=50)

        col_add, col_info = st.columns([1,3])
        with col_info:
            st.markdown(f"""<div class='alert-success' style='font-size:.8rem;'>
            <b>Validate</b> checks: ① Target year realism ② Framework alignment (IPCC 1.5°C / RE100 / CDP Water)
            ③ Baseline recency ④ Ambition vs benchmark ⑤ Scope completeness (SBTi 5-point logic)
            </div>""", unsafe_allow_html=True)
        with col_add:
            add_clicked = st.button("✅ Validate & Add →")

        if add_clicked:
            if not t_name: st.error("Target name required.")
            else:
                issues, suggestions, sbti_ok = validate_target(t_cat, t_target_year, t_baseline_year)
                actual_pct = calc_actual_progress(t_baseline, t_target_val, t_current)
                expected_pct = calc_expected_progress(t_baseline_year, t_target_year)
                status = get_status(actual_pct, expected_pct)
                entry = {"name":t_name,"category":t_cat,"pillar":t_pillar[0],
                    "indicator":t_indicator,"unit":t_unit,"baseline":t_baseline,
                    "baseline_year":t_baseline_year,"target_val":t_target_val,
                    "target_year":t_target_year,"current":t_current,
                    "actual_pct":actual_pct,"expected_pct":expected_pct,
                    "status":status,"sbti_validated":sbti_ok,
                    "issues":issues,"suggestions":suggestions,"notes":t_notes}
                st.session_state.targets[ac].append(entry)
                all_t = st.session_state.targets[ac]
                st.session_state.companies[ac].update({"targets":len(all_t),
                    "on_track":sum(1 for t in all_t if t["status"]=="On Track"),
                    "at_risk":sum(1 for t in all_t if t["status"]=="At Risk"),
                    "lagging":sum(1 for t in all_t if t["status"]=="Lagging")})
                if issues:
                    for iss in issues: st.markdown(f"<div class='alert-warning'>⚠️ {iss}</div>", unsafe_allow_html=True)
                for sug in suggestions: st.markdown(f"<div class='alert-success'>{sug}</div>", unsafe_allow_html=True)
                if sbti_ok: st.success("✅ SBTi-style validation passed.")
                st.success(f"Target '{t_name}' added · Status: {status} · Actual progress: {actual_pct}% · Expected by now: {expected_pct}%")

    # TARGET LIST
    targets = st.session_state.targets.get(ac, [])
    if targets:
        st.markdown(f"<div class='section-label' style='margin-top:20px;'>TARGETS ({len(targets)})</div>", unsafe_allow_html=True)
        for i, t in enumerate(targets):
            icon = "🟢" if t["status"]=="On Track" else ("🟡" if t["status"]=="At Risk" else "🔴")
            sbti_b = " <span style='background:#1A6B3C;color:white;border-radius:4px;padding:1px 6px;font-size:.7rem;'>SBTi ✓</span>" if t.get("sbti_validated") else ""
            with st.expander(f"{icon} {t['name']} — {t['category']} · {t['target_year']}"):
                col1,col2 = st.columns([1,2])
                with col1:
                    st.plotly_chart(make_target_vs_actual_chart(t), use_container_width=True)
                with col2:
                    # Key metrics
                    gap = round(float(t.get("target_val",0)) - float(t.get("current",0)), 2)
                    actual = t.get("actual_pct", 0)
                    expected = t.get("expected_pct", 0)
                    gap_class = "gap-positive" if (gap < 0 and t["pillar"]=="E") or (gap > 0 and t["pillar"] in ["S","G"]) else "gap-negative"
                    st.markdown(f"""
                    <div class='esg-card' style='padding:14px;'>
                      <div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-bottom:10px;'>
                        <div style='text-align:center;'>
                          <div style='font-size:1.3rem;font-weight:700;color:{C["mid"]};'>{actual}%</div>
                          <div style='font-size:.7rem;color:{C["subtle"]};'>Actual progress</div></div>
                        <div style='text-align:center;'>
                          <div style='font-size:1.3rem;font-weight:700;color:#93C5FD;'>{expected}%</div>
                          <div style='font-size:.7rem;color:{C["subtle"]};'>Expected by now</div></div>
                        <div style='text-align:center;'>
                          <div style='font-size:1.3rem;font-weight:700;' class='{gap_class}'>{gap:+,.2f}</div>
                          <div style='font-size:.7rem;color:{C["subtle"]};'>Gap ({t.get("unit","")})</div></div>
                      </div>
                      <div style='font-size:.82rem;margin-bottom:4px;'>
                        <b>Baseline:</b> {t.get("baseline"):,} ({t.get("baseline_year")}) →
                        <b>Current:</b> {t.get("current"):,} →
                        <b>Target:</b> {t.get("target_val"):,} ({t.get("target_year")})
                      </div>
                      <div style='font-size:.82rem;'><b>KPI:</b> {t.get("indicator","—")} {sbti_b}</div>
                    </div>""", unsafe_allow_html=True)
                    # Annual action insight
                    needed = annual_reduction_needed(t.get("baseline",0), t.get("target_val",0), t.get("baseline_year",2020), t.get("target_year",2030))
                    if needed is not None:
                        st.markdown(f"<div class='strategy-box'>📍 <b>Action required:</b> Change {t.get('indicator','value')} by <b>{needed:+,.2f} {t.get('unit','')}/year</b> from today through {t.get('target_year')} to meet this target.</div>", unsafe_allow_html=True)
                    if t.get("suggestions"):
                        for s in t["suggestions"]: st.markdown(f"<div class='alert-success'>{s}</div>", unsafe_allow_html=True)
                    if t.get("issues"):
                        for iss in t["issues"]: st.markdown(f"<div class='alert-warning'>⚠️ {iss}</div>", unsafe_allow_html=True)

                # Delete button
                if st.button(f"🗑️ Delete target", key=f"del_{ac}_{i}"):
                    st.session_state.targets[ac].pop(i)
                    all_t = st.session_state.targets[ac]
                    st.session_state.companies[ac].update({"targets":len(all_t),
                        "on_track":sum(1 for t in all_t if t["status"]=="On Track"),
                        "at_risk":sum(1 for t in all_t if t["status"]=="At Risk"),
                        "lagging":sum(1 for t in all_t if t["status"]=="Lagging")})
                    st.rerun()
    else:
        st.markdown("<div class='esg-card' style='text-align:center;padding:40px;color:#5A8A6A;'><div style='font-size:2rem;'>🎯</div><div style='font-weight:600;'>No targets yet</div></div>", unsafe_allow_html=True)

    # RESET
    st.markdown("---")
    col_reset1, col_reset2 = st.columns([1,4])
    with col_reset1:
        if st.button("🔄 Reset all targets"):
            st.session_state.targets[ac] = []
            st.session_state.companies[ac].update({"targets":0,"on_track":0,"at_risk":0,"lagging":0})
            st.rerun()

# ════════════════════════════════════════════════════════════
# ANALYSIS & INSIGHTS
# ════════════════════════════════════════════════════════════
elif "Analysis" in page:
    st.markdown("<div class='main-header'><h1>📈 Analysis & Insights</h1><p>Scores · Benchmarks · SDG heatmap · Materiality · Risks & Opportunities · Report</p></div>", unsafe_allow_html=True)
    cl = list(st.session_state.companies.keys())
    di = cl.index(st.session_state.current_company) if st.session_state.current_company in cl else 0
    ac = st.selectbox("Active Company", cl, index=di)
    st.session_state.current_company = ac
    cd = st.session_state.companies.get(ac, {})
    industry = cd.get("industry", INDUSTRIES[0])
    e_s, s_s, g_s, ov = cd.get("E_score",0), cd.get("S_score",0), cd.get("G_score",0), cd.get("overall",0)
    grade = cd.get("grade","—")

    tab_ov, tab_ind, tab_sdg, tab_risk, tab_mat, tab_rep = st.tabs(["📊 Overview","🔍 Indicators","🌐 SDG Heatmap","⚡ Risks & Opportunities","📐 Materiality","📄 Report"])

    # ── OVERVIEW ──
    with tab_ov:
        col1,col2,col3,col4 = st.columns([1.5,1,1,1])
        with col1: st.plotly_chart(make_radar(e_s or 55, s_s or 60, g_s or 65), use_container_width=True)
        with col2:
            gc = grade_color(grade)
            st.markdown(f"<div class='metric-card'><div class='value' style='color:{gc};'>{grade}</div><div class='label'>Overall Grade</div><div style='font-size:1.4rem;font-weight:700;color:{C['mid']};margin-top:6px;'>{ov}</div><div style='font-size:.72rem;color:{C['subtle']};'>/ 100</div></div>", unsafe_allow_html=True)
        with col3: st.plotly_chart(make_gauge(e_s or 55,"Environment",C["mid"]), use_container_width=True)
        with col4: st.plotly_chart(make_gauge(s_s or 60,"Social","#4CAF80"), use_container_width=True)

        # Score breakdown note
        st.markdown(f"<div style='font-size:.78rem;color:{C['subtle']};margin:4px 0 12px 0;'>Score = E×40% + S×35% + G×25% · Based on indicator coverage + benchmark performance</div>", unsafe_allow_html=True)

        # Data quality badge
        dq = st.session_state.dq.get(ac, {})
        if dq.get("coverage_pct",0) or dq.get("assured"):
            badge = "dq-badge-assured" if dq.get("assured") and dq.get("coverage_pct",0)>=80 else "dq-badge-partial"
            st.markdown(f"<span class='{badge}'>{'Externally Assured' if dq.get('assured') else 'Unassured'} · {dq.get('coverage_pct',0)}% coverage · {dq.get('assurer','')}</span>", unsafe_allow_html=True)

        # Framework alignment
        st.markdown("<div class='section-label' style='margin-top:16px;'>FRAMEWORK ALIGNMENT ESTIMATE</div>", unsafe_allow_html=True)
        fw_scores = {"GRI":min(100,(e_s+s_s+g_s)//3+5),"CDP":min(100,e_s+3),"SASB":min(100,(e_s+g_s)//2+4),
            "IFRS S1/S2":min(100,e_s-3),"S&P CSA":min(100,ov+2),"GRESB":min(100,(e_s+g_s)//2),"SBTi":min(100,e_s-8)}
        fw_df = pd.DataFrame(list(fw_scores.items()), columns=["Framework","Score"])
        fig_fw = px.bar(fw_df,x="Framework",y="Score",color="Score",
            color_continuous_scale=[[0,"#FEE2E2"],[.4,"#FEF3C7"],[.7,"#DCFCE7"],[1,C["mid"]]],range_color=[0,100])
        fig_fw.update_layout(height=200,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,margin=dict(t=10,b=40,l=10,r=10),coloraxis_showscale=False,
            yaxis=dict(range=[0,105],gridcolor=C["foam"]))
        st.plotly_chart(fig_fw, use_container_width=True)

        # Peer benchmarking
        peers = {k:v for k,v in st.session_state.companies.items() if v.get("industry")==industry and k!=ac}
        if peers:
            st.markdown("<div class='section-label'>PEER BENCHMARKING</div>", unsafe_allow_html=True)
            fig_p = go.Figure()
            fig_p.add_trace(go.Scatterpolar(r=[e_s,s_s,g_s,e_s],theta=["E","S","G","E"],name=ac,
                line=dict(color=C["mid"],width=3),fill="toself",fillcolor=f"rgba(26,107,60,.15)"))
            for pn,pd_data in peers.items():
                fig_p.add_trace(go.Scatterpolar(r=[pd_data["E_score"],pd_data["S_score"],pd_data["G_score"],pd_data["E_score"]],
                    theta=["E","S","G","E"],name=pn,line=dict(color=C["mist"],width=1.5)))
            fig_p.update_layout(polar=dict(radialaxis=dict(range=[0,100],gridcolor=C["mist"])),
                height=280,paper_bgcolor="rgba(0,0,0,0)",margin=dict(t=30,b=10))
            st.plotly_chart(fig_p, use_container_width=True)

    # ── INDICATOR DETAIL ──
    with tab_ind:
        st.markdown("<div class='section-label'>INDICATOR-LEVEL PERFORMANCE</div>", unsafe_allow_html=True)
        for pillar, pname, pcol in [("E","Environmental",C["mid"]),("S","Social","#4CAF80"),("G","Governance","#6B9B7E")]:
            st.markdown(f"<div style='font-weight:600;font-size:.95rem;color:{pcol};margin:12px 0 6px 0;'>{pname}</div>", unsafe_allow_html=True)
            inds = get_indicators(industry, pillar)
            edata = st.session_state.esg_data.get(ac, {}).get(pillar, {})
            for ind_meta in inds:
                iname = ind_meta["name"]
                unit = ind_meta["unit"]
                val_data = edata.get(iname, {})
                cur = float(val_data.get("current",0) or 0)
                prior = float(val_data.get("prior",0) or 0)
                ba, bt = ind_meta.get("benchmark_avg"), ind_meta.get("benchmark_top")
                if not cur: continue
                # Status vs benchmark
                if ba and bt:
                    if unit == "%":
                        perf = "strong" if cur >= bt else ("average" if cur >= ba else "lagging")
                    else:
                        perf = "strong" if cur <= bt else ("average" if cur <= ba else "lagging")
                else:
                    perf = "reported"
                perf_color = {"strong":C["mid"],"average":"#F59E0B","lagging":"#EF4444","reported":"#93C5FD"}.get(perf,"#93C5FD")
                perf_label = {"strong":"▲ Top quartile","average":"~ Industry avg","lagging":"▼ Lagging","reported":"Reported"}.get(perf,"")
                yoy_str = ""
                if prior:
                    yoy = round((cur-prior)/max(abs(prior),0.001)*100,1)
                    trend = "↑" if yoy > 0 else "↓"
                    yoy_str = f"  {trend} {abs(yoy):.1f}% YoY"
                # Find linked target
                linked_target = None
                for t in st.session_state.targets.get(ac,[]):
                    if t.get("indicator","").lower() in iname.lower() or iname.lower() in t.get("indicator","").lower():
                        linked_target = t; break
                with st.expander(f"{'🟢' if perf=='strong' else '🟡' if perf=='average' else '🔴' if perf=='lagging' else '○'}  {iname}  —  {cur:,} {unit}  {yoy_str}"):
                    col1,col2 = st.columns([2,3])
                    with col1:
                        st.markdown(f"""<div class='esg-card' style='padding:14px;'>
                          <div style='font-size:.8rem;color:{C['subtle']};'>Framework refs</div>
                          <div style='font-size:.82rem;margin:4px 0;'>GRI {ind_meta.get('gri','—')} · SASB {ind_meta.get('sasb','—')}</div>
                          <div style='font-size:.82rem;'>CSA: {ind_meta.get('csa','—')}</div>
                          <div style='margin-top:8px;font-size:.82rem;'>
                            <span style='color:{perf_color};font-weight:600;'>{perf_label}</span>
                          </div>
                          {'<div style="font-size:.8rem;margin-top:4px;">Industry avg: <b>'+str(ba)+'</b> · Top quartile: <b>'+str(bt)+'</b> '+unit+'</div>' if ba else ''}
                        </div>""", unsafe_allow_html=True)
                    with col2:
                        if linked_target:
                            st.plotly_chart(make_target_vs_actual_chart(linked_target), use_container_width=True)
                        elif ba:
                            # Mini bar: current vs avg vs top quartile
                            fig_bar = go.Figure()
                            fig_bar.add_trace(go.Bar(x=["This Company","Industry Avg","Top Quartile"],
                                y=[cur, ba, bt], marker_color=[perf_color, "#93C5FD", C["mid"]]))
                            fig_bar.update_layout(height=160, margin=dict(t=10,b=20,l=10,r=10),
                                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                yaxis=dict(gridcolor=C["foam"]), font=dict(family="Inter",size=10))
                            st.plotly_chart(fig_bar, use_container_width=True)
                        # Action insight
                        if linked_target:
                            needed = annual_reduction_needed(linked_target.get("baseline",0), linked_target.get("target_val",0), linked_target.get("baseline_year",2020), linked_target.get("target_year",2030))
                            if needed:
                                st.markdown(f"<div class='strategy-box'>🎯 Need <b>{needed:+,.2f} {unit}/year</b> to reach {linked_target['name']} by {linked_target['target_year']}</div>", unsafe_allow_html=True)

    # ── SDG HEATMAP ──
    with tab_sdg:
        st.markdown("<div class='section-label'>SDG ALIGNMENT HEATMAP</div>", unsafe_allow_html=True)
        relevant_sdgs = INDUSTRY_SDGS.get(industry, [13,12,6,8])
        sdg_html = "".join([f"<span class='sdg-chip' style='background:{SDG_COLORS.get(n,"#999")};'>SDG {n}: {SDG_NAMES.get(n,'')}</span>" for n in relevant_sdgs])
        st.markdown(sdg_html, unsafe_allow_html=True)
        st.plotly_chart(make_sdg_heatmap(ac, st.session_state.companies, st.session_state.esg_data), use_container_width=True)
        # Coverage heatmap
        st.markdown("<div class='section-label' style='margin-top:16px;'>INDICATOR REPORTING COVERAGE</div>", unsafe_allow_html=True)
        coverage_data = []
        for pillar in ["E","S","G"]:
            for ind_meta in get_indicators(industry, pillar):
                val = st.session_state.esg_data.get(ac,{}).get(pillar,{}).get(ind_meta["name"],{})
                cur = float(val.get("current",0) or 0) if isinstance(val,dict) else 0
                prior = float(val.get("prior",0) or 0) if isinstance(val,dict) else 0
                if cur and prior: trend = "improving" if (cur < prior and pillar=="E") or (cur > prior and pillar in ["S","G"]) else ("declining" if (cur > prior and pillar=="E") or (cur < prior and pillar in ["S","G"]) else "stable")
                elif cur: trend = "reported (no prior)"
                else: trend = "not reported"
                coverage_data.append({"Indicator":ind_meta["name"],"Pillar":pillar,"Status":trend})
        if coverage_data:
            df_cov = pd.DataFrame(coverage_data)
            color_map = {"improving":C["mid"],"stable":"#93C5FD","declining":"#EF4444","reported (no prior)":"#F59E0B","not reported":"#E5E7EB"}
            fig_cov = px.bar(df_cov, x="Indicator", y=[1]*len(df_cov), color="Status",
                color_discrete_map=color_map, barmode="stack")
            fig_cov.update_layout(height=180, yaxis=dict(showticklabels=False,title=""),
                xaxis=dict(tickangle=45, tickfont=dict(size=8)),
                legend=dict(orientation="h",y=1.2,font=dict(size=9)),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=40,b=80,l=10,r=10))
            st.plotly_chart(fig_cov, use_container_width=True)

    # ── RISKS & OPPORTUNITIES ──
    with tab_risk:
        st.markdown("<div class='section-label'>TRANSITION & PHYSICAL RISKS BY PILLAR</div>", unsafe_allow_html=True)
        RISK_LIBRARY = {
            "Steel & Metals": {
                "E": [
                    ("🔴 High","Carbon pricing / CBAM","Cost increase on carbon-intensive imports; EU CBAM directly affects steel exports","Accelerate EAF transition; SBTi validation strengthens market position"),
                    ("🟡 Medium","Water scarcity at plant level","Cooling water availability risk in water-stressed geographies","Deploy WRI Aqueduct site-level risk assessment; invest in closed-loop cooling"),
                    ("🟢 Opportunity","Green steel premium","Growing demand for certified low-carbon steel from automotive and construction sectors","Pursue ResponsibleSteel or SteelZero certification; lock in offtake agreements"),
                ],
                "S": [
                    ("🔴 High","Heat stress / physical risk","Rising ambient temperatures increase worker heat illness risk in furnace environments","WBGT monitoring; mandatory NIOSH acclimatisation protocols"),
                    ("🟡 Medium","Community opposition to expansion","Air/water quality concerns can delay planning approvals","Establish community advisory panel; publish air quality monitoring data"),
                ],
                "G": [
                    ("🟡 Medium","Supply chain ESG audit gaps","Unaudited suppliers carry reputational and regulatory (CSRD, LkSG) risk","Expand audit programme to Tier 2; adopt OECD RBC Guidance"),
                    ("🟢 Opportunity","ESG-linked financing","Green bonds and SLLs at lower cost for SBTi-aligned issuers","Set credible milestones; engage relationship banks on sustainability-linked loan framework"),
                ]
            },
            "FMCG / Consumer Goods": {
                "E": [
                    ("🔴 High","Plastic regulation (EPR/SUP)","Extended producer responsibility laws increasing cost of non-recyclable packaging","Shift to monomaterial recyclable packaging; register with national PROs"),
                    ("🟡 Medium","Deforestation-linked commodity risk","EUDR compliance risk for palm oil, cocoa, soy sourcing","Deploy satellite monitoring (Global Forest Watch); achieve RSPO segregated certification"),
                    ("🟢 Opportunity","Product carbon labelling","Early movers on product-level carbon footprint labels gaining retailer preference","Commission ISO 14067 product LCAs for top 10 SKUs"),
                ],
                "S": [
                    ("🟡 Medium","Living wage reputational risk","NGO campaigns on supply chain wage gaps directly impact brand value","Publish Anker-methodology living wage gap assessment; commit to closure timeline"),
                ],
                "G": [
                    ("🟢 Opportunity","Consumer trust premium","ESG transparency correlated with consumer NPS and willingness-to-pay in key segments","Publish GRI-aligned sustainability report; improve CDP disclosure score"),
                ]
            }
        }
        default_risks = {
            "E":[("🟡 Medium","Carbon pricing exposure","Rising carbon cost directly impacts operating margins","Reduce emissions intensity; explore internal carbon pricing"),
                 ("🟢 Opportunity","Energy efficiency gains","Operational efficiency improvements reduce both cost and emissions","ISO 50001 audit; renewable PPA procurement")],
            "S":[("🟡 Medium","Talent risk","Poor ESG reputation increases employee acquisition/retention cost","Publish pay equity data; improve safety record"),
                 ("🟢 Opportunity","Social licence","Strong community relations reduces permitting and regulatory friction","Community investment programme; stakeholder advisory panel")],
            "G":[("🟡 Medium","Governance scrutiny","Institutional investors apply ESG governance screens to investment decisions","Board skills matrix; ESG committee; TCFD-aligned disclosure"),
                 ("🟢 Opportunity","ESG-linked capital","Better ESG scores → lower cost of green/SLL financing","Set SBTi target; engage banks on SLL framework")]
        }
        risks = RISK_LIBRARY.get(industry, {})
        for pillar, pname in [("E","Environmental"),("S","Social"),("G","Governance")]:
            pillar_risks = risks.get(pillar, default_risks.get(pillar,[]))
            st.markdown(f"<div style='font-weight:600;margin:12px 0 6px 0;color:{C['mid']};'>{pname}</div>", unsafe_allow_html=True)
            for severity, risk_name, description, mitigation in pillar_risks:
                col1, col2 = st.columns([1,3])
                with col1: st.markdown(f"<div style='padding-top:10px;font-size:.85rem;font-weight:600;'>{severity}</div>", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""<div class='esg-card' style='padding:12px;'>
                      <div style='font-weight:600;font-size:.88rem;'>{risk_name}</div>
                      <div style='font-size:.82rem;color:{C['subtle']};margin:3px 0;'>{description}</div>
                      <div class='strategy-box' style='margin:4px 0 0 0;font-size:.8rem;'>💡 {mitigation}</div>
                    </div>""", unsafe_allow_html=True)

    # ── MATERIALITY MATRIX ──
    with tab_mat:
        st.markdown("<div class='section-label'>MATERIALITY MATRIX — IMPACT vs FINANCIAL MATERIALITY</div>", unsafe_allow_html=True)
        # Materiality scores (industry-preset)
        MATERIALITY = {
            "Steel & Metals": [
                ("Climate & GHG emissions","E",9,9),("Energy efficiency","E",7,8),("Water stewardship","E",6,7),
                ("Circular economy / scrap","E",7,7),("Air quality","E",8,6),("Biodiversity","E",5,4),
                ("Worker health & safety","S",9,9),("Heat stress","S",7,6),("Community relations","S",6,5),
                ("Supply chain labour","S",5,6),("Board governance","G",6,8),("Anti-corruption","G",5,7),
                ("ESG-linked pay","G",4,6),("Tax transparency","G",4,5)
            ],
            "FMCG / Consumer Goods": [
                ("Packaging & plastics","E",9,9),("Climate & GHG","E",8,8),("Sustainable sourcing","E",9,7),
                ("Water use","E",6,6),("Waste","E",6,5),("Product health","S",8,9),
                ("Supply chain labour","S",9,8),("Diversity & inclusion","S",6,7),
                ("Responsible marketing","G",7,7),("Data privacy","G",6,8),("Governance","G",5,7)
            ]
        }
        mat_data = MATERIALITY.get(industry, [
            ("Climate & GHG","E",8,8),("Energy","E",7,7),("Water","E",6,6),("Waste","E",5,5),
            ("Safety","S",8,8),("Diversity","S",6,6),("Community","S",5,5),
            ("Governance","G",7,7),("Anti-corruption","G",6,6)
        ])
        df_mat = pd.DataFrame(mat_data, columns=["Topic","Pillar","Impact","Financial Materiality"])
        colors_mat = {p: col for p,col in [("E",C["mid"]),("S","#4CAF80"),("G","#6B9B7E")]}
        fig_mat = go.Figure()
        for pillar in ["E","S","G"]:
            sub = df_mat[df_mat["Pillar"]==pillar]
            fig_mat.add_trace(go.Scatter(x=sub["Financial Materiality"],y=sub["Impact"],mode="markers+text",
                name={"E":"Environmental","S":"Social","G":"Governance"}[pillar],
                marker=dict(size=14,color=colors_mat[pillar],line=dict(width=1,color="white")),
                text=sub["Topic"],textposition="top center",textfont=dict(size=9)))
        fig_mat.update_layout(height=420, xaxis=dict(title="Financial Materiality",range=[0,11],gridcolor=C["foam"]),
            yaxis=dict(title="Impact on Environment/Society",range=[0,11],gridcolor=C["foam"]),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=20,b=60,l=60,r=20), font=dict(family="Inter",size=10),
            legend=dict(orientation="h",y=-0.15))
        # Quadrant labels
        for x,y,lbl in [(7.5,7.5,"HIGH PRIORITY"),(2.5,7.5,"IMPACT-LED"),(7.5,2.5,"FINANCIALLY LED"),(2.5,2.5,"MONITOR")]:
            fig_mat.add_annotation(x=x,y=y,text=lbl,showarrow=False,
                font=dict(size=8,color=C["mist"]),opacity=0.6)
        fig_mat.add_shape(type="line",x0=5,x1=5,y0=0,y1=11,line=dict(color=C["mist"],width=1,dash="dot"))
        fig_mat.add_shape(type="line",x0=0,x1=11,y0=5,y1=5,line=dict(color=C["mist"],width=1,dash="dot"))
        st.plotly_chart(fig_mat, use_container_width=True)
        st.markdown(f"<div style='font-size:.78rem;color:{C['subtle']};'>Double materiality: X-axis = financial risk/opportunity to the company · Y-axis = impact on environment/society. Top-right quadrant = highest priority for reporting and action.</div>", unsafe_allow_html=True)

    # ── REPORT ──
    with tab_rep:
        st.markdown("<div class='section-label'>GENERATE COMPANY REPORT</div>", unsafe_allow_html=True)
        report_year = cd.get("report_year", CURRENT_YEAR-1)
        targets = st.session_state.targets.get(ac,[])
        dq = st.session_state.dq.get(ac,{})
        on_track = sum(1 for t in targets if t["status"]=="On Track")
        edata = st.session_state.esg_data.get(ac,{})
        total_filled = sum(1 for p in ["E","S","G"] for v in edata.get(p,{}).values() if isinstance(v,dict) and v.get("current",0))
        total_ind = sum(len(get_indicators(industry,p)) for p in ["E","S","G"])

        report_md = f"""# ESG Compass Report — {ac}
**Reporting Year:** {report_year}  |  **Industry:** {industry}  |  **Country:** {cd.get('country','')}  
**Frameworks:** {', '.join(cd.get('frameworks',[]))}  |  **Generated:** {datetime.now().strftime('%d %B %Y')}

---

## Executive Summary

{ac} has achieved an overall ESG score of **{ov}/100** (Grade: **{grade}**), reflecting performance across Environmental ({e_s}/100), Social ({s_s}/100), and Governance ({g_s}/100) dimensions. Data coverage stands at **{round(total_filled/max(total_ind,1)*100)}%** ({total_filled} of {total_ind} indicators reported). {'Data has been externally assured at ' + dq.get('assurance_level','') + ' level by ' + dq.get('assurer','') + '.' if dq.get('assured') else 'Data has not been externally assured.'}

Of **{len(targets)} sustainability targets** tracked, **{on_track} are On Track**, {sum(1 for t in targets if t['status']=='At Risk')} At Risk, and {sum(1 for t in targets if t['status']=='Lagging')} Lagging.

---

## ESG Performance Summary

| Dimension | Score | Grade | Weight |
|---|---|---|---|
| Environmental | {e_s} | {score_to_grade(e_s)} | 40% |
| Social | {s_s} | {score_to_grade(s_s)} | 35% |
| Governance | {g_s} | {score_to_grade(g_s)} | 25% |
| **Overall** | **{ov}** | **{grade}** | — |

---

## Target Progress

| Target | Category | Status | Actual % | Expected % | Gap |
|---|---|---|---|---|---|
"""
        for t in targets:
            gap = round(float(t.get("target_val",0)) - float(t.get("current",0)), 2)
            report_md += f"| {t['name']} | {t['category']} | {t['status']} | {t.get('actual_pct',0)}% | {t.get('expected_pct',0)}% | {gap:+,.2f} {t.get('unit','')} |\n"

        report_md += f"""
---

## SDG Alignment

{ac} ({industry}) contributes primarily to the following UN Sustainable Development Goals:

{chr(10).join([f"- **SDG {n}: {SDG_NAMES.get(n,'')}**" for n in INDUSTRY_SDGS.get(industry,[])])}

---

## Data Quality

- **Coverage:** {dq.get('coverage_pct',0)}% of operations
- **External assurance:** {'Yes — ' + dq.get('assurance_level','') + ' assurance by ' + dq.get('assurer','') if dq.get('assured') else 'Not assured'}
- **Reporting frameworks:** {', '.join(cd.get('frameworks',[]))}

---

## Key Recommendations

1. {'Prioritise indicator data coverage — currently at ' + str(round(total_filled/max(total_ind,1)*100)) + '%. Higher coverage improves score and framework alignment.' if total_filled/max(total_ind,1) < 0.7 else 'Maintain data coverage and focus on benchmark performance improvement.'}
2. {'Address ' + str(sum(1 for t in targets if t["status"]=="Lagging")) + ' lagging target(s) with detailed action plans and interim milestones.' if any(t["status"]=="Lagging" for t in targets) else 'All targets on track or at risk — maintain current trajectory.'}
3. {'Pursue external assurance to strengthen data credibility and framework compliance.' if not dq.get('assured') else 'Expand assurance scope to cover ' + str(100 - dq.get('coverage_pct',0)) + '% of remaining operations.'}
4. Consider SBTi target submission for climate commitments to access ESG-linked financing at preferential rates.

---

*Generated by ESG Compass · GRI · SASB · CDP · IFRS S1/S2 · S&P CSA · GRESB · SBTi aligned*
"""
        st.markdown(report_md)
        st.download_button("⬇️ Download Report (.md)", data=report_md.encode(),
            file_name=f"ESGCompass_Report_{ac.replace(' ','_')}_{report_year}.md",
            mime="text/markdown")
