import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json, io, math, re, base64, requests
from datetime import datetime

CURRENT_YEAR = datetime.now().year

st.set_page_config(
    page_title="Viridis · ESG Intelligence",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── DARK PREMIUM PALETTE ─────────────────────────────────────────────────
C = {
    "bg":         "#0A0F0D",   # near-black green-tinted
    "surface":    "#111916",   # card background
    "surface2":   "#162018",   # slightly lighter surface
    "border":     "#1E3028",   # subtle borders
    "border2":    "#2A4035",   # slightly brighter border
    "deep":       "#0D3D26",   # dark green
    "mid":        "#1A6B3C",   # core green
    "leaf":       "#2ECC71",   # bright accent green
    "mint":       "#4ADE80",   # lighter accent
    "mist":       "#6EE7A0",   # pale green text
    "foam":       "#A7F3C4",   # very light green
    "text":       "#E8F5EC",   # primary text (near white, green tint)
    "subtext":    "#8BAF98",   # secondary text
    "dim":        "#4A6B58",   # dimmed text
    "amber":      "#F59E0B",   # warning
    "red":        "#EF4444",   # danger
    "blue":       "#60A5FA",   # info
    "white":      "#FFFFFF",
}

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

*, html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif !important;
    background-color: {C['bg']};
    color: {C['text']};
}}

/* ── SCROLLBAR ── */
::-webkit-scrollbar {{ width: 4px; height: 4px; }}
::-webkit-scrollbar-track {{ background: {C['bg']}; }}
::-webkit-scrollbar-thumb {{ background: {C['border2']}; border-radius: 2px; }}

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {{
    background: {C['surface']} !important;
    border-right: 1px solid {C['border']} !important;
}}
section[data-testid="stSidebar"] * {{ color: {C['text']} !important; }}
section[data-testid="stSidebar"] .stRadio label {{
    color: {C['subtext']} !important;
    font-size: .88rem;
    padding: 6px 10px;
    border-radius: 8px;
    transition: all .15s;
}}
section[data-testid="stSidebar"] .stRadio label:hover {{
    background: {C['border']};
    color: {C['foam']} !important;
}}

/* ── LOGO BLOCK ── */
.vrd-logo {{
    padding: 20px 16px 24px 16px;
    border-bottom: 1px solid {C['border']};
    margin-bottom: 16px;
}}
.vrd-logo-mark {{
    display: flex; align-items: center; gap: 10px;
}}
.vrd-logo-icon {{
    width: 36px; height: 36px; border-radius: 10px;
    background: linear-gradient(135deg, {C['mid']}, {C['leaf']});
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem; flex-shrink: 0;
}}
.vrd-logo-name {{
    font-size: 1.25rem; font-weight: 800; color: {C['foam']};
    letter-spacing: -.5px;
}}
.vrd-logo-sub {{
    font-size: .68rem; color: {C['dim']}; letter-spacing: 2px;
    text-transform: uppercase; margin-top: 2px;
}}

/* ── PAGE HEADER ── */
.vrd-header {{
    background: linear-gradient(135deg, {C['surface']} 0%, {C['surface2']} 100%);
    border: 1px solid {C['border']};
    border-radius: 16px;
    padding: 28px 36px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}}
.vrd-header::before {{
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, {C['mid']}22 0%, transparent 70%);
    border-radius: 50%;
}}
.vrd-header::after {{
    content: '';
    position: absolute;
    bottom: -60px; left: 20%;
    width: 300px; height: 120px;
    background: radial-gradient(ellipse, {C['leaf']}0A 0%, transparent 70%);
}}
.vrd-header h1 {{
    color: {C['foam']};
    font-size: 1.8rem; font-weight: 800;
    margin: 0 0 4px 0; letter-spacing: -.5px;
}}
.vrd-header p {{
    color: {C['subtext']}; margin: 0; font-size: .88rem;
}}
.vrd-header-badge {{
    display: inline-block;
    background: {C['mid']}33;
    border: 1px solid {C['mid']};
    color: {C['mist']};
    border-radius: 20px; padding: 2px 10px;
    font-size: .7rem; font-weight: 600;
    margin-right: 4px; margin-top: 8px;
}}

/* ── CARDS ── */
.vrd-card {{
    background: {C['surface']};
    border: 1px solid {C['border']};
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 14px;
    transition: border-color .2s;
}}
.vrd-card:hover {{ border-color: {C['border2']}; }}

.vrd-metric {{
    background: {C['surface']};
    border: 1px solid {C['border']};
    border-radius: 12px;
    padding: 18px 16px;
    text-align: center;
}}
.vrd-metric .val {{
    font-size: 2rem; font-weight: 800;
    font-variant-numeric: tabular-nums;
    line-height: 1;
}}
.vrd-metric .lbl {{
    font-size: .72rem; color: {C['subtext']};
    text-transform: uppercase; letter-spacing: 1px;
    margin-top: 5px;
}}

