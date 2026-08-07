import streamlit as st

STATUS_STYLES = {
    "shortlisted": {"emoji": "🟢", "label": "Shortlisted", "bg": "#dcfce7", "fg": "#15803d"},
    "pending": {"emoji": "🟡", "label": "Pending", "bg": "#fef9c3", "fg": "#a16207"},
    "rejected": {"emoji": "🔴", "label": "Rejected", "bg": "#fee2e2", "fg": "#b91c1c"},
}

PRIMARY = "#4f46e5"
PRIMARY_DARK = "#3730a3"
SURFACE = "#ffffff"
BORDER = "#e5e7eb"
MUTED = "#6b7280"


def apply_theme() -> None:
    st.markdown(
        f"""
        <style>
        .block-container {{
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1200px;
        }}

        [data-testid="stSidebar"] {{
            background-color: #111827;
        }}
        [data-testid="stSidebar"] * {{
            color: #e5e7eb !important;
        }}
        [data-testid="stSidebarNav"] a {{
            border-radius: 8px;
            padding: 0.4rem 0.6rem !important;
            margin: 0.1rem 0.5rem;
        }}
        [data-testid="stSidebarNav"] a:hover {{
            background-color: #1f2937;
        }}
        [data-testid="stSidebarNav"] a[aria-current="page"] {{
            background-color: {PRIMARY};
        }}
        [data-testid="stSidebarNav"] a[aria-current="page"] span {{
            color: white !important;
            font-weight: 600;
        }}

        h1, h2, h3 {{
            letter-spacing: -0.01em;
        }}

        .app-header {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding-bottom: 0.25rem;
        }}
        .app-header .badge {{
            background: {PRIMARY};
            color: white;
            font-size: 0.7rem;
            font-weight: 700;
            padding: 0.15rem 0.55rem;
            border-radius: 999px;
            letter-spacing: 0.04em;
        }}

        .kpi-card {{
            background: {SURFACE};
            border: 1px solid {BORDER};
            border-radius: 14px;
            padding: 1.1rem 1.25rem;
            box-shadow: 0 1px 2px rgba(0,0,0,0.04);
        }}
        .kpi-card .kpi-label {{
            color: {MUTED};
            font-size: 0.82rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.03em;
        }}
        .kpi-card .kpi-value {{
            font-size: 1.9rem;
            font-weight: 700;
            color: #111827;
            margin-top: 0.15rem;
        }}
        .kpi-card .kpi-icon {{
            font-size: 1.4rem;
        }}

        .status-chip {{
            display: inline-block;
            padding: 0.15rem 0.6rem;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 600;
            white-space: nowrap;
        }}

        .skill-chip {{
            display: inline-block;
            background: #eef2ff;
            color: {PRIMARY_DARK};
            padding: 0.1rem 0.55rem;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 600;
            margin: 0.1rem 0.25rem 0.1rem 0;
        }}

        .missing-chip {{
            display: inline-block;
            background: #fef2f2;
            color: #b91c1c;
            padding: 0.1rem 0.55rem;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 600;
            margin: 0.1rem 0.25rem 0.1rem 0;
        }}

        div[data-testid="stMetric"] {{
            background: {SURFACE};
            border: 1px solid {BORDER};
            border-radius: 14px;
            padding: 0.9rem 1rem;
        }}

        .stButton > button {{
            border-radius: 8px;
            font-weight: 600;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str = "", emoji: str = "") -> None:
    st.markdown(
        f"""
        <div class="app-header">
            <span style="font-size:1.7rem;">{emoji}</span>
            <div>
                <div style="font-size:1.5rem; font-weight:700; color:#111827;">{title}</div>
                <div style="color:{MUTED}; font-size:0.92rem;">{subtitle}</div>
            </div>
        </div>
        <hr style="margin: 0.75rem 0 1.25rem 0; border-color:#e5e7eb;" />
        """,
        unsafe_allow_html=True,
    )


def kpi_card(label: str, value: str, icon: str) -> str:
    return f"""
    <div class="kpi-card">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
    </div>
    """


def status_chip(status: str) -> str:
    style = STATUS_STYLES.get(status, STATUS_STYLES["pending"])
    return (
        f'<span class="status-chip" style="background:{style["bg"]}; color:{style["fg"]};">'
        f'{style["emoji"]} {style["label"]}</span>'
    )


def skill_chips(skills: list[str], limit: int = 6) -> str:
    if not skills:
        return '<span style="color:#9ca3af; font-size:0.85rem;">No skills extracted</span>'
    chips = "".join(f'<span class="skill-chip">{s}</span>' for s in skills[:limit])
    remainder = len(skills) - limit
    if remainder > 0:
        chips += f'<span class="skill-chip">+{remainder} more</span>'
    return chips


def missing_chips(skills: list[str], limit: int = 6) -> str:
    if not skills:
        return '<span style="color:#9ca3af; font-size:0.85rem;">None</span>'
    chips = "".join(f'<span class="missing-chip">{s}</span>' for s in skills[:limit])
    remainder = len(skills) - limit
    if remainder > 0:
        chips += f'<span class="missing-chip">+{remainder} more</span>'
    return chips
