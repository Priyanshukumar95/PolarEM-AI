"""
utils/style.py
Shared professional styling for the Streamlit dashboard.
Tailwind-inspired: white background, grey icons/text, soft shadows,
rounded cards, hover lift effect.

Usage — put this at the TOP of app.py and every file in pages/:
    from utils.style import apply_style
    apply_style()

NOTE on the sidebar showing "app" instead of "Dashboard":
Streamlit's multipage nav takes its label straight from the entry file's
name. Rename app.py -> Dashboard.py and the sidebar will show "Dashboard"
automatically — no code change needed. (If you're using the newer
st.navigation()/st.Page() API instead of the pages/ folder convention,
set the label explicitly there instead: st.Page("app.py", title="Dashboard").)
"""

import streamlit as st


def apply_style():
    st.markdown(
        """
        <style>
        /* ---------- Global ---------- */
        html, body, [class*="css"] {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
                         Roboto, Helvetica, Arial, sans-serif;
        }

        .stApp {
            background-color: #FFFFFF;
        }

        /* ---------- Headings ---------- */
        h1 {
            color: #111827 !important;
            font-weight: 700 !important;
        }
        h2, h3 {
            color: #374151 !important;
            font-weight: 600 !important;
        }
        p, span, label, .stCaption {
            color: #6B7280 !important;
        }

        /* ---------- Sidebar ---------- */
        section[data-testid="stSidebar"] {
            background-color: #F9FAFB;
            border-right: 1px solid #E5E7EB;
        }
        section[data-testid="stSidebar"] .stMarkdown {
            color: #374151;
        }

        /* ---------- Sidebar nav arrows ---------- */
        /* Streamlit's auto-generated multipage nav links live inside
           [data-testid="stSidebarNav"] as <li><a>...</a></li>. We prepend
           a "›" arrow to each link and slide it in slightly on hover,
           matching the hover-lift feel used elsewhere in this theme. */
        section[data-testid="stSidebarNav"] ul li a {
            position: relative;
            display: flex;
            align-items: center;
            padding-left: 26px !important;
            border-radius: 8px;
            transition: all 0.2s ease-in-out;
        }
        section[data-testid="stSidebarNav"] ul li a::before {
            content: "›";
            position: absolute;
            left: 8px;
            font-size: 18px;
            font-weight: 700;
            color: #9CA3AF;
            transition: transform 0.2s ease-in-out, color 0.2s ease-in-out;
        }
        section[data-testid="stSidebarNav"] ul li a:hover {
            background-color: #EFF6FF;
        }
        section[data-testid="stSidebarNav"] ul li a:hover::before {
            transform: translateX(3px);
            color: #3B82F6;
        }
        /* Active/selected page: filled arrow + blue accent, so it's obvious
           which page you're on at a glance */
        section[data-testid="stSidebarNav"] ul li a[aria-selected="true"] {
            background-color: #EFF6FF;
            font-weight: 600;
        }
        section[data-testid="stSidebarNav"] ul li a[aria-selected="true"]::before {
            content: "▸";
            color: #3B82F6;
        }

        /* ---------- Metric cards ---------- */
        div[data-testid="stMetric"] {
            background-color: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 12px;
            padding: 18px 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.06);
            transition: all 0.2s ease-in-out;
        }
        div[data-testid="stMetric"]:hover {
            box-shadow: 0 6px 16px rgba(0,0,0,0.10);
            transform: translateY(-2px);
            border-color: #3B82F6;
        }
        div[data-testid="stMetricLabel"] {
            color: #6B7280 !important;
            font-size: 13px !important;
            font-weight: 500 !important;
        }
        div[data-testid="stMetricValue"] {
            color: #111827 !important;
            font-size: 26px !important;
            font-weight: 700 !important;
        }

        /* ---------- Buttons ---------- */
        .stButton>button {
            background-color: #FFFFFF;
            color: #374151;
            border: 1px solid #D1D5DB;
            border-radius: 8px;
            padding: 8px 20px;
            font-weight: 500;
            transition: all 0.2s ease-in-out;
        }
        .stButton>button:hover {
            border-color: #3B82F6;
            color: #3B82F6;
            background-color: #EFF6FF;
            transform: translateY(-1px);
            box-shadow: 0 4px 10px rgba(59,130,246,0.15);
        }
        .stButton>button[kind="primary"] {
            background-color: #3B82F6;
            color: #FFFFFF;
            border: none;
        }
        .stButton>button[kind="primary"]:hover {
            background-color: #2563EB;
            box-shadow: 0 4px 12px rgba(37,99,235,0.35);
        }

        /* ---------- Sliders ---------- */
        .stSlider > div > div > div > div {
            background-color: #3B82F6;
        }

        /* ---------- Dataframes / tables ---------- */
        [data-testid="stDataFrame"] {
            border: 1px solid #E5E7EB;
            border-radius: 10px;
            overflow: hidden;
        }

        /* ---------- Alerts / status boxes ---------- */
        div[data-testid="stAlert"] {
            border-radius: 10px;
            border: 1px solid #E5E7EB;
        }

        /* ---------- Custom card component (see card() helper below) ---------- */
        .custom-card {
            background-color: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 14px;
            padding: 20px 24px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            transition: all 0.2s ease-in-out;
            margin-bottom: 12px;
        }
        .custom-card:hover {
            box-shadow: 0 8px 20px rgba(0,0,0,0.08);
            transform: translateY(-3px);
            border-color: #93C5FD;
        }
        .custom-card-icon {
            font-size: 22px;
            color: #6B7280;
            margin-bottom: 6px;
        }
        .custom-card-title {
            color: #111827;
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 4px;
        }
        .custom-card-desc {
            color: #6B7280;
            font-size: 13px;
        }

        /* ---------- Divider ---------- */
        hr {
            border-color: #E5E7EB !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def card(icon: str, title: str, desc: str):
    """Renders one professional white card with a grey icon, title, and
    description. Use inside st.columns() for a card-grid layout.

    Example:
        c1, c2, c3 = st.columns(3)
        with c1:
            card("📈", "Load Forecast", "24-hour XGBoost prediction")
    """
    st.markdown(
        f"""
        <div class="custom-card">
            <div class="custom-card-icon">{icon}</div>
            <div class="custom-card-title">{title}</div>
            <div class="custom-card-desc">{desc}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