/* ── COMPANY CARD (dashboard) ── */
.vrd-co-card {{
    background: {C['surface']};
    border: 1px solid {C['border']};
    border-radius: 16px;
    padding: 20px;
    transition: all .2s;
    cursor: pointer;
    position: relative;
    overflow: hidden;
}}
.vrd-co-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 16px 16px 0 0;
}}
.vrd-co-card.grade-a::before {{ background: linear-gradient(90deg, {C['leaf']}, {C['mint']}); }}
.vrd-co-card.grade-b::before {{ background: linear-gradient(90deg, {C['amber']}, #FCD34D); }}
.vrd-co-card.grade-c::before {{ background: linear-gradient(90deg, {C['red']}, #F87171); }}
.vrd-co-card:hover {{ border-color: {C['mid']}; transform: translateY(-2px); box-shadow: 0 8px 32px rgba(0,0,0,.4); }}

/* ── SECTION LABEL ── */
.vrd-label {{
    font-size: .68rem; text-transform: uppercase;
    letter-spacing: 2px; color: {C['dim']};
    font-weight: 600; margin-bottom: 8px;
    font-family: 'JetBrains Mono', monospace !important;
}}

/* ── BADGES ── */
.badge-green {{ background: {C['mid']}33; color: {C['mist']}; border: 1px solid {C['mid']}66; border-radius: 20px; padding: 2px 10px; font-size: .72rem; font-weight: 600; display: inline-block; }}
.badge-amber {{ background: {C['amber']}22; color: {C['amber']}; border: 1px solid {C['amber']}44; border-radius: 20px; padding: 2px 10px; font-size: .72rem; font-weight: 600; display: inline-block; }}
.badge-red   {{ background: {C['red']}22;   color: {C['red']};   border: 1px solid {C['red']}44;   border-radius: 20px; padding: 2px 10px; font-size: .72rem; font-weight: 600; display: inline-block; }}
.badge-blue  {{ background: {C['blue']}22;  color: {C['blue']};  border: 1px solid {C['blue']}44;  border-radius: 20px; padding: 2px 10px; font-size: .72rem; font-weight: 600; display: inline-block; }}
.badge-fw    {{ background: {C['surface2']}; color: {C['subtext']}; border: 1px solid {C['border']}; border-radius: 6px; padding: 2px 8px; font-size: .7rem; display: inline-block; margin: 2px; }}

/* ── STRATEGY / ALERT ── */
.vrd-strategy {{
    background: {C['mid']}18;
    border-left: 3px solid {C['leaf']};
    border-radius: 0 10px 10px 0;
    padding: 12px 16px; margin: 8px 0;
    font-size: .85rem;
}}
.vrd-alert-warn {{
    background: {C['amber']}18;
    border-left: 3px solid {C['amber']};
    border-radius: 0 10px 10px 0;
    padding: 10px 14px; margin: 6px 0; font-size: .84rem; color: {C['amber']};
}}
.vrd-alert-ok {{
    background: {C['leaf']}18;
    border-left: 3px solid {C['leaf']};
    border-radius: 0 10px 10px 0;
    padding: 10px 14px; margin: 6px 0; font-size: .84rem; color: {C['mist']};
}}
.vrd-alert-err {{
    background: {C['red']}18;
    border-left: 3px solid {C['red']};
    border-radius: 0 10px 10px 0;
    padding: 10px 14px; margin: 6px 0; font-size: .84rem; color: {C['red']};
}}

/* ── AI EXTRACTION BOX ── */
.vrd-ai-box {{
    background: linear-gradient(135deg, {C['surface2']}, {C['surface']});
    border: 1px solid {C['mid']}66;
    border-radius: 14px;
    padding: 20px 24px;
    margin: 12px 0;
}}
.vrd-ai-header {{
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 12px;
}}
.vrd-ai-dot {{
    width: 8px; height: 8px; border-radius: 50%;
    background: {C['leaf']};
    box-shadow: 0 0 8px {C['leaf']};
    animation: pulse 2s infinite;
}}
@keyframes pulse {{
    0%, 100% {{ opacity: 1; transform: scale(1); }}
    50% {{ opacity: .5; transform: scale(.85); }}
}}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {{
    background: {C['surface']} !important;
    border: 1px solid {C['border']} !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 2px !important;
}}
.stTabs [data-baseweb="tab"] {{
    border-radius: 7px !important;
    color: {C['subtext']} !important;
    font-weight: 500 !important;
    font-size: .85rem !important;
}}
.stTabs [aria-selected="true"] {{
    background: {C['mid']} !important;
    color: {C['foam']} !important;
}}

/* ── INPUTS ── */
.stTextInput input, .stNumberInput input, .stTextArea textarea,
.stSelectbox > div > div {{
    background: {C['surface2']} !important;
    border: 1px solid {C['border2']} !important;
    color: {C['text']} !important;
    border-radius: 8px !important;
}}
.stSelectbox > div > div:hover {{ border-color: {C['mid']} !important; }}

/* ── BUTTONS ── */
.stButton > button {{
    background: linear-gradient(135deg, {C['mid']}, {C['deep']}) !important;
    color: {C['foam']} !important;
    border: 1px solid {C['mid']} !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: .85rem !important;
    transition: all .15s !important;
}}
.stButton > button:hover {{
    background: linear-gradient(135deg, {C['leaf']}, {C['mid']}) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px {C['mid']}44 !important;
}}

/* ── EXPANDER ── */
div[data-testid="stExpander"] {{
    background: {C['surface']} !important;
    border: 1px solid {C['border']} !important;
    border-radius: 10px !important;
}}
div[data-testid="stExpander"] summary {{
    color: {C['text']} !important;
}}

/* ── MONO NUMBERS ── */
.mono {{ font-family: 'JetBrains Mono', monospace !important; }}

/* ── DECORATIVE ELEMENTS ── */
.vrd-divider {{
    height: 1px;
    background: linear-gradient(90deg, transparent, {C['border2']}, transparent);
    margin: 16px 0;
}}

/* ── SDG CHIP ── */
.sdg-chip {{
    display: inline-block; border-radius: 8px;
    padding: 3px 10px; font-size: .72rem;
    font-weight: 700; margin: 2px; color: white;
    letter-spacing: .3px;
}}

/* ── PROGRESS BAR CUSTOM ── */
.vrd-progress {{
    background: {C['border']};
    border-radius: 4px; height: 5px; overflow: hidden;
}}
.vrd-progress-fill {{
    height: 5px; border-radius: 4px;
    transition: width .3s;
}}

/* ── DATAFRAME ── */
.stDataFrame {{ border-radius: 10px !important; overflow: hidden !important; }}
</style>
""", unsafe_allow_html=True)

# ─── DATA ────────────────────────────────────────────────────────────────────
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
        ],
        "S": [
            {"name":"LTIFR","unit":"per 1M hrs","gri":"403-9","sasb":"EM-IS-320a.1","csa":"H&S","min_val":0,"max_val":20,"benchmark_avg":2.1,"benchmark_top":0.4},
            {"name":"Fatalities","unit":"number","gri":"403-9","sasb":"EM-IS-320a.1","csa":"H&S","min_val":0,"max_val":50,"benchmark_avg":1,"benchmark_top":0},
            {"name":"Heat stress incidents","unit":"number","gri":"403-10","sasb":"EM-IS-320a.1","csa":"H&S","min_val":0,"max_val":500,"benchmark_avg":12,"benchmark_top":0},
            {"name":"Women in total workforce","unit":"%","gri":"405-1","sasb":"—","csa":"Human Capital Dev","min_val":0,"max_val":100,"benchmark_avg":9,"benchmark_top":22},
            {"name":"Women in management","unit":"%","gri":"405-1","sasb":"—","csa":"Human Capital Dev","min_val":0,"max_val":100,"benchmark_avg":11,"benchmark_top":28},
            {"name":"Training hours per employee","unit":"hrs/year","gri":"404-1","sasb":"—","csa":"Human Capital Dev","min_val":0,"max_val":500,"benchmark_avg":32,"benchmark_top":68},
            {"name":"Community grievances resolved","unit":"%","gri":"413-1","sasb":"EM-MM-210a.2","csa":"Local Communities","min_val":0,"max_val":100,"benchmark_avg":74,"benchmark_top":97},
            {"name":"Supplier ESG audits coverage","unit":"%","gri":"414-2","sasb":"EM-IS-430a.1","csa":"Supply Chain Mgmt","min_val":0,"max_val":100,"benchmark_avg":38,"benchmark_top":85},
        ],
        "G": [
            {"name":"Board independence","unit":"%","gri":"2-9","sasb":"—","csa":"Corporate Governance","min_val":0,"max_val":100,"benchmark_avg":52,"benchmark_top":78},
            {"name":"Women on board","unit":"%","gri":"405-1","sasb":"—","csa":"Corporate Governance","min_val":0,"max_val":100,"benchmark_avg":22,"benchmark_top":40},
            {"name":"ESG-linked executive pay","unit":"%","gri":"2-19","sasb":"—","csa":"Corporate Governance","min_val":0,"max_val":100,"benchmark_avg":18,"benchmark_top":38},
            {"name":"Anti-corruption training completion","unit":"%","gri":"205-2","sasb":"—","csa":"Business Ethics","min_val":0,"max_val":100,"benchmark_avg":82,"benchmark_top":100},
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
            {"name":"Sustainably-sourced palm oil","unit":"%","gri":"308-1","sasb":"FB-AG-430a.2","csa":"Supply Chain Mgmt","min_val":0,"max_val":100,"benchmark_avg":72,"benchmark_top":100},
            {"name":"Manufacturing waste to landfill","unit":"%","gri":"306-5","sasb":"CG-HP-150a.1","csa":"Operational Eco-Efficiency","min_val":0,"max_val":100,"benchmark_avg":8,"benchmark_top":0},
        ],
        "S": [
            {"name":"LTIFR","unit":"per 1M hrs","gri":"403-9","sasb":"—","csa":"H&S","min_val":0,"max_val":10,"benchmark_avg":0.9,"benchmark_top":0.2},
            {"name":"Women in management","unit":"%","gri":"405-1","sasb":"—","csa":"Human Capital Dev","min_val":0,"max_val":100,"benchmark_avg":38,"benchmark_top":52},
            {"name":"Supplier living wage coverage","unit":"%","gri":"2-30","sasb":"CG-HP-430a.1","csa":"Supply Chain Mgmt","min_val":0,"max_val":100,"benchmark_avg":28,"benchmark_top":72},
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
    ],
    "G": [
        {"name":"Board independence","unit":"%","gri":"2-9","sasb":"—","csa":"Corporate Governance","min_val":0,"max_val":100,"benchmark_avg":None,"benchmark_top":None},
        {"name":"Women on board","unit":"%","gri":"405-1","sasb":"—","csa":"Corporate Governance","min_val":0,"max_val":100,"benchmark_avg":None,"benchmark_top":None},
        {"name":"ESG-linked executive pay","unit":"%","gri":"2-19","sasb":"—","csa":"Corporate Governance","min_val":0,"max_val":100,"benchmark_avg":None,"benchmark_top":None},
        {"name":"Anti-corruption training completion","unit":"%","gri":"205-2","sasb":"—","csa":"Business Ethics","min_val":0,"max_val":100,"benchmark_avg":None,"benchmark_top":None},
        {"name":"Supply chain ESG audits","unit":"%","gri":"414-2","sasb":"—","csa":"Supply Chain Mgmt","min_val":0,"max_val":100,"benchmark_avg":None,"benchmark_top":None},
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
    return INDICATOR_LIBRARY.get(industry, {}).get(pillar, DEFAULT_INDICATORS.get(pillar, []))

def score_to_grade(s):
    for t, g in [(85,"A+"),(78,"A"),(72,"A-"),(65,"B+"),(58,"B"),(50,"B-"),(42,"C+"),(35,"C")]:
        if s >= t: return g
    return "D"

def grade_color(g):
    if g.startswith("A"): return C["leaf"]
    if g.startswith("B"): return C["amber"]
    return C["red"]

def grade_class(g):
    if g.startswith("A"): return "grade-a"
    if g.startswith("B"): return "grade-b"
    return "grade-c"

def calc_expected_progress(baseline_year, target_year):
    total = max(1, target_year - baseline_year)
    elapsed = max(0, CURRENT_YEAR - baseline_year)
    return min(100, round(elapsed / total * 100, 1))

def calc_actual_progress(baseline, target, current):
    try:
        b, t, c = float(baseline), float(target), float(current)
        if abs(t - b) < 1e-9: return 0
        return min(100, round(abs(c - b) / abs(t - b) * 100, 1))
    except: return 0

def get_status(actual, expected):
    if actual >= expected * 0.90: return "On Track"
    if actual >= expected * 0.50: return "At Risk"
    return "Lagging"

def validate_target(category, target_year, baseline_year):
    issues, suggestions, sbti_ok = [], [], False
    ytt = target_year - CURRENT_YEAR
    if target_year <= CURRENT_YEAR: issues.append("Target year has already passed.")
    if ytt > 30: issues.append("Target beyond 30 years — add interim milestones every 5 years.")
    if "Net Zero" in category or "Carbon Neutral" in category:
        if target_year <= 2050: sbti_ok = True; suggestions.append("✅ Aligns with IPCC 1.5°C net-zero-by-2050 pathway.")
        else: issues.append("Net zero beyond 2050 does not align with IPCC 1.5°C.")
        suggestions.append("Scope 1+2+3 must be covered. Residual emissions offset by verified carbon removals only.")
    elif "SBTi" in category:
        if 5 <= ytt <= 15: sbti_ok = True; suggestions.append("✅ Timeframe consistent with SBTi near-term validation.")
        else: issues.append("SBTi near-term targets should be 5-10 years from submission.")
        suggestions.append("Minimum 4.2% absolute reduction/year for 1.5°C cross-sector pathway.")
    elif "Renewable Energy" in category:
        if target_year <= 2035: suggestions.append("✅ Aligns with RE100 and IEA NZE scenario.")
        else: issues.append("100% renewable post-2035 lags IEA NZE trajectory.")
    elif "Water" in category:
        suggestions.append("Set context-based target with WRI Aqueduct basin-level stress data.")
    if CURRENT_YEAR - baseline_year > 5:
        issues.append(f"Baseline year ({baseline_year}) is over 5 years old — consider restating.")
    return issues, suggestions, sbti_ok

def annual_change_needed(baseline, target, target_year):
    try:
        years = target_year - CURRENT_YEAR
        if years <= 0: return None
        return round((float(target) - float(baseline)) / years, 2)
    except: return None

def flag_value(val, meta):
    flags = []
    try:
        v = float(val)
        mn, mx = meta.get("min_val", 0), meta.get("max_val", 1e12)
        if v < mn: flags.append(f"Below minimum plausible ({mn:,})")
        if v > mx: flags.append(f"Exceeds maximum plausible ({mx:,.0f}) — verify")
        if meta.get("unit") == "%" and (v < 0 or v > 100): flags.append("Percentage must be 0–100")
    except: pass
    return flags

# ─── AI EXTRACTION ────────────────────────────────────────────────────────────
def extract_text_from_pdf(pdf_bytes):
    try:
        import fitz
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text[:50000]  # cap at 50k chars to stay within context
    except Exception as e:
        return f"Error reading PDF: {e}"

def fetch_url_text(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; Viridis ESG Bot)"}
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        # Strip HTML tags roughly
        text = re.sub(r'<[^>]+>', ' ', r.text)
        text = re.sub(r'\s+', ' ', text)
        return text[:50000]
    except Exception as e:
        return f"Error fetching URL: {e}"

def run_ai_extraction(document_text, industry, indicators_list, api_key):
    """Call Claude API to extract ESG indicator values from document text."""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)

        indicator_names = "\n".join([f"- {m['name']} (unit: {m['unit']})" for m in indicators_list])

        prompt = f"""You are an expert ESG data analyst. I have provided text from a company's sustainability or annual report. 
The company operates in the {industry} industry.

Your task: extract the most recent reported values for each of these ESG indicators from the document text. 
Also identify any sustainability targets the company has committed to.

INDICATORS TO EXTRACT:
{indicator_names}

DOCUMENT TEXT:
{document_text}

Respond ONLY with a valid JSON object in exactly this format (no markdown, no explanation, just JSON):
{{
  "company_name": "extracted company name or null",
  "reporting_year": "extracted reporting year or null",
  "indicators": {{
    "Indicator Name": {{
      "value": numeric_value_or_null,
      "unit": "unit as found in report",
      "confidence": "high/medium/low",
      "source_text": "brief quote or description of where this was found"
    }}
  }},
  "targets": [
    {{
      "name": "target name",
      "indicator": "which indicator this relates to",
      "target_value": numeric_or_null,
      "target_year": year_integer_or_null,
      "baseline_year": year_integer_or_null,
      "baseline_value": numeric_or_null,
      "category": "Net Zero / Carbon Neutral or SBTi or 100% Renewable Energy or Custom",
      "source_text": "brief description"
    }}
  ],
  "notes": "any important caveats or observations about data quality"
}}

If a value cannot be found with reasonable confidence, set value to null. Do not invent numbers."""

        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = message.content[0].text.strip()
        # Clean up any accidental markdown fences
        raw = re.sub(r'^```json\s*', '', raw)
        raw = re.sub(r'^```\s*', '', raw)
        raw = re.sub(r'```\s*$', '', raw)
        return json.loads(raw)
    except json.JSONDecodeError as e:
        return {"error": f"AI returned invalid JSON: {e}", "raw": raw[:500]}
    except Exception as e:
        return {"error": str(e)}

# ─── CHARTS ──────────────────────────────────────────────────────────────────
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color=C["subtext"], size=10),
    margin=dict(t=20, b=20, l=20, r=20),
)

def mini_radar(e, s, g, size=180):
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=[e, s, g, e], theta=["E", "S", "G", "E"],
        fill="toself",
        fillcolor=f"rgba(46,204,113,0.15)",
        line=dict(color=C["leaf"], width=2)
    ))
    fig.update_layout(**CHART_LAYOUT,
        polar=dict(
            radialaxis=dict(visible=True, range=[0,100], tickfont=dict(size=8, color=C["dim"]), gridcolor=C["border"]),
            angularaxis=dict(tickfont=dict(size=9, color=C["subtext"])),
            bgcolor="rgba(0,0,0,0)"
        ),
        showlegend=False, height=size)
    return fig

def gauge_chart(value, title, color=None, max_val=100):
    col = color or C["leaf"]
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=value,
        title={"text": title, "font": {"size": 11, "color": C["subtext"]}},
        number={"font": {"size": 22, "color": col}},
        gauge={
            "axis": {"range": [0, max_val], "tickcolor": C["dim"]},
            "bar": {"color": col, "thickness": 0.65},
            "bgcolor": C["border"],
            "borderwidth": 0,
            "steps": [
                {"range": [0, 40], "color": "#2D1515"},
                {"range": [40, 65], "color": "#2D2A0F"},
                {"range": [65, 85], "color": "#0F2D1A"},
                {"range": [85, 100], "color": "#1A4A2A"},
            ]
        }
    ))
    fig.update_layout(**CHART_LAYOUT, height=165, margin=dict(t=40, b=10, l=20, r=20))
    return fig

def target_progress_chart(t):
    b = float(t.get("baseline", 0))
    tv = float(t.get("target_val", 0))
    cur = float(t.get("current", 0))
    ep = calc_expected_progress(t.get("baseline_year", 2020), t.get("target_year", 2030))
    expected_val = round(b + (tv - b) * ep / 100, 2)
    sc = {C["leaf"]: "On Track", C["amber"]: "At Risk", C["red"]: "Lagging"
          }.get(t.get("status",""), C["leaf"])
    status_color = C["leaf"] if t.get("status") == "On Track" else (C["amber"] if t.get("status") == "At Risk" else C["red"])
    fig = go.Figure()
    for label, val, color in [
        (f"Baseline ({t.get('baseline_year','')})", b, C["dim"]),
        ("Current", cur, status_color),
        ("Expected Now", expected_val, C["blue"]),
        (f"Target ({t.get('target_year','')})", tv, C["mid"]),
    ]:
        fig.add_trace(go.Bar(x=[label], y=[val], marker_color=color, name=label,
            marker=dict(line=dict(width=0)), width=0.5))
    fig.update_layout(**CHART_LAYOUT,
        barmode="group", height=220,
        yaxis=dict(gridcolor=C["border"], color=C["subtext"]),
        xaxis=dict(color=C["subtext"]),
        legend=dict(orientation="h", y=-0.3, font=dict(size=9)),
        margin=dict(t=10, b=60, l=50, r=10))
    return fig

# ─── SESSION STATE ────────────────────────────────────────────────────────────
if "companies" not in st.session_state: st.session_state.companies = dict(SAMPLE_COMPANIES)
if "current_company" not in st.session_state: st.session_state.current_company = None
if "esg_data" not in st.session_state: st.session_state.esg_data = {}
if "targets" not in st.session_state: st.session_state.targets = {}
if "dq" not in st.session_state: st.session_state.dq = {}
if "ai_results" not in st.session_state: st.session_state.ai_results = {}

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div class="vrd-logo">
      <div class="vrd-logo-mark">
        <div class="vrd-logo-icon">🌿</div>
        <div>
          <div class="vrd-logo-name">Viridis</div>
          <div class="vrd-logo-sub">ESG Intelligence</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="vrd-label" style="padding: 0 8px;">NAVIGATION</div>', unsafe_allow_html=True)
    page = st.radio("", [
        "⬡  Dashboard",
        "🏢  Company Setup",
        "🤖  AI Data Extraction",
        "📊  Data Input",
        "🎯  Targets",
        "📈  Analysis & Insights",
    ], label_visibility="collapsed")

    st.markdown('<div class="vrd-divider" style="margin: 16px 8px;"></div>', unsafe_allow_html=True)

    if st.session_state.current_company:
        cd = st.session_state.companies.get(st.session_state.current_company, {})
        gc = grade_color(cd.get("grade", "—"))
        st.markdown(f"""<div style="padding: 10px 8px;">
          <div class="vrd-label">ACTIVE COMPANY</div>
          <div style="font-weight:700; font-size:.95rem; color:{C['foam']};">{st.session_state.current_company}</div>
          <div style="font-size:.75rem; color:{C['subtext']}; margin-top:2px;">{cd.get('industry','')} · {cd.get('country','')}</div>
          <div style="margin-top:6px;"><span style="color:{gc}; font-weight:800; font-size:1.1rem;">{cd.get('grade','—')}</span>
          <span style="color:{C['subtext']}; font-size:.8rem;"> · {cd.get('overall',0)}/100</span></div>
        </div>""", unsafe_allow_html=True)
        st.markdown('<div class="vrd-divider" style="margin: 8px;"></div>', unsafe_allow_html=True)

    st.markdown(f"""<div style="padding: 0 8px;">
      <div class="vrd-label">FRAMEWORKS</div>
      {"".join([f'<div style="font-size:.76rem; color:{C["dim"]}; padding:2px 0;">✓ {fw}</div>' for fw in FRAMEWORKS])}
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="vrd-divider" style="margin: 16px 8px;"></div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:.65rem; color:{C["dim"]}; text-align:center; padding:0 8px;">v3.0 · Viridis ESG Intelligence<br>GRI·SASB·CDP·IFRS·CSA·GRESB·SBTi</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# DASHBOARD
# ════════════════════════════════════════════════════════════
if "Dashboard" in page:
    st.markdown(f"""<div class="vrd-header">
      <h1>⬡ Viridis Dashboard</h1>
      <p>Real-time ESG portfolio overview · {len(st.session_state.companies)} companies tracked</p>
      {"".join([f'<span class="vrd-header-badge">{fw}</span>' for fw in ["GRI","SASB","CDP","IFRS S1/S2","S&P CSA","GRESB","SBTi"]])}
    </div>""", unsafe_allow_html=True)

    cos = st.session_state.companies
    all_scores = [c["overall"] for c in cos.values()]
    tot_targets = sum(c["targets"] for c in cos.values())
    ot_targets = sum(c["on_track"] for c in cos.values())

    # Top metrics
    m1,m2,m3,m4,m5 = st.columns(5)
    for col, val, label, color in [
        (m1, len(cos), "Companies", C["leaf"]),
        (m2, f"{round(sum(all_scores)/len(all_scores),1) if all_scores else 0}", "Avg ESG Score", C["mint"]),
        (m3, f"{ot_targets}/{tot_targets}", "Targets On Track", C["amber"]),
        (m4, sum(1 for c in cos.values() if c["grade"].startswith("A")), "A-Grade", C["leaf"]),
        (m5, sum(1 for c in cos.values() if c["grade"].startswith("B")), "B-Grade", C["amber"]),
    ]:
        col.markdown(f"""<div class="vrd-metric">
          <div class="val mono" style="color:{color};">{val}</div>
          <div class="lbl">{label}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<div class="vrd-label">COMPANY CARDS</div>', unsafe_allow_html=True)

    # Company cards — 2 per row
    company_items = list(cos.items())
    for i in range(0, len(company_items), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i + j >= len(company_items): break
            name, data = company_items[i + j]
            gc = grade_color(data["grade"])
            gcls = grade_class(data["grade"])
            ot = data.get("on_track", 0)
            tot = data.get("targets", 0)
            ar = data.get("at_risk", 0)
            lg = data.get("lagging", 0)
            ot_pct = round(ot/max(tot,1)*100)

            # target status bar
            target_html = ""
            if tot:
                target_html = f"""<div style="margin-top:10px;">
                  <div class="vrd-label">TARGET STATUS</div>
                  <div style="display:flex; gap:4px; align-items:center; margin-bottom:4px;">
                    <div style="flex:{ot}; background:{C['leaf']}; height:6px; border-radius:3px;"></div>
                    <div style="flex:{ar}; background:{C['amber']}; height:6px; border-radius:3px;"></div>
                    <div style="flex:{max(lg,0)}; background:{C['red']}; height:6px; border-radius:3px;"></div>
                    <div style="flex:{max(tot-ot-ar-lg,0)}; background:{C['border']}; height:6px; border-radius:3px;"></div>
                  </div>
                  <div style="font-size:.72rem; color:{C['subtext']};">{ot} on track · {ar} at risk · {lg} lagging</div>
                </div>"""

            fws_html = "".join([f'<span class="badge-fw">{fw}</span>' for fw in data.get("frameworks",[])])

            with col:
                card_col, btn_col = st.columns([4,1])
                with card_col:
                    st.markdown(f"""<div class="vrd-co-card {gcls}">
                      <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:12px;">
                        <div>
                          <div style="font-weight:700; font-size:1rem; color:{C['foam']};">{name}</div>
                          <div style="font-size:.78rem; color:{C['subtext']}; margin-top:2px;">{data.get('industry','')} · {data.get('country','')}</div>
                        </div>
                        <div style="text-align:right;">
                          <div style="font-size:1.6rem; font-weight:900; color:{gc}; line-height:1;">{data['grade']}</div>
                          <div style="font-size:.72rem; color:{C['subtext']};">{data['overall']}/100</div>
                        </div>
                      </div>
                      <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:8px; margin-bottom:8px;">
                        {"".join([f'<div><div style="font-size:.68rem; color:{C["dim"]}; margin-bottom:3px;">{lbl}</div><div style="font-size:.9rem; font-weight:700; color:{col_};" class="mono">{val_}</div><div class="vrd-progress"><div class="vrd-progress-fill" style="width:{val_}%; background:{col_};"></div></div></div>' for lbl, val_, col_ in [("E", data["E_score"], C["leaf"]), ("S", data["S_score"], C["mint"]), ("G", data["G_score"], C["mist"])]])}
                      </div>
                      <div>{fws_html}</div>
                      {target_html}
                    </div>""", unsafe_allow_html=True)
                with btn_col:
                    st.markdown("<br><br>", unsafe_allow_html=True)
                    if st.button("→", key=f"go_{name}", help=f"View {name}"):
                        st.session_state.current_company = name
                        st.rerun()

    # Portfolio scatter
    st.markdown(f'<div class="vrd-label" style="margin-top:24px;">PORTFOLIO · E vs S SCORES</div>', unsafe_allow_html=True)
    df_p = pd.DataFrame([{"Company":k,"E":v["E_score"],"S":v["S_score"],"Overall":v["overall"],"Industry":v.get("industry","")} for k,v in cos.items()])
    if not df_p.empty:
        fig_s = px.scatter(df_p,x="E",y="S",size="Overall",color="Industry",hover_name="Company",size_max=36,
            color_discrete_sequence=[C["leaf"],C["amber"],C["blue"],C["mist"],C["mid"]])
        fig_s.update_layout(**CHART_LAYOUT, height=280,
            xaxis=dict(range=[0,105], gridcolor=C["border"], color=C["subtext"], title="Environmental Score"),
            yaxis=dict(range=[0,105], gridcolor=C["border"], color=C["subtext"], title="Social Score"),
            legend=dict(font=dict(color=C["subtext"], size=10)))
        st.plotly_chart(fig_s, use_container_width=True)


# ════════════════════════════════════════════════════════════
# COMPANY SETUP
# ════════════════════════════════════════════════════════════
elif "Company Setup" in page:
    st.markdown(f'<div class="vrd-header"><h1>🏢 Company Setup</h1><p>Register companies and configure their ESG profiles</p></div>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["➕ New Company", "📋 Manage Companies"])
    with tab1:
        st.markdown('<div class="vrd-card">', unsafe_allow_html=True)
        c1,c2 = st.columns(2)
        with c1:
            cn = st.text_input("Company Name *")
            ind = st.selectbox("Industry *", INDUSTRIES)
            country = st.text_input("Country", "India")
            rev = st.number_input("Revenue (USD Billion)", 0.0, step=0.1)
        with c2:
            ry = st.selectbox("Reporting Year", list(range(CURRENT_YEAR-1, CURRENT_YEAR-6, -1)))
            emp = st.number_input("Employees", 0, step=100)
            fws = st.multiselect("Reporting Frameworks", FRAMEWORKS, default=["GRI","CDP"])
        st.markdown('</div>', unsafe_allow_html=True)
        if st.button("Register Company →"):
            if cn:
                st.session_state.companies[cn] = {"industry":ind,"country":country,"revenue_bn":rev,"E_score":0,"S_score":0,"G_score":0,"overall":0,"grade":"—","frameworks":fws,"targets":0,"on_track":0,"at_risk":0,"lagging":0,"employees":emp,"report_year":ry}
                st.session_state.current_company = cn
                st.markdown(f'<div class="vrd-alert-ok">✅ {cn} registered. Proceed to AI Extraction or Data Input.</div>', unsafe_allow_html=True)
            else: st.markdown('<div class="vrd-alert-err">Company name required.</div>', unsafe_allow_html=True)
    with tab2:
        for name, data in st.session_state.companies.items():
            c1,c2,c3 = st.columns([3,1,1])
            gc = grade_color(data["grade"])
            with c1: st.markdown(f'<div style="padding:8px 0; color:{C["text"]}; font-weight:500;">{name} <span style="color:{C["subtext"]}; font-size:.82rem;">· {data.get("industry","")} · {data.get("country","")}</span></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div style="padding-top:8px;"><span style="color:{gc}; font-weight:800;">{data["grade"]}</span> <span style="color:{C["subtext"]}; font-size:.8rem;">{data["overall"]}/100</span></div>', unsafe_allow_html=True)
            with c3:
                if st.button("Select", key=f"sel_{name}"):
                    st.session_state.current_company = name
                    st.rerun()


# ════════════════════════════════════════════════════════════
# AI DATA EXTRACTION
# ════════════════════════════════════════════════════════════
elif "AI" in page:
    st.markdown(f'<div class="vrd-header"><h1>🤖 AI Data Extraction</h1><p>Upload a sustainability report or paste a URL — Viridis reads it and extracts ESG indicator values automatically</p></div>', unsafe_allow_html=True)

    cl = list(st.session_state.companies.keys())
    di = cl.index(st.session_state.current_company) if st.session_state.current_company in cl else 0
    ac = st.selectbox("Active Company", cl, index=di)
    st.session_state.current_company = ac
    cd = st.session_state.companies.get(ac, {})
    industry = cd.get("industry", INDUSTRIES[0])

    st.markdown(f"""<div class="vrd-ai-box">
      <div class="vrd-ai-header">
        <div class="vrd-ai-dot"></div>
        <div style="font-weight:600; color:{C['foam']};">Viridis AI Engine</div>
        <div style="font-size:.78rem; color:{C['subtext']};">Powered by Claude · Extracts ESG data from reports</div>
      </div>
      <div style="font-size:.84rem; color:{C['subtext']};">
        Reads sustainability reports, annual reports, or integrated reports. Extracts indicator values, identifies targets, and flags data quality. 
        Accuracy is typically 60–80% — always review extracted values before saving.
      </div>
    </div>""", unsafe_allow_html=True)

    # API key
    api_key = st.text_input("Anthropic API Key", type="password",
        help="Your key stays in this session only and is never stored. Get one at console.anthropic.com")

    tab_pdf, tab_url = st.tabs(["📄 Upload PDF", "🌐 Fetch URL"])

    doc_text = None
    source_label = ""

    with tab_pdf:
        uploaded = st.file_uploader("Upload sustainability / annual report (PDF)", type=["pdf"])
        if uploaded:
            st.markdown(f'<div class="vrd-alert-ok">📄 {uploaded.name} ({round(len(uploaded.getvalue())/1024)}KB) — ready for extraction</div>', unsafe_allow_html=True)
            if st.button("🤖 Extract from PDF", key="btn_pdf"):
                if not api_key:
                    st.markdown('<div class="vrd-alert-err">Please enter your Anthropic API key above.</div>', unsafe_allow_html=True)
                else:
                    with st.spinner("Reading PDF and extracting ESG data..."):
                        doc_text = extract_text_from_pdf(uploaded.getvalue())
                        source_label = uploaded.name

    with tab_url:
        url_input = st.text_input("Report URL", placeholder="https://www.company.com/sustainability-report-2024.pdf")
        st.markdown(f'<div style="font-size:.78rem; color:{C["subtext"]};">Works best with public PDF reports or HTML sustainability pages. Paywalled or login-protected pages cannot be fetched.</div>', unsafe_allow_html=True)
        if st.button("🤖 Fetch & Extract", key="btn_url"):
            if not api_key:
                st.markdown('<div class="vrd-alert-err">Please enter your Anthropic API key above.</div>', unsafe_allow_html=True)
            elif not url_input:
                st.markdown('<div class="vrd-alert-err">Please enter a URL.</div>', unsafe_allow_html=True)
            else:
                with st.spinner(f"Fetching {url_input}..."):
                    doc_text = fetch_url_text(url_input)
                    source_label = url_input

    # Run extraction if we have text
    if doc_text and api_key and source_label:
        if "Error" in doc_text[:100]:
            st.markdown(f'<div class="vrd-alert-err">{doc_text}</div>', unsafe_allow_html=True)
        else:
            all_inds = get_indicators(industry, "E") + get_indicators(industry, "S") + get_indicators(industry, "G")
            with st.spinner("AI is reading the report and extracting indicator values..."):
                result = run_ai_extraction(doc_text, industry, all_inds, api_key)
            st.session_state.ai_results[ac] = result

    # Display results
    ai_res = st.session_state.ai_results.get(ac)
    if ai_res:
        if "error" in ai_res:
            st.markdown(f'<div class="vrd-alert-err">Extraction error: {ai_res["error"]}</div>', unsafe_allow_html=True)
        else:
            # Summary header
            extracted_inds = {k:v for k,v in ai_res.get("indicators",{}).items() if v.get("value") is not None}
            st.markdown(f"""<div class="vrd-card">
              <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <div>
                  <div style="font-weight:700; font-size:1rem; color:{C['foam']};">{ai_res.get('company_name','Unknown company')} · {ai_res.get('reporting_year','Unknown year')}</div>
                  <div style="font-size:.82rem; color:{C['subtext']}; margin-top:2px;">
                    <span class="badge-green">{len(extracted_inds)} values extracted</span>&nbsp;
                    <span class="badge-amber">{len(ai_res.get('indicators',{})) - len(extracted_inds)} not found</span>&nbsp;
                    <span class="badge-blue">{len(ai_res.get('targets',[]))} targets identified</span>
                  </div>
                </div>
              </div>
              {f'<div style="font-size:.8rem; color:{C["subtext"]};">{ai_res.get("notes","")}</div>' if ai_res.get("notes") else ""}
            </div>""", unsafe_allow_html=True)

            # Extracted indicators table
            st.markdown(f'<div class="vrd-label">EXTRACTED INDICATOR VALUES</div>', unsafe_allow_html=True)
            if extracted_inds:
                rows = []
                for ind_name, v in ai_res.get("indicators",{}).items():
                    conf_badge = {"high":f'<span class="badge-green">High</span>',"medium":f'<span class="badge-amber">Medium</span>',"low":f'<span class="badge-red">Low</span>'}.get(v.get("confidence",""),'—')
                    found = v.get("value") is not None
                    rows.append({
                        "Indicator": ind_name,
                        "Value": f'{v.get("value","—"):,}' if isinstance(v.get("value"), (int,float)) else "—",
                        "Unit": v.get("unit","—"),
                        "Confidence": v.get("confidence","—").title() if v.get("confidence") else "—",
                        "Source": (v.get("source_text","") or "")[:80],
                        "_found": found
                    })
                df_ext = pd.DataFrame(rows)
                st.dataframe(df_ext[["Indicator","Value","Unit","Confidence","Source"]].style.apply(
                    lambda x: ['color: ' + (C["leaf"] if x["Confidence"]=="High" else C["amber"] if x["Confidence"]=="Medium" else C["red"]) + '; font-weight:600' if col == "Confidence" else '' for col in x.index], axis=1),
                    use_container_width=True, height=300)

            # Apply to data input button
            if extracted_inds:
                st.markdown("<br>", unsafe_allow_html=True)
                col1, col2 = st.columns([1, 3])
                with col1:
                    if st.button("✅ Apply to Data Input →"):
                        if ac not in st.session_state.esg_data:
                            st.session_state.esg_data[ac] = {}
                        report_year = ai_res.get("reporting_year")
                        try: report_year = int(report_year)
                        except: report_year = CURRENT_YEAR - 1
                        for pillar in ["E","S","G"]:
                            if pillar not in st.session_state.esg_data[ac]:
                                st.session_state.esg_data[ac][pillar] = {}
                            for ind_meta in get_indicators(industry, pillar):
                                iname = ind_meta["name"]
                                if iname in ai_res.get("indicators",{}):
                                    val = ai_res["indicators"][iname].get("value")
                                    if val is not None:
                                        existing = st.session_state.esg_data[ac][pillar].get(iname, {})
                                        st.session_state.esg_data[ac][pillar][iname] = {
                                            "current": val,
                                            "prior": existing.get("current", 0),
                                            "ai_extracted": True,
                                            "confidence": ai_res["indicators"][iname].get("confidence",""),
                                        }
                        st.markdown(f'<div class="vrd-alert-ok">✅ {len(extracted_inds)} values applied to Data Input. AI-extracted values are flagged — review before finalising.</div>', unsafe_allow_html=True)
                with col2:
                    st.markdown(f'<div style="font-size:.8rem; color:{C["subtext"]}; padding-top:10px;">Values will pre-fill the Data Input tab. You can review and correct each one before saving. AI-extracted values shown with a robot icon.</div>', unsafe_allow_html=True)

            # Extracted targets
            if ai_res.get("targets"):
                st.markdown(f'<div class="vrd-label" style="margin-top:16px;">IDENTIFIED TARGETS</div>', unsafe_allow_html=True)
                for t in ai_res["targets"]:
                    st.markdown(f"""<div class="vrd-card" style="padding:14px;">
                      <div style="font-weight:600; color:{C['foam']}; margin-bottom:4px;">{t.get('name','Unnamed target')}</div>
                      <div style="font-size:.82rem; color:{C['subtext']};">
                        {t.get('indicator','—')} · Target: {t.get('target_value','?')} by {t.get('target_year','?')}
                        {f" (baseline: {t.get('baseline_value','?')} in {t.get('baseline_year','?')})" if t.get('baseline_year') else ""}
                      </div>
                      <div style="font-size:.78rem; color:{C['dim']}; margin-top:4px;">{t.get('source_text','')}</div>
                    </div>""", unsafe_allow_html=True)
                if st.button("📌 Add all identified targets →"):
                    if ac not in st.session_state.targets: st.session_state.targets[ac] = []
                    for t in ai_res["targets"]:
                        try:
                            baseline = float(t.get("baseline_value") or 0)
                            target_val = float(t.get("target_value") or 0)
                            target_year = int(t.get("target_year") or CURRENT_YEAR+5)
                            baseline_year = int(t.get("baseline_year") or CURRENT_YEAR-3)
                            actual_pct = 0
                            expected_pct = calc_expected_progress(baseline_year, target_year)
                            status = get_status(actual_pct, expected_pct)
                            issues, suggestions, sbti_ok = validate_target(t.get("category","Custom"), target_year, baseline_year)
                            st.session_state.targets[ac].append({
                                "name": t.get("name","AI-identified target"),
                                "category": t.get("category","Custom"),
                                "pillar": "E",
                                "indicator": t.get("indicator","—"),
                                "unit": "—",
                                "baseline": baseline, "baseline_year": baseline_year,
                                "target_val": target_val, "target_year": target_year,
                                "current": baseline, "actual_pct": actual_pct,
                                "expected_pct": expected_pct, "status": status,
                                "sbti_validated": sbti_ok,
                                "issues": issues, "suggestions": suggestions,
                                "notes": "AI-extracted from report"
                            })
                        except: pass
                    all_t = st.session_state.targets[ac]
                    st.session_state.companies[ac].update({"targets":len(all_t),"on_track":sum(1 for t in all_t if t["status"]=="On Track"),"at_risk":sum(1 for t in all_t if t["status"]=="At Risk"),"lagging":sum(1 for t in all_t if t["status"]=="Lagging")})
                    st.markdown(f'<div class="vrd-alert-ok">✅ {len(ai_res["targets"])} targets added. Go to Targets tab to review and update current values.</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# DATA INPUT
# ════════════════════════════════════════════════════════════
elif "Data Input" in page:
    st.markdown(f'<div class="vrd-header"><h1>📊 Data Input</h1><p>Industry-specific indicators · GRI · SASB · S&P CSA · GRESB · BRSR</p></div>', unsafe_allow_html=True)
    cl = list(st.session_state.companies.keys())
    di = cl.index(st.session_state.current_company) if st.session_state.current_company in cl else 0
    ac = st.selectbox("Active Company", cl, index=di)
    st.session_state.current_company = ac
    cd = st.session_state.companies.get(ac, {})
    industry = cd.get("industry", INDUSTRIES[0])
    if ac not in st.session_state.esg_data: st.session_state.esg_data[ac] = {}
    if ac not in st.session_state.dq: st.session_state.dq[ac] = {"assured":False,"assurance_level":"None","coverage_pct":0,"assurer":""}

    # DQ
    with st.expander("📋 Data Quality Declaration"):
        dq = st.session_state.dq[ac]
        c1,c2,c3,c4 = st.columns(4)
        with c1: dq["assured"] = st.checkbox("Externally assured", dq.get("assured",False))
        with c2: dq["assurance_level"] = st.selectbox("Level", ["None","Limited","Reasonable"], index=["None","Limited","Reasonable"].index(dq.get("assurance_level","None")))
        with c3: dq["assurer"] = st.text_input("Assurer", dq.get("assurer",""))
        with c4: dq["coverage_pct"] = st.number_input("Coverage (%)", 0, 100, int(dq.get("coverage_pct",0)))
        st.session_state.dq[ac] = dq

    # Template download
    c_dl, c_up = st.columns([1,2])
    with c_dl:
        out = io.BytesIO()
        with pd.ExcelWriter(out, engine="openpyxl") as w:
            for pillar, pname in [("E","Environmental"),("S","Social"),("G","Governance")]:
                rows = [{"Indicator":m["name"],"Unit":m["unit"],"GRI":m.get("gri","—"),"SASB":m.get("sasb","—"),
                    "CSA Criterion":m.get("csa","—"),"Current Year":"","Prior Year":"","Notes":"",
                    "Industry Avg":m.get("benchmark_avg",""),"Top Quartile":m.get("benchmark_top","")} for m in get_indicators(industry, pillar)]
                pd.DataFrame(rows).to_excel(w, sheet_name=pname[:31], index=False)
        out.seek(0)
        st.download_button("⬇️ Download Template", data=out,
            file_name=f"Viridis_{ac.replace(' ','_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    with c_up:
        uf = st.file_uploader("Upload completed template", type=["xlsx"])
        if uf:
            try:
                xl = pd.read_excel(uf, sheet_name=None)
                for sn, df in xl.items():
                    if "Indicator" in df.columns and "Current Year" in df.columns:
                        pk = {"Environmental":"E","Social":"S","Governance":"G"}.get(sn, sn)
                        if pk not in st.session_state.esg_data[ac]: st.session_state.esg_data[ac][pk] = {}
                        for _, row in df.iterrows():
                            if pd.notna(row.get("Indicator")) and pd.notna(row.get("Current Year")):
                                st.session_state.esg_data[ac][pk][row["Indicator"]] = {"current":row["Current Year"],"prior":row.get("Prior Year",0)}
                st.markdown('<div class="vrd-alert-ok">✅ Template uploaded successfully.</div>', unsafe_allow_html=True)
            except Exception as e: st.markdown(f'<div class="vrd-alert-err">Error: {e}</div>', unsafe_allow_html=True)

    st.markdown('<div class="vrd-divider"></div>', unsafe_allow_html=True)

    # Production volume
    with st.expander("⚙️ Production / Activity Data (for intensity calculations)"):
        c1,c2 = st.columns(2)
        with c1: prod_vol = st.number_input("Production volume", 0.0, step=1000.0, key=f"pv_{ac}")
        with c2: prod_unit = st.selectbox("Unit", ["tonnes","MWh","m²","units","million litres"], key=f"pu_{ac}")

    tab_e, tab_s, tab_g = st.tabs(["🌍 Environmental","👥 Social","🏛️ Governance"])

    def render_pillar(pillar):
        inds = get_indicators(industry, pillar)
        if pillar not in st.session_state.esg_data[ac]: st.session_state.esg_data[ac][pillar] = {}
        filled = 0
        for i, m in enumerate(inds):
            iname = m["name"]
            stored = st.session_state.esg_data[ac][pillar].get(iname, {})
            cur = float(stored.get("current",0) or 0)
            prior = float(stored.get("prior",0) or 0)
            ai_flag = stored.get("ai_extracted", False)
            conf = stored.get("confidence","")
            icon = ("🤖" if ai_flag else "✅" if cur else "○")
            conf_badge = f' <span class="badge-{"green" if conf=="high" else "amber" if conf=="medium" else "red"}">{conf}</span>' if ai_flag and conf else ""

            with st.expander(f"{icon}  {iname}  [{m['unit']}]  ·  GRI {m.get('gri','—')}  ·  SASB {m.get('sasb','—')}"):
                if ai_flag:
                    st.markdown(f'<div class="vrd-alert-ok" style="margin-bottom:8px;">🤖 AI-extracted value ({conf} confidence) — please verify before saving.</div>', unsafe_allow_html=True)
                c1,c2,c3 = st.columns(3)
                with c1: new_cur = st.number_input(f"Current year", value=cur, key=f"{pillar}_{i}_c", step=0.01)
                with c2: new_prior = st.number_input(f"Prior year", value=prior, key=f"{pillar}_{i}_p", step=0.01)
                with c3:
                    if new_prior and new_cur:
                        yoy = round((new_cur - new_prior)/max(abs(new_prior),0.001)*100,1)
                        yoy_col = C["leaf"] if (yoy < 0 and pillar=="E") or (yoy > 0 and pillar in ["S","G"]) else C["red"]
                        st.markdown(f'<div style="padding-top:28px; font-size:.9rem; color:{yoy_col}; font-weight:700;">{yoy:+.1f}% YoY</div>', unsafe_allow_html=True)
                for fl in flag_value(new_cur, m):
                    st.markdown(f'<div class="vrd-alert-warn">⚠️ {fl}</div>', unsafe_allow_html=True)
                ba, bt = m.get("benchmark_avg"), m.get("benchmark_top")
                if ba:
                    st.markdown(f'<div style="font-size:.78rem; color:{C["subtext"]}; margin-top:4px;">Benchmarks · Industry avg: <span class="mono">{ba:,}</span> · Top quartile: <span class="mono">{bt:,}</span> {m["unit"]}</div>', unsafe_allow_html=True)
                if prod_vol > 0 and new_cur > 0 and m["unit"] not in ["%","number","hrs/year"]:
                    st.markdown(f'<div style="font-size:.78rem; color:{C["subtext"]};">Intensity: <span class="mono">{round(new_cur/prod_vol,4):,}</span> {m["unit"]}/{prod_unit}</div>', unsafe_allow_html=True)
                st.session_state.esg_data[ac][pillar][iname] = {"current":new_cur,"prior":new_prior,"ai_extracted":ai_flag,"confidence":conf}
                if new_cur: filled += 1
        cov = round(filled/max(len(inds),1)*100)
        st.markdown(f'<div style="font-size:.78rem; color:{C["subtext"]}; margin-top:8px;">{filled}/{len(inds)} filled · {cov}% coverage</div>', unsafe_allow_html=True)
        return filled, len(inds)

    with tab_e: render_pillar("E")
    with tab_s: render_pillar("S")
    with tab_g: render_pillar("G")

    if st.button("💾 Save & Recalculate Scores"):
        scores = {}
        for pillar in ["E","S","G"]:
            inds = get_indicators(industry, pillar)
            fp = sum(1 for v in st.session_state.esg_data[ac].get(pillar,{}).values() if isinstance(v,dict) and v.get("current",0))
            cov_s = round(fp/max(len(inds),1)*40)
            bench_s = 0
            for m in inds:
                v = st.session_state.esg_data[ac].get(pillar,{}).get(m["name"],{})
                val = float(v.get("current",0) or 0) if isinstance(v,dict) else 0
                ba, bt = m.get("benchmark_avg"), m.get("benchmark_top")
                if val and ba and bt:
                    better = val >= bt if m["unit"]=="%"  else val <= bt
                    avg_ok = val >= ba if m["unit"]=="%"  else val <= ba
                    if better: bench_s += 2
                    elif avg_ok: bench_s += 1
            scores[pillar] = min(95, 30 + cov_s + min(25, bench_s))
        overall = round(scores["E"]*0.4 + scores["S"]*0.35 + scores["G"]*0.25)
        st.session_state.companies[ac].update({"E_score":scores["E"],"S_score":scores["S"],"G_score":scores["G"],"overall":overall,"grade":score_to_grade(overall)})
        st.markdown(f'<div class="vrd-alert-ok">✅ E:{scores["E"]} · S:{scores["S"]} · G:{scores["G"]} · Overall:{overall} ({score_to_grade(overall)})</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# TARGETS
# ════════════════════════════════════════════════════════════
elif "Targets" in page:
    st.markdown(f'<div class="vrd-header"><h1>🎯 Targets</h1><p>Set, validate, and track sustainability commitments · SBTi · IPCC · CDP · RE100 aligned</p></div>', unsafe_allow_html=True)
    cl = list(st.session_state.companies.keys())
    di = cl.index(st.session_state.current_company) if st.session_state.current_company in cl else 0
    ac = st.selectbox("Active Company", cl, index=di)
    st.session_state.current_company = ac
    cd = st.session_state.companies.get(ac, {})
    industry = cd.get("industry", INDUSTRIES[0])
    if ac not in st.session_state.targets: st.session_state.targets[ac] = []
    all_ind_names = ["(select or type)"] + [m["name"] for p in ["E","S","G"] for m in get_indicators(industry, p)]

    with st.expander("➕ Add New Target", expanded=not st.session_state.targets[ac]):
        c1,c2,c3 = st.columns(3)
        with c1:
            t_cat = st.selectbox("Category", TARGET_CATEGORIES)
            t_name = st.text_input("Target Name *", placeholder="e.g. Net Zero by 2050")
            t_pillar = st.selectbox("Pillar", ["E — Environmental","S — Social","G — Governance"])
        with c2:
            t_ind = st.selectbox("Linked KPI", all_ind_names)
            if t_ind == "(select or type)": t_ind = st.text_input("Custom KPI", placeholder="e.g. Scope 1+2 (tCO2e)")
            t_unit = st.text_input("Unit", placeholder="tCO2e")
            t_by = st.selectbox("Baseline Year", list(range(CURRENT_YEAR-1, 2005, -1)))
            t_bv = st.number_input("Baseline Value", step=0.01)
        with c3:
            t_tv = st.number_input("Target Value", step=0.01)
            ty_list = list(range(CURRENT_YEAR+1, 2076))
            t_ty = st.selectbox("Target Year", ty_list, index=ty_list.index(2030) if 2030 in ty_list else 0)
            t_cur = st.number_input("Current Achievement", step=0.01)

        st.markdown(f'<div class="vrd-alert-ok" style="font-size:.8rem; margin:8px 0;">Validation checks: ① Target year ② Framework alignment (IPCC/RE100/CDP) ③ Baseline recency ④ Ambition ⑤ Scope completeness</div>', unsafe_allow_html=True)
        if st.button("✅ Validate & Add →"):
            if not t_name: st.markdown('<div class="vrd-alert-err">Target name required.</div>', unsafe_allow_html=True)
            else:
                issues, suggestions, sbti_ok = validate_target(t_cat, t_ty, t_by)
                actual_pct = calc_actual_progress(t_bv, t_tv, t_cur)
                expected_pct = calc_expected_progress(t_by, t_ty)
                status = get_status(actual_pct, expected_pct)
                st.session_state.targets[ac].append({"name":t_name,"category":t_cat,"pillar":t_pillar[0],"indicator":t_ind,"unit":t_unit,"baseline":t_bv,"baseline_year":t_by,"target_val":t_tv,"target_year":t_ty,"current":t_cur,"actual_pct":actual_pct,"expected_pct":expected_pct,"status":status,"sbti_validated":sbti_ok,"issues":issues,"suggestions":suggestions,"notes":""})
                all_t = st.session_state.targets[ac]
                st.session_state.companies[ac].update({"targets":len(all_t),"on_track":sum(1 for t in all_t if t["status"]=="On Track"),"at_risk":sum(1 for t in all_t if t["status"]=="At Risk"),"lagging":sum(1 for t in all_t if t["status"]=="Lagging")})
                for iss in issues: st.markdown(f'<div class="vrd-alert-warn">⚠️ {iss}</div>', unsafe_allow_html=True)
                for sug in suggestions: st.markdown(f'<div class="vrd-alert-ok">{sug}</div>', unsafe_allow_html=True)
                if sbti_ok: st.markdown(f'<div class="vrd-alert-ok">✅ SBTi-style validation passed.</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="vrd-alert-ok">Target added · {status} · Actual: {actual_pct}% · Expected: {expected_pct}%</div>', unsafe_allow_html=True)

    targets = st.session_state.targets.get(ac, [])
    if targets:
        st.markdown(f'<div class="vrd-label" style="margin-top:20px;">TARGETS ({len(targets)})</div>', unsafe_allow_html=True)
        for i, t in enumerate(targets):
            sc = {"On Track":C["leaf"],"At Risk":C["amber"],"Lagging":C["red"]}.get(t["status"],C["leaf"])
            icon = {"On Track":"🟢","At Risk":"🟡","Lagging":"🔴"}.get(t["status"],"⚪")
            sbti_b = f' <span class="badge-green">SBTi ✓</span>' if t.get("sbti_validated") else ""
            with st.expander(f"{icon}  {t['name']}  ·  {t['category']}  ·  {t['target_year']}"):
                c1,c2 = st.columns([1,2])
                with c1: st.plotly_chart(target_progress_chart(t), use_container_width=True)
                with c2:
                    gap = round(float(t.get("target_val",0)) - float(t.get("current",0)), 2)
                    gap_col = C["leaf"] if (gap < 0 and t["pillar"]=="E") or (gap > 0) else C["red"]
                    st.markdown(f"""<div class="vrd-card" style="padding:14px;">
                      <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:8px; margin-bottom:10px; text-align:center;">
                        <div><div style="font-size:1.3rem; font-weight:800; color:{C['leaf']};" class="mono">{t.get('actual_pct',0)}%</div><div style="font-size:.7rem; color:{C['subtext']};">Actual progress</div></div>
                        <div><div style="font-size:1.3rem; font-weight:800; color:{C['blue']};" class="mono">{t.get('expected_pct',0)}%</div><div style="font-size:.7rem; color:{C['subtext']};">Expected now</div></div>
                        <div><div style="font-size:1.3rem; font-weight:800; color:{gap_col};" class="mono">{gap:+,.1f}</div><div style="font-size:.7rem; color:{C['subtext']};">Gap ({t.get('unit','')})</div></div>
                      </div>
                      <div style="font-size:.82rem; color:{C['subtext']}; margin-bottom:6px;">
                        Baseline: <span class="mono" style="color:{C['text']};">{t.get('baseline'):,}</span> ({t.get('baseline_year')}) →
                        Current: <span class="mono" style="color:{C['text']};">{t.get('current'):,}</span> →
                        Target: <span class="mono" style="color:{C['text']};">{t.get('target_val'):,}</span> ({t.get('target_year')}) {sbti_b}
                      </div>
                    </div>""", unsafe_allow_html=True)
                    needed = annual_change_needed(t.get("baseline",0), t.get("target_val",0), t.get("target_year",2030))
                    if needed: st.markdown(f'<div class="vrd-strategy">📍 <strong>Action:</strong> Change <em>{t.get("indicator","value")}</em> by <strong class="mono">{needed:+,.2f} {t.get("unit","")}/year</strong> through {t.get("target_year")}.</div>', unsafe_allow_html=True)
                    for sug in t.get("suggestions",[]): st.markdown(f'<div class="vrd-alert-ok">{sug}</div>', unsafe_allow_html=True)
                    for iss in t.get("issues",[]): st.markdown(f'<div class="vrd-alert-warn">⚠️ {iss}</div>', unsafe_allow_html=True)
                if st.button("🗑️ Delete", key=f"del_{ac}_{i}"):
                    st.session_state.targets[ac].pop(i)
                    all_t = st.session_state.targets[ac]
                    st.session_state.companies[ac].update({"targets":len(all_t),"on_track":sum(1 for t in all_t if t["status"]=="On Track"),"at_risk":sum(1 for t in all_t if t["status"]=="At Risk"),"lagging":sum(1 for t in all_t if t["status"]=="Lagging")})
                    st.rerun()
    else:
        st.markdown(f'<div class="vrd-card" style="text-align:center; padding:40px; color:{C["subtext"]};">No targets yet — add one above.</div>', unsafe_allow_html=True)

    st.markdown('<div class="vrd-divider"></div>', unsafe_allow_html=True)
    if st.button("🔄 Reset all targets"):
        st.session_state.targets[ac] = []
        st.session_state.companies[ac].update({"targets":0,"on_track":0,"at_risk":0,"lagging":0})
        st.rerun()


# ════════════════════════════════════════════════════════════
# ANALYSIS & INSIGHTS
# ════════════════════════════════════════════════════════════
elif "Analysis" in page:
    st.markdown(f'<div class="vrd-header"><h1>📈 Analysis & Insights</h1><p>Scores · Benchmarks · SDG alignment · Materiality · Risks & Opportunities · Report</p></div>', unsafe_allow_html=True)
    cl = list(st.session_state.companies.keys())
    di = cl.index(st.session_state.current_company) if st.session_state.current_company in cl else 0
    ac = st.selectbox("Active Company", cl, index=di)
    st.session_state.current_company = ac
    cd = st.session_state.companies.get(ac, {})
    industry = cd.get("industry", INDUSTRIES[0])
    e_s, s_s, g_s, ov = cd.get("E_score",0), cd.get("S_score",0), cd.get("G_score",0), cd.get("overall",0)
    grade = cd.get("grade","—")

    tab_ov, tab_ind, tab_sdg, tab_risk, tab_mat, tab_rep = st.tabs(["📊 Overview","🔍 Indicators","🌐 SDG","⚡ Risks","📐 Materiality","📄 Report"])

    with tab_ov:
        c1,c2,c3,c4 = st.columns([1.5,1,1,1])
        with c1: st.plotly_chart(mini_radar(e_s or 55, s_s or 60, g_s or 65, size=200), use_container_width=True)
        with c2:
            gc = grade_color(grade)
            st.markdown(f"""<div class="vrd-metric" style="height:165px; display:flex; flex-direction:column; justify-content:center;">
              <div style="font-size:3rem; font-weight:900; color:{gc}; line-height:1;">{grade}</div>
              <div style="font-size:1rem; color:{C['subtext']}; margin-top:4px;">Overall</div>
              <div style="font-size:1.5rem; font-weight:800; color:{C['text']};" class="mono">{ov}<span style="font-size:.8rem; color:{C['subtext']};">/100</span></div>
            </div>""", unsafe_allow_html=True)
        with c3: st.plotly_chart(gauge_chart(e_s or 55,"Environment",C["leaf"]), use_container_width=True)
        with c4: st.plotly_chart(gauge_chart(s_s or 60,"Social",C["mint"]), use_container_width=True)

        st.markdown(f'<div style="font-size:.75rem; color:{C["dim"]}; margin:4px 0 16px;">Score = E×40% + S×35% + G×25% · Coverage + benchmark performance</div>', unsafe_allow_html=True)

        # Framework alignment
        st.markdown(f'<div class="vrd-label">FRAMEWORK ALIGNMENT ESTIMATE</div>', unsafe_allow_html=True)
        fw_scores = {"GRI":min(100,(e_s+s_s+g_s)//3+5),"CDP":min(100,e_s+3),"SASB":min(100,(e_s+g_s)//2+4),"IFRS S1/S2":min(100,e_s-3),"S&P CSA":min(100,ov+2),"GRESB":min(100,(e_s+g_s)//2),"SBTi":min(100,e_s-8)}
        fig_fw = go.Figure()
        for fw, sc in fw_scores.items():
            color = C["leaf"] if sc >= 70 else (C["amber"] if sc >= 50 else C["red"])
            fig_fw.add_trace(go.Bar(x=[fw], y=[sc], marker_color=color, name=fw, marker=dict(line=dict(width=0))))
        fig_fw.update_layout(**CHART_LAYOUT, barmode="group", height=190,
            yaxis=dict(range=[0,105], gridcolor=C["border"], color=C["subtext"]),
            xaxis=dict(color=C["subtext"]), showlegend=False,
            margin=dict(t=10,b=40,l=10,r=10))
        st.plotly_chart(fig_fw, use_container_width=True)

        # Peers
        peers = {k:v for k,v in st.session_state.companies.items() if v.get("industry")==industry and k!=ac}
        if peers:
            st.markdown(f'<div class="vrd-label">PEER BENCHMARKING</div>', unsafe_allow_html=True)
            fig_p = go.Figure()
            fig_p.add_trace(go.Scatterpolar(r=[e_s,s_s,g_s,e_s],theta=["E","S","G","E"],name=ac,
                line=dict(color=C["leaf"],width=3),fill="toself",fillcolor="rgba(46,204,113,.12)"))
            for pn,pd_ in peers.items():
                fig_p.add_trace(go.Scatterpolar(r=[pd_["E_score"],pd_["S_score"],pd_["G_score"],pd_["E_score"]],
                    theta=["E","S","G","E"],name=pn,line=dict(color=C["dim"],width=1.5)))
            fig_p.update_layout(**CHART_LAYOUT,
                polar=dict(radialaxis=dict(range=[0,100],gridcolor=C["border"],tickfont=dict(color=C["dim"])),bgcolor="rgba(0,0,0,0)"),
                height=260, margin=dict(t=30,b=10), legend=dict(font=dict(color=C["subtext"],size=10)))
            st.plotly_chart(fig_p, use_container_width=True)

    with tab_ind:
        st.markdown(f'<div class="vrd-label">INDICATOR PERFORMANCE</div>', unsafe_allow_html=True)
        for pillar, pname, pcol in [("E","Environmental",C["leaf"]),("S","Social",C["mint"]),("G","Governance",C["mist"])]:
            st.markdown(f'<div style="font-weight:700; font-size:.9rem; color:{pcol}; margin:14px 0 6px;">▸ {pname}</div>', unsafe_allow_html=True)
            inds = get_indicators(industry, pillar)
            edata = st.session_state.esg_data.get(ac,{}).get(pillar,{})
            for m in inds:
                iname = m["name"]
                vd = edata.get(iname,{})
                cur = float(vd.get("current",0) or 0) if isinstance(vd,dict) else 0
                prior = float(vd.get("prior",0) or 0) if isinstance(vd,dict) else 0
                if not cur: continue
                ba, bt = m.get("benchmark_avg"), m.get("benchmark_top")
                if ba and bt:
                    perf = ("strong" if (cur >= bt if m["unit"]=="%"  else cur <= bt)
                            else "average" if (cur >= ba if m["unit"]=="%"  else cur <= ba)
                            else "lagging")
                else: perf = "reported"
                pc = {"strong":C["leaf"],"average":C["amber"],"lagging":C["red"],"reported":C["blue"]}.get(perf)
                pl = {"strong":"▲ Top quartile","average":"~ Avg","lagging":"▼ Lagging","reported":"Reported"}.get(perf)
                yoy_s = ""
                if prior:
                    yoy = round((cur-prior)/max(abs(prior),.001)*100,1)
                    yoy_s = f"  {'↑' if yoy>0 else '↓'}{abs(yoy):.1f}%"
                linked = next((t for t in st.session_state.targets.get(ac,[]) if t.get("indicator","").lower() in iname.lower() or iname.lower() in t.get("indicator","").lower()), None)
                with st.expander(f"{'🟢' if perf=='strong' else '🟡' if perf=='average' else '🔴' if perf=='lagging' else '○'}  {iname}  —  {cur:,} {m['unit']}{yoy_s}"):
                    c1,c2 = st.columns([1,2])
                    with c1:
                        st.markdown(f"""<div class="vrd-card" style="padding:12px;">
                          <div style="font-size:.75rem; color:{C['subtext']};">GRI {m.get('gri','—')} · SASB {m.get('sasb','—')}<br>CSA: {m.get('csa','—')}</div>
                          <div style="margin-top:8px; font-size:.85rem; font-weight:700; color:{pc};">{pl}</div>
                          {f'<div style="font-size:.75rem; color:{C["subtext"]}; margin-top:4px;">Avg: {ba:,} · Top: {bt:,} {m["unit"]}</div>' if ba else ''}
                        </div>""", unsafe_allow_html=True)
                    with c2:
                        if linked: st.plotly_chart(target_progress_chart(linked), use_container_width=True)
                        elif ba:
                            fig_b = go.Figure()
                            for lbl, v, col_ in [("This company",cur,pc),("Industry avg",ba,C["dim"]),("Top quartile",bt,C["leaf"])]:
                                fig_b.add_trace(go.Bar(x=[lbl],y=[v],marker_color=col_,name=lbl,marker=dict(line=dict(width=0))))
                            fig_b.update_layout(**CHART_LAYOUT, barmode="group", height=160, showlegend=False,
                                yaxis=dict(gridcolor=C["border"]), margin=dict(t=10,b=30,l=40,r=10))
                            st.plotly_chart(fig_b, use_container_width=True)
                    if linked:
                        n = annual_change_needed(linked.get("baseline",0),linked.get("target_val",0),linked.get("target_year",2030))
                        if n: st.markdown(f'<div class="vrd-strategy">🎯 Need <strong>{n:+,.2f} {m["unit"]}/year</strong> to reach {linked["name"]} by {linked["target_year"]}.</div>', unsafe_allow_html=True)

    with tab_sdg:
        st.markdown(f'<div class="vrd-label">SDG ALIGNMENT — {industry.upper()}</div>', unsafe_allow_html=True)
        relevant = INDUSTRY_SDGS.get(industry,[13,12,6,8])
        sdg_html = "".join([f'<span class="sdg-chip" style="background:{SDG_COLORS.get(n,"#999")};">SDG {n}: {SDG_NAMES.get(n,"")}</span>' for n in relevant])
        st.markdown(sdg_html, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        # Coverage heatmap
        cov_data = []
        for pillar in ["E","S","G"]:
            for m in get_indicators(industry, pillar):
                vd = st.session_state.esg_data.get(ac,{}).get(pillar,{}).get(m["name"],{})
                cur = float(vd.get("current",0) or 0) if isinstance(vd,dict) else 0
                prior = float(vd.get("prior",0) or 0) if isinstance(vd,dict) else 0
                if cur and prior:
                    trend = "Improving" if (cur<prior and pillar=="E") or (cur>prior and pillar in ["S","G"]) else ("Declining" if (cur>prior and pillar=="E") or (cur<prior and pillar in ["S","G"]) else "Stable")
                elif cur: trend = "Reported"
                else: trend = "Not Reported"
                cov_data.append({"Indicator":m["name"][:30],"Pillar":pillar,"Status":trend})
        if cov_data:
            df_cov = pd.DataFrame(cov_data)
            cmap = {"Improving":C["leaf"],"Stable":C["blue"],"Declining":C["red"],"Reported":C["amber"],"Not Reported":C["border2"]}
            fig_cov = px.bar(df_cov,x="Indicator",y=[1]*len(df_cov),color="Status",color_discrete_map=cmap)
            fig_cov.update_layout(**CHART_LAYOUT, height=200, yaxis=dict(showticklabels=False,title=""),
                xaxis=dict(tickangle=45,tickfont=dict(size=8,color=C["subtext"])),
                legend=dict(orientation="h",y=1.3,font=dict(size=9,color=C["subtext"])),
                margin=dict(t=50,b=90,l=10,r=10))
            st.plotly_chart(fig_cov, use_container_width=True)

    with tab_risk:
        st.markdown(f'<div class="vrd-label">TRANSITION & PHYSICAL RISKS · {industry.upper()}</div>', unsafe_allow_html=True)
        RISKS = {
            "Steel & Metals":{
                "E":[("🔴","Carbon pricing / CBAM","EU CBAM directly increases cost on carbon-intensive steel exports; rising carbon prices erode margin.","Accelerate EAF transition; SBTi validation strengthens market access."),
                     ("🟡","Water scarcity","Cooling water availability at risk in water-stressed Indian geographies.","WRI Aqueduct site-level assessment; closed-loop cooling investment."),
                     ("🟢","Green steel premium","Automotive and construction sectors paying premium for certified low-carbon steel.","Pursue ResponsibleSteel or SteelZero; lock in offtake agreements.")],
                "S":[("🔴","Heat stress","Rising ambient temperatures compound worker risk near blast furnaces.","WBGT monitoring; NIOSH acclimatisation protocols; rest rotation schedules."),
                     ("🟡","Community opposition","Air/water quality concerns can block capacity expansion permits.","Community advisory panel; real-time air quality monitoring disclosure.")],
                "G":[("🟡","Supply chain ESG gaps","Unaudited suppliers create CSRD/LkSG regulatory and reputational risk.","Expand audits to Tier 2; adopt OECD RBC Guidance."),
                     ("🟢","ESG-linked financing","SBTi-aligned issuers access green bonds and SLLs at lower cost.","Set credible milestones; engage banks on sustainability-linked loan framework.")]
            },
            "FMCG / Consumer Goods":{
                "E":[("🔴","Plastic EPR regulation","Extended producer responsibility laws increasing compliance cost for non-recyclable packaging.","Shift to monomaterial recyclable packaging; register with national PROs."),
                     ("🟡","Deforestation risk (EUDR)","EU Deforestation Regulation creates market access risk for non-verified palm oil, soy, cocoa.","Satellite monitoring via Global Forest Watch; achieve RSPO segregated certification."),
                     ("🟢","Product carbon labelling","Early movers on ISO 14067 product footprints gaining retailer preference.","Commission LCAs for top 10 SKUs; explore Environmental Product Declarations.")],
                "S":[("🟡","Living wage reputational risk","NGO campaigns on supply chain wage gaps directly impact brand NPS and sales.","Publish Anker-methodology gap assessment; commit to closure timeline.")],
                "G":[("🟢","Consumer trust premium","ESG transparency correlated with willingness-to-pay uplift in premium segments.","Publish GRI-aligned sustainability report; improve CDP score.")]
            }
        }
        default_risks = {
            "E":[("🟡","Carbon pricing","Rising carbon cost on operating margins.","Reduce emissions intensity; internal carbon pricing."),("🟢","Energy efficiency","Operational efficiency reduces both cost and emissions.","ISO 50001 audit; renewable PPA.")],
            "S":[("🟡","Talent risk","Poor ESG reputation increases staff acquisition/retention cost.","Publish pay equity data; improve safety record."),("🟢","Social licence","Strong community relations reduces permitting friction.","Community investment programme.")],
            "G":[("🟡","Governance scrutiny","Institutional investor ESG screens affect cost of capital.","Board skills matrix; ESG committee; TCFD disclosure."),("🟢","ESG-linked capital","Better scores → lower cost on green/SLL financing.","SBTi target; engage banks on SLL.")]
        }
        risks = RISKS.get(industry, {})
        for pillar, pname in [("E","Environmental"),("S","Social"),("G","Governance")]:
            pr = risks.get(pillar, default_risks.get(pillar,[]))
            st.markdown(f'<div style="font-weight:700; color:{C["leaf"]}; font-size:.9rem; margin:12px 0 6px;">▸ {pname}</div>', unsafe_allow_html=True)
            for sev, rname, desc, mit in pr:
                c1,c2 = st.columns([1,5])
                with c1: st.markdown(f'<div style="padding-top:12px; font-size:1rem;">{sev}</div>', unsafe_allow_html=True)
                with c2:
                    st.markdown(f"""<div class="vrd-card" style="padding:12px;">
                      <div style="font-weight:600; color:{C['foam']}; font-size:.88rem;">{rname}</div>
                      <div style="font-size:.8rem; color:{C['subtext']}; margin:3px 0;">{desc}</div>
                      <div class="vrd-strategy" style="margin:4px 0 0; font-size:.8rem;">💡 {mit}</div>
                    </div>""", unsafe_allow_html=True)

    with tab_mat:
        st.markdown(f'<div class="vrd-label">MATERIALITY MATRIX — IMPACT vs FINANCIAL MATERIALITY</div>', unsafe_allow_html=True)
        MATERIALITY = {
            "Steel & Metals":[("Climate & GHG","E",9,9),("Energy efficiency","E",7,8),("Water stewardship","E",6,7),("Scrap circularity","E",7,7),("Air quality","E",8,6),("Worker safety","S",9,9),("Heat stress","S",7,6),("Community","S",6,5),("Board governance","G",6,8),("Anti-corruption","G",5,7)],
            "FMCG / Consumer Goods":[("Packaging plastics","E",9,9),("Climate GHG","E",8,8),("Sustainable sourcing","E",9,7),("Water use","E",6,6),("Product health","S",8,9),("Supply chain labour","S",9,8),("Diversity","S",6,7),("Responsible marketing","G",7,7),("Data privacy","G",6,8)],
        }
        mat = MATERIALITY.get(industry,[("Climate & GHG","E",8,8),("Energy","E",7,7),("Water","E",6,6),("Safety","S",8,8),("Diversity","S",6,6),("Governance","G",7,7)])
        df_mat = pd.DataFrame(mat, columns=["Topic","Pillar","Impact","Financial"])
        pcols = {"E":C["leaf"],"S":C["mint"],"G":C["mist"]}
        fig_mat = go.Figure()
        for p in ["E","S","G"]:
            sub = df_mat[df_mat["Pillar"]==p]
            fig_mat.add_trace(go.Scatter(x=sub["Financial"],y=sub["Impact"],mode="markers+text",
                name={"E":"Environmental","S":"Social","G":"Governance"}[p],
                marker=dict(size=16,color=pcols[p],line=dict(width=1,color=C["bg"])),
                text=sub["Topic"],textposition="top center",textfont=dict(size=9,color=C["subtext"])))
        for x,y,lbl in [(7.5,7.5,"HIGH PRIORITY"),(2.5,7.5,"IMPACT-LED"),(7.5,2.5,"FINANCIALLY LED"),(2.5,2.5,"MONITOR")]:
            fig_mat.add_annotation(x=x,y=y,text=lbl,showarrow=False,font=dict(size=8,color=C["border2"]),opacity=.8)
        fig_mat.add_shape(type="line",x0=5,x1=5,y0=0,y1=11,line=dict(color=C["border2"],width=1,dash="dot"))
        fig_mat.add_shape(type="line",x0=0,x1=11,y0=5,y1=5,line=dict(color=C["border2"],width=1,dash="dot"))
        fig_mat.update_layout(**CHART_LAYOUT, height=420,
            xaxis=dict(title="Financial Materiality →",range=[0,11],gridcolor=C["border"],color=C["subtext"]),
            yaxis=dict(title="↑ Impact on Society/Environment",range=[0,11],gridcolor=C["border"],color=C["subtext"]),
            legend=dict(orientation="h",y=-0.15,font=dict(color=C["subtext"],size=10)))
        st.plotly_chart(fig_mat, use_container_width=True)

    with tab_rep:
        st.markdown(f'<div class="vrd-label">GENERATE REPORT</div>', unsafe_allow_html=True)
        targets = st.session_state.targets.get(ac,[])
        dq = st.session_state.dq.get(ac,{})
        ot = sum(1 for t in targets if t["status"]=="On Track")
        tot_ind = sum(len(get_indicators(industry,p)) for p in ["E","S","G"])
        filled = sum(1 for p in ["E","S","G"] for v in st.session_state.esg_data.get(ac,{}).get(p,{}).values() if isinstance(v,dict) and v.get("current",0))
        ry = cd.get("report_year", CURRENT_YEAR-1)

        report = f"""# Viridis ESG Intelligence Report
## {ac}
**Reporting Year:** {ry}  |  **Industry:** {industry}  |  **Country:** {cd.get('country','')}  
**Frameworks:** {', '.join(cd.get('frameworks',[]))}  |  **Generated:** {datetime.now().strftime('%d %B %Y')}

---

## Executive Summary

{ac} achieved an overall ESG score of **{ov}/100** (Grade **{grade}**) across Environmental ({e_s}/100), Social ({s_s}/100), and Governance ({g_s}/100) dimensions.  
Data coverage: **{round(filled/max(tot_ind,1)*100)}%** ({filled}/{tot_ind} indicators).  
{'Externally assured (' + dq.get("assurance_level","") + ') by ' + dq.get("assurer","") + '.' if dq.get("assured") else 'Not externally assured.'}

Targets: **{ot} on track** · {sum(1 for t in targets if t["status"]=="At Risk")} at risk · {sum(1 for t in targets if t["status"]=="Lagging")} lagging of {len(targets)} total.

---

## Scores

| Dimension | Score | Grade | Weight |
|---|---|---|---|
| Environmental | {e_s} | {score_to_grade(e_s)} | 40% |
| Social | {s_s} | {score_to_grade(s_s)} | 35% |
| Governance | {g_s} | {score_to_grade(g_s)} | 25% |
| **Overall** | **{ov}** | **{grade}** | — |

---

## Target Tracker

| Target | Category | Status | Actual | Expected | Gap |
|---|---|---|---|---|---|
{"".join([f'| {t["name"]} | {t["category"]} | {t["status"]} | {t.get("actual_pct",0)}% | {t.get("expected_pct",0)}% | {round(float(t.get("target_val",0))-float(t.get("current",0)),2):+,} {t.get("unit","")} |{chr(10)}' for t in targets])}

---

## SDG Alignment

{chr(10).join([f'- **SDG {n}: {SDG_NAMES.get(n,"")}**' for n in INDUSTRY_SDGS.get(industry,[])])}

---

## Key Recommendations

1. {'Improve indicator coverage (currently ' + str(round(filled/max(tot_ind,1)*100)) + '%) — higher coverage directly improves all framework scores.' if filled/max(tot_ind,1) < 0.7 else 'Maintain coverage and focus on benchmark outperformance.'}
2. {'Address ' + str(sum(1 for t in targets if t["status"]=="Lagging")) + ' lagging target(s) with urgent action plans and interim milestones.' if any(t["status"]=="Lagging" for t in targets) else 'All targets on track or at risk — maintain trajectory.'}
3. {'Pursue external assurance to strengthen credibility for investor and regulatory audiences.' if not dq.get("assured") else 'Expand assurance scope to remaining ' + str(100-dq.get("coverage_pct",0)) + '% of operations.'}
4. Consider SBTi target submission to access preferential ESG-linked financing and strengthen CDP score.

---

*Generated by Viridis · GRI · SASB · CDP · IFRS S1/S2 · S&P CSA · GRESB · SBTi/IPCC aligned*
"""
        st.markdown(report)
        st.download_button("⬇️ Download Report (.md)", data=report.encode(),
            file_name=f"Viridis_{ac.replace(' ','_')}_{ry}.md", mime="text/markdown")
