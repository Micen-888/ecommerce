from __future__ import annotations

from typing import Iterable

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import text

from src.database import get_pg_engine, get_mongo_db, ping_databases

st.set_page_config(
    page_title="Global E-Commerce OLAP",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# -----------------------------------------------------------------------------
# Styling
# -----------------------------------------------------------------------------
def inject_css() -> None:
    st.markdown(
        """
        <style>
            :root {
                --primary: #2563EB;
                --primary-dark: #1D4ED8;
                --primary-soft: #DBEAFE;
                --bg: #F6F8FC;
                --card: #FFFFFF;
                --border: #E2E8F0;
                --text: #0F172A;
                --text-2: #334155;
                --muted: #64748B;
                --muted-2: #475569;
                --sidebar: #0F172A;
                --shadow: 0 14px 42px rgba(15, 23, 42, 0.075);
            }

            html, body, [class*="css"] {
                font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            }

            .stApp {
                background:
                    radial-gradient(circle at 12% 0%, rgba(37, 99, 235, 0.08), transparent 34%),
                    linear-gradient(180deg, #F8FAFC 0%, #EEF2F7 100%);
                color: var(--text);
            }

            .block-container {
                padding-top: 2.2rem;
                padding-bottom: 3.2rem;
                max-width: 1320px;
            }

            [data-testid="stHeader"] {
                background: rgba(248, 250, 252, 0.82);
                backdrop-filter: blur(14px);
                border-bottom: 1px solid rgba(226, 232, 240, 0.9);
            }

            [data-testid="stSidebar"] {
                background: var(--sidebar);
                border-right: 1px solid rgba(255,255,255,0.08);
            }

            [data-testid="stSidebar"] h1,
            [data-testid="stSidebar"] h2,
            [data-testid="stSidebar"] h3,
            [data-testid="stSidebar"] label,
            [data-testid="stSidebar"] p,
            [data-testid="stSidebar"] span {
                color: #F8FAFC !important;
            }

            [data-testid="stSidebar"] .stCaptionContainer,
            [data-testid="stSidebar"] small {
                color: #CBD5E1 !important;
            }

            [data-testid="stSidebar"] div[data-baseweb="select"] > div,
            [data-testid="stSidebar"] input {
                background: #111827 !important;
                border-color: rgba(148, 163, 184, 0.22) !important;
                color: #F8FAFC !important;
            }

            [data-testid="stSidebar"] div[data-baseweb="select"] span {
                color: #F8FAFC !important;
            }

            [data-testid="stSidebar"] .stButton button {
                background: #1E293B;
                border: 1px solid rgba(148, 163, 184, 0.28);
                color: #F8FAFC;
                border-radius: 12px;
            }

            .hero {
                padding: 34px 36px;
                border-radius: 28px;
                background:
                    radial-gradient(circle at top left, rgba(37, 99, 235, 0.18), transparent 32%),
                    linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 52%, #EEF2FF 100%);
                border: 1px solid rgba(203, 213, 225, 0.9);
                box-shadow: var(--shadow);
                margin-bottom: 18px;
            }

            .eyebrow {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                padding: 7px 14px;
                border-radius: 999px;
                background: var(--primary-soft);
                color: var(--primary-dark) !important;
                font-size: 0.78rem;
                font-weight: 900;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                margin-bottom: 14px;
            }

            .hero h1 {
                margin: 0 0 12px 0;
                font-size: clamp(2.35rem, 4vw, 3.55rem);
                line-height: 1.02;
                letter-spacing: -0.065em;
                color: var(--text) !important;
                font-weight: 900;
            }

            .hero p {
                max-width: 920px;
                margin: 0;
                color: var(--muted-2) !important;
                font-size: 1.05rem;
                line-height: 1.75;
                font-weight: 500;
            }

            .kpi-grid {
                display: grid;
                grid-template-columns: repeat(5, minmax(0, 1fr));
                gap: 16px;
                margin: 18px 0 22px 0;
            }

            .kpi-card {
                background: var(--card);
                border: 1px solid var(--border);
                border-radius: 22px;
                padding: 20px 20px 18px 20px;
                box-shadow: 0 12px 32px rgba(15, 23, 42, 0.06);
                min-height: 108px;
            }

            .kpi-label {
                color: var(--muted) !important;
                opacity: 1 !important;
                font-size: 0.82rem;
                font-weight: 800;
                letter-spacing: 0.045em;
                text-transform: uppercase;
                margin-bottom: 10px;
            }

            .kpi-value {
                color: var(--text) !important;
                font-size: 1.7rem;
                font-weight: 900;
                line-height: 1.1;
                letter-spacing: -0.04em;
            }

            @media (max-width: 1100px) {
                .kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
            }

            @media (max-width: 720px) {
                .kpi-grid { grid-template-columns: 1fr; }
                .hero { padding: 26px 24px; }
            }

            .mini-card,
            .section-card,
            .insight-card {
                border-radius: 22px;
                background: rgba(255, 255, 255, 0.98);
                border: 1px solid rgba(226, 232, 240, 0.96);
                box-shadow: 0 12px 34px rgba(15, 23, 42, 0.055);
            }

            .mini-card {
                padding: 20px 20px 18px 20px;
                min-height: 122px;
            }

            .mini-label {
                color: var(--primary-dark) !important;
                font-size: 0.78rem;
                font-weight: 900;
                text-transform: uppercase;
                letter-spacing: 0.06em;
                margin-bottom: 8px;
            }

            .mini-value {
                color: var(--text) !important;
                font-size: 1.65rem;
                font-weight: 900;
                letter-spacing: -0.035em;
                margin-bottom: 5px;
            }

            .mini-help {
                color: var(--muted-2) !important;
                font-size: 0.92rem;
                line-height: 1.62;
                font-weight: 500;
            }

            .section-card {
                padding: 22px 24px;
                margin: 0 0 20px 0;
            }

            .section-card h3 {
                margin: 0 0 8px 0;
                font-size: 1.36rem;
                color: var(--text) !important;
                font-weight: 900;
                letter-spacing: -0.025em;
            }

            .section-card p {
                color: var(--muted-2) !important;
                margin: 0;
                line-height: 1.68;
                font-weight: 500;
            }

            .insight-card {
                padding: 17px 20px;
                margin: 0 0 20px 0;
                border-left: 6px solid var(--primary);
                color: var(--muted-2) !important;
                line-height: 1.68;
                font-weight: 500;
            }

            .insight-card b {
                color: var(--text) !important;
                font-weight: 900;
            }

            .stTabs [data-baseweb="tab-list"] {
                gap: 9px;
                border-bottom: 0;
                margin-top: 12px;
                margin-bottom: 16px;
            }

            .stTabs [data-baseweb="tab"] {
                height: 46px;
                padding: 0 18px;
                border-radius: 999px;
                background: #FFFFFF;
                border: 1px solid var(--border);
                color: var(--text-2) !important;
                font-weight: 800;
                box-shadow: 0 5px 16px rgba(15, 23, 42, 0.045);
            }

            .stTabs [data-baseweb="tab"] p {
                color: var(--text-2) !important;
                font-weight: 800;
            }

            .stTabs [aria-selected="true"] {
                background: var(--primary) !important;
                border-color: var(--primary) !important;
            }

            .stTabs [aria-selected="true"] p {
                color: #FFFFFF !important;
            }

            div[data-testid="stMetric"] {
                background: #FFFFFF;
                border: 1px solid var(--border);
                border-radius: 20px;
                padding: 17px 19px;
                box-shadow: 0 10px 30px rgba(15, 23, 42, 0.055);
            }

            div[data-testid="stMetricLabel"],
            div[data-testid="stMetricLabel"] *,
            div[data-testid="stMetric"] label,
            div[data-testid="stMetric"] label * {
                color: var(--muted) !important;
                opacity: 1 !important;
                font-weight: 800 !important;
            }

            div[data-testid="stMetricValue"],
            div[data-testid="stMetricValue"] * {
                color: var(--text) !important;
                opacity: 1 !important;
                font-weight: 900 !important;
            }

            [data-testid="stDataFrame"] {
                border-radius: 18px;
                overflow: hidden;
                border: 1px solid var(--border);
                box-shadow: 0 10px 30px rgba(15, 23, 42, 0.045);
            }

            .small-muted {
                color: var(--muted-2) !important;
                font-size: 0.92rem;
                line-height: 1.6;
            }

            h1, h2, h3, h4, h5, h6 {
                color: var(--text) !important;
                letter-spacing: -0.02em;
            }

            p, li, span {
                opacity: 1;
            }

            hr {
                margin: 1rem 0 1.5rem 0;
                border-color: var(--border);
            }
        </style>
        """,
        unsafe_allow_html=True,
    )



# -----------------------------------------------------------------------------
# Data loading
# -----------------------------------------------------------------------------
@st.cache_data(ttl=120)
def load_postgres_orders() -> pd.DataFrame:
    query = """
        SELECT
            o.order_id,
            o.order_date,
            c.customer_name,
            c.customer_segment,
            c.country,
            c.region,
            p.product_category,
            p.product_name,
            p.unit_price,
            o.quantity,
            o.total_sales,
            o.profit
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        JOIN products p ON o.product_id = p.product_id
        ORDER BY o.order_date, o.order_id;
    """
    engine = get_pg_engine()
    with engine.connect() as conn:
        return pd.read_sql_query(text(query), conn)


@st.cache_data(ttl=120)
def load_mongo_transaction_details() -> pd.DataFrame:
    db = get_mongo_db()
    pipeline = [
        {
            "$lookup": {
                "from": "shipping_details",
                "localField": "order_id",
                "foreignField": "order_id",
                "as": "shipping_detail",
            }
        },
        {"$unwind": "$shipping_detail"},
        {
            "$project": {
                "_id": 0,
                "order_id": 1,
                "payment_method": "$payment.method",
                "discount_percent": "$pricing.discount_percent",
                "shipping_cost": "$shipping_detail.shipping.cost",
            }
        },
    ]
    docs = list(db.transaction_logs.aggregate(pipeline))
    return pd.DataFrame(docs)


@st.cache_data(ttl=120)
def load_merged_data() -> pd.DataFrame:
    pg_df = load_postgres_orders()
    mongo_df = load_mongo_transaction_details()
    df = pg_df.merge(mongo_df, on="order_id", how="inner")

    df["order_date"] = pd.to_datetime(df["order_date"])
    numeric_cols = [
        "unit_price",
        "quantity",
        "total_sales",
        "profit",
        "discount_percent",
        "shipping_cost",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["profit_margin_percent"] = (df["profit"] / df["total_sales"].replace(0, pd.NA)) * 100
    df["shipping_to_sales_percent"] = (
        df["shipping_cost"] / df["total_sales"].replace(0, pd.NA)
    ) * 100
    df["year"] = df["order_date"].dt.year
    df["month"] = df["order_date"].dt.month
    df["year_month"] = df["order_date"].dt.to_period("M").astype(str)
    df["discount_bucket"] = df["discount_percent"].astype(int).astype(str) + "%"
    return df


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def format_currency(value: float) -> str:
    return f"${value:,.2f}"


def format_percent(value: float) -> str:
    return f"{value:,.2f}%"


def number_delta(current: float, base: float) -> str:
    if base == 0 or pd.isna(base):
        return "0%"
    return f"{((current - base) / base) * 100:+.1f}%"


def polish_chart(fig, height: int = 430):
    """Apply a presentation-safe Plotly style.

    The previous version relied on Plotly/Streamlit default tick colors. On some
    Streamlit themes, axis tick labels and legend labels became too pale. This
    function locks all chart text, ticks, legends, and colorbars to accessible
    dark colors so the dashboard remains readable in a presentation.
    """
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=18, r=18, t=68, b=34),
        title=dict(x=0, xanchor="left", font=dict(size=19, color="#0F172A")),
        font=dict(
            family="Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
            size=13,
            color="#0F172A",
        ),
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="rgba(255,255,255,0)",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.03,
            xanchor="left",
            x=0,
            font=dict(color="#334155", size=13),
            bgcolor="rgba(255,255,255,0)",
        ),
        hoverlabel=dict(
            bgcolor="#FFFFFF",
            bordercolor="#CBD5E1",
            font=dict(color="#0F172A", size=13),
        ),
    )

    axis_title_font = dict(color="#334155", size=13)
    tick_font = dict(color="#334155", size=12)

    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        showline=True,
        linecolor="rgba(100, 116, 139, 0.35)",
        ticks="outside",
        tickcolor="rgba(100, 116, 139, 0.45)",
        tickfont=tick_font,
        title_font=axis_title_font,
    )
    fig.update_yaxes(
        gridcolor="rgba(148, 163, 184, 0.28)",
        zeroline=False,
        showline=True,
        linecolor="rgba(100, 116, 139, 0.35)",
        ticks="outside",
        tickcolor="rgba(100, 116, 139, 0.45)",
        tickfont=tick_font,
        title_font=axis_title_font,
    )

    fig.update_coloraxes(
        colorbar=dict(
            tickfont=dict(color="#334155", size=12),
            title=dict(font=dict(color="#334155", size=13)),
        )
    )

    fig.update_annotations(font=dict(color="#0F172A"))
    return fig


def render_page_header(title: str, subtitle: str, badge: str) -> None:
    st.markdown(
        f"""
        <div class="section-card">
            <div class="eyebrow">{badge}</div>
            <h3>{title}</h3>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.markdown("# 📊 OLAP Control")
    st.sidebar.caption("Kosongkan filter berarti semua data digunakan. Pilih hanya saat ingin slice-and-dice.")

    min_date = df["order_date"].min().date()
    max_date = df["order_date"].max().date()
    selected_range = st.sidebar.date_input(
        "Periode transaksi",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    if isinstance(selected_range, tuple) and len(selected_range) == 2:
        start_date, end_date = selected_range
    else:
        start_date, end_date = min_date, max_date

    def selected_or_all(label: str, values: list[str], help_text: str | None = None) -> list[str]:
        selected = st.sidebar.multiselect(label, values, default=[], placeholder="Semua", help=help_text)
        return selected if selected else values

    all_regions = sorted(df["region"].dropna().unique().tolist())
    selected_regions = selected_or_all("Region", all_regions, "Kosong = semua region")

    country_base = df[df["region"].isin(selected_regions)]
    all_countries = sorted(country_base["country"].dropna().unique().tolist())
    selected_countries = selected_or_all("Country", all_countries, "Country mengikuti region yang dipilih")

    all_segments = sorted(df["customer_segment"].dropna().unique().tolist())
    selected_segments = selected_or_all("Customer segment", all_segments)

    all_categories = sorted(df["product_category"].dropna().unique().tolist())
    selected_categories = selected_or_all("Product category", all_categories)

    with st.sidebar.expander("Database status", expanded=False):
        status = ping_databases()
        st.json(status)
        if st.button("Refresh data cache", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    mask = (
        (df["order_date"].dt.date >= start_date)
        & (df["order_date"].dt.date <= end_date)
        & (df["region"].isin(selected_regions))
        & (df["country"].isin(selected_countries))
        & (df["customer_segment"].isin(selected_segments))
        & (df["product_category"].isin(selected_categories))
    )
    return df.loc[mask].copy()


def metric_cards(df: pd.DataFrame) -> None:
    total_sales = df["total_sales"].sum()
    total_profit = df["profit"].sum()
    total_orders = df["order_id"].nunique()
    avg_margin = (total_profit / total_sales * 100) if total_sales else 0
    avg_discount = df["discount_percent"].mean()

    cols = st.columns(5)
    metrics = [
        ("Total sales", format_currency(total_sales)),
        ("Total profit", format_currency(total_profit)),
        ("Orders", f"{total_orders:,}"),
        ("Profit margin", format_percent(avg_margin)),
        ("Avg. discount", format_percent(avg_discount)),
    ]

    for col, (label, value) in zip(cols, metrics):
        with col:
            st.metric(label=label, value=value)


def show_methodology(df: pd.DataFrame) -> None:
    render_page_header(
        "Metodologi & Rumusan Masalah",
        "Ringkasan rancangan analitik: PostgreSQL untuk data relasional, MongoDB untuk log transaksi dan pengiriman, lalu digabungkan pada layer aplikasi berdasarkan order_id.",
        "Project overview",
    )

    col1, col2, col3 = st.columns(3)
    cards = [
        ("01", "Profitabilitas", "Pola profit berdasarkan kategori produk, segmen pelanggan, dan wilayah geografis."),
        ("02", "Tren Penjualan", "Tren bulanan, seasonal pattern, serta produk/kategori terbaik dan terburuk."),
        ("03", "Diskon & Pengiriman", "Efektivitas diskon dan efisiensi shipping cost terhadap margin profit."),
    ]
    for col, (num, title, body) in zip([col1, col2, col3], cards):
        col.markdown(
            f"""
            <div class="mini-card">
                <div class="mini-label">Problem {num}</div>
                <div class="mini-value" style="font-size: 1.25rem;">{title}</div>
                <div class="mini-help">{body}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("### Arsitektur Dual-Database")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            """
            <div class="section-card">
                <h3>PostgreSQL</h3>
                <p>Menangani tabel relasional: <b>customers</b>, <b>products</b>, dan <b>orders</b>. Dipakai untuk JOIN, GROUP BY, agregasi profit, tren waktu, dan dimensi OLAP.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """
            <div class="section-card">
                <h3>MongoDB</h3>
                <p>Menangani dokumen semi-terstruktur: <b>transaction_logs</b> dan <b>shipping_details</b>. Dipakai untuk diskon, payment method, dan shipping cost.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("### Health Check Dataset")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Rows", f"{len(df):,}")
    col2.metric("Countries", f"{df['country'].nunique():,}")
    col3.metric("Regions", f"{df['region'].nunique():,}")
    col4.metric("Categories", f"{df['product_category'].nunique():,}")

    with st.expander("Lihat formula metrik analitik"):
        st.code(
            """
Profit Margin (%) = Profit / Total Sales * 100
Shipping-to-Sales Ratio (%) = Shipping Cost / Total Sales * 100
Discount Efficiency = Profit Margin setelah diskon dibandingkan antar level diskon
            """.strip(),
            language="text",
        )


def show_problem_1(df: pd.DataFrame) -> None:
    render_page_header(
        "Analisis Profitabilitas",
        "Mencari kategori, segmen, dan wilayah yang memberi kontribusi profit terbesar serta margin terbaik.",
        "Problem 1",
    )

    category_profit = (
        df.groupby("product_category", as_index=False)
        .agg(total_sales=("total_sales", "sum"), total_profit=("profit", "sum"), orders=("order_id", "nunique"))
    )
    category_profit["profit_margin_percent"] = category_profit["total_profit"] / category_profit["total_sales"] * 100
    category_profit = category_profit.sort_values("total_profit", ascending=False)

    best_category = category_profit.iloc[0]
    st.markdown(
        f"""
        <div class="insight-card">
            <b>Insight utama:</b> kategori dengan profit terbesar adalah <b>{best_category['product_category']}</b>
            dengan total profit <b>{format_currency(best_category['total_profit'])}</b> dan margin
            <b>{format_percent(best_category['profit_margin_percent'])}</b>.
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1.08, 0.92])
    with col1:
        fig = px.bar(
            category_profit,
            x="product_category",
            y="total_profit",
            text="profit_margin_percent",
            title="Total profit by product category",
            labels={"product_category": "Product category", "total_profit": "Total profit", "profit_margin_percent": "Profit margin (%)"},
        )
        fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
        fig.update_layout(yaxis_tickprefix="$", xaxis_title=None)
        st.plotly_chart(polish_chart(fig, 430), use_container_width=True)

    with col2:
        segment_profit = (
            df.groupby("customer_segment", as_index=False)
            .agg(total_sales=("total_sales", "sum"), total_profit=("profit", "sum"), orders=("order_id", "nunique"))
        )
        segment_profit["profit_margin_percent"] = segment_profit["total_profit"] / segment_profit["total_sales"] * 100
        fig = px.pie(
            segment_profit,
            names="customer_segment",
            values="total_profit",
            title="Profit contribution by customer segment",
            hole=0.48,
        )
        st.plotly_chart(polish_chart(fig, 430), use_container_width=True)

    heatmap = (
        df.groupby(["region", "customer_segment"], as_index=False)
        .agg(total_sales=("total_sales", "sum"), total_profit=("profit", "sum"))
    )
    heatmap["profit_margin_percent"] = heatmap["total_profit"] / heatmap["total_sales"] * 100
    pivot = heatmap.pivot(index="region", columns="customer_segment", values="profit_margin_percent")
    fig = px.imshow(
        pivot,
        text_auto=".2f",
        aspect="auto",
        title="Profit margin heatmap: region × customer segment",
        labels=dict(x="Customer segment", y="Region", color="Profit margin (%)"),
    )
    st.plotly_chart(polish_chart(fig, 460), use_container_width=True)

    ranking = (
        df.groupby(["region", "customer_segment", "product_category", "product_name"], as_index=False)
        .agg(orders=("order_id", "nunique"), total_sales=("total_sales", "sum"), total_profit=("profit", "sum"))
    )
    ranking["profit_margin_percent"] = ranking["total_profit"] / ranking["total_sales"] * 100
    ranking = ranking.sort_values("total_profit", ascending=False)

    st.markdown("### Ranking profitabilitas produk")
    st.dataframe(
        ranking.head(20),
        use_container_width=True,
        hide_index=True,
        column_config={
            "total_sales": st.column_config.NumberColumn("Total sales", format="$%.2f"),
            "total_profit": st.column_config.NumberColumn("Total profit", format="$%.2f"),
            "profit_margin_percent": st.column_config.NumberColumn("Profit margin", format="%.2f%%"),
        },
    )


def show_problem_2(df: pd.DataFrame) -> None:
    render_page_header(
        "Analisis Tren Penjualan & Seasonal",
        "Melihat pola monthly sales/profit, peak season, serta produk dengan performa terbaik dan terburuk.",
        "Problem 2",
    )

    monthly = (
        df.groupby("year_month", as_index=False)
        .agg(total_sales=("total_sales", "sum"), total_profit=("profit", "sum"), orders=("order_id", "nunique"))
        .sort_values("year_month")
    )
    monthly["profit_margin_percent"] = monthly["total_profit"] / monthly["total_sales"] * 100
    peak_month = monthly.sort_values("total_sales", ascending=False).iloc[0]

    st.markdown(
        f"""
        <div class="insight-card">
            <b>Peak sales period:</b> bulan <b>{peak_month['year_month']}</b> mencatat sales tertinggi,
            yaitu <b>{format_currency(peak_month['total_sales'])}</b> dari <b>{int(peak_month['orders']):,}</b> order.
        </div>
        """,
        unsafe_allow_html=True,
    )

    fig = px.line(
        monthly,
        x="year_month",
        y=["total_sales", "total_profit"],
        markers=True,
        title="Monthly sales and profit trend",
        labels={"year_month": "Month", "value": "Amount", "variable": "Metric"},
    )
    fig.update_layout(yaxis_tickprefix="$", xaxis_title=None)
    st.plotly_chart(polish_chart(fig, 470), use_container_width=True)

    category_monthly = (
        df.groupby(["year_month", "product_category"], as_index=False)
        .agg(total_sales=("total_sales", "sum"), total_profit=("profit", "sum"))
        .sort_values("year_month")
    )
    fig = px.line(
        category_monthly,
        x="year_month",
        y="total_sales",
        color="product_category",
        markers=True,
        title="Monthly sales comparison by product category",
        labels={"year_month": "Month", "total_sales": "Total sales", "product_category": "Category"},
    )
    fig.update_layout(yaxis_tickprefix="$", xaxis_title=None)
    st.plotly_chart(polish_chart(fig, 470), use_container_width=True)

    col1, col2 = st.columns([0.95, 1.05])
    with col1:
        seasonal = (
            df.groupby("month", as_index=False)
            .agg(avg_sales=("total_sales", "mean"), total_sales=("total_sales", "sum"), orders=("order_id", "nunique"))
            .sort_values("month")
        )
        seasonal["month_name"] = pd.to_datetime(seasonal["month"], format="%m").dt.strftime("%b")
        fig = px.bar(
            seasonal,
            x="month_name",
            y="avg_sales",
            title="Seasonal pattern: average sales by month",
            labels={"month_name": "Month", "avg_sales": "Average sales per transaction"},
        )
        fig.update_layout(yaxis_tickprefix="$", xaxis_title=None)
        st.plotly_chart(polish_chart(fig, 430), use_container_width=True)

    with col2:
        product_perf = (
            df.groupby(["product_category", "product_name"], as_index=False)
            .agg(total_sales=("total_sales", "sum"), total_profit=("profit", "sum"), orders=("order_id", "nunique"))
        )
        product_perf["profit_margin_percent"] = product_perf["total_profit"] / product_perf["total_sales"] * 100
        top10 = product_perf.sort_values("total_profit", ascending=False).head(10)
        fig = px.bar(
            top10.sort_values("total_profit"),
            x="total_profit",
            y="product_name",
            orientation="h",
            title="Top 10 products by profit",
            labels={"total_profit": "Total profit", "product_name": "Product"},
        )
        fig.update_layout(xaxis_tickprefix="$", yaxis_title=None)
        st.plotly_chart(polish_chart(fig, 430), use_container_width=True)

    st.markdown("### Bottom 10 produk berdasarkan profit")
    product_perf = (
        df.groupby(["product_category", "product_name"], as_index=False)
        .agg(total_sales=("total_sales", "sum"), total_profit=("profit", "sum"), orders=("order_id", "nunique"))
    )
    product_perf["profit_margin_percent"] = product_perf["total_profit"] / product_perf["total_sales"] * 100
    st.dataframe(
        product_perf.sort_values("total_profit", ascending=True).head(10),
        use_container_width=True,
        hide_index=True,
        column_config={
            "total_sales": st.column_config.NumberColumn("Total sales", format="$%.2f"),
            "total_profit": st.column_config.NumberColumn("Total profit", format="$%.2f"),
            "profit_margin_percent": st.column_config.NumberColumn("Profit margin", format="%.2f%%"),
        },
    )


def show_problem_3(df: pd.DataFrame) -> None:
    render_page_header(
        "Efektivitas Diskon & Efisiensi Biaya Pengiriman",
        "Mengukur apakah diskon dan shipping cost masih menghasilkan margin yang sehat pada tiap kategori, wilayah, dan segmen pelanggan.",
        "Problem 3",
    )

    discount_perf = (
        df.groupby("discount_percent", as_index=False)
        .agg(total_sales=("total_sales", "sum"), total_profit=("profit", "sum"), orders=("order_id", "nunique"))
        .sort_values("discount_percent")
    )
    discount_perf["profit_margin_percent"] = discount_perf["total_profit"] / discount_perf["total_sales"] * 100

    if len(discount_perf) > 1:
        lowest_discount = discount_perf.iloc[0]
        highest_discount = discount_perf.iloc[-1]
        margin_drop = lowest_discount["profit_margin_percent"] - highest_discount["profit_margin_percent"]
    else:
        margin_drop = 0

    st.markdown(
        f"""
        <div class="insight-card">
            <b>Insight utama:</b> semakin tinggi diskon, margin cenderung turun. Selisih margin antara diskon terendah dan tertinggi pada filter aktif adalah <b>{margin_drop:.2f} percentage points</b>.
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        fig = px.bar(
            discount_perf,
            x="discount_percent",
            y="profit_margin_percent",
            text="profit_margin_percent",
            title="Profit margin by discount level",
            labels={"discount_percent": "Discount (%)", "profit_margin_percent": "Profit margin (%)"},
        )
        fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
        st.plotly_chart(polish_chart(fig, 430), use_container_width=True)

    with col2:
        shipping_summary = (
            df.groupby("region", as_index=False)
            .agg(total_sales=("total_sales", "sum"), total_profit=("profit", "sum"), shipping_cost=("shipping_cost", "sum"))
        )
        shipping_summary["profit_margin_percent"] = shipping_summary["total_profit"] / shipping_summary["total_sales"] * 100
        shipping_summary["shipping_to_sales_percent"] = shipping_summary["shipping_cost"] / shipping_summary["total_sales"] * 100
        fig = px.scatter(
            shipping_summary,
            x="shipping_to_sales_percent",
            y="profit_margin_percent",
            size="total_sales",
            hover_name="region",
            title="Shipping efficiency vs profit margin by region",
            labels={
                "shipping_to_sales_percent": "Shipping-to-sales ratio (%)",
                "profit_margin_percent": "Profit margin (%)",
                "total_sales": "Total sales",
            },
        )
        st.plotly_chart(polish_chart(fig, 430), use_container_width=True)

    fig = px.scatter(
        df,
        x="shipping_to_sales_percent",
        y="profit_margin_percent",
        color="discount_bucket",
        hover_data=["order_id", "region", "customer_segment", "product_category", "total_sales", "profit"],
        title="Transaction-level risk map: shipping ratio vs profit margin",
        labels={
            "shipping_to_sales_percent": "Shipping-to-sales ratio (%)",
            "profit_margin_percent": "Profit margin (%)",
            "discount_bucket": "Discount",
        },
    )
    st.plotly_chart(polish_chart(fig, 500), use_container_width=True)

    heatmap = (
        df.groupby(["region", "product_category"], as_index=False)
        .agg(total_sales=("total_sales", "sum"), total_profit=("profit", "sum"), shipping_cost=("shipping_cost", "sum"))
    )
    heatmap["profit_margin_percent"] = heatmap["total_profit"] / heatmap["total_sales"] * 100
    pivot = heatmap.pivot(index="region", columns="product_category", values="profit_margin_percent")
    fig = px.imshow(
        pivot,
        text_auto=".2f",
        aspect="auto",
        title="Profit margin heatmap: region × product category",
        labels=dict(x="Product category", y="Region", color="Profit margin (%)"),
    )
    st.plotly_chart(polish_chart(fig, 460), use_container_width=True)

    risk = (
        df.groupby(["region", "customer_segment", "product_category"], as_index=False)
        .agg(
            orders=("order_id", "nunique"),
            avg_discount=("discount_percent", "mean"),
            total_sales=("total_sales", "sum"),
            total_profit=("profit", "sum"),
            shipping_cost=("shipping_cost", "sum"),
        )
    )
    risk["profit_margin_percent"] = risk["total_profit"] / risk["total_sales"] * 100
    risk["shipping_to_sales_percent"] = risk["shipping_cost"] / risk["total_sales"] * 100
    risk = risk.sort_values(["profit_margin_percent", "shipping_to_sales_percent"], ascending=[True, False])

    st.markdown("### Area risiko margin rendah")
    st.dataframe(
        risk.head(20),
        use_container_width=True,
        hide_index=True,
        column_config={
            "avg_discount": st.column_config.NumberColumn("Avg. discount", format="%.2f%%"),
            "total_sales": st.column_config.NumberColumn("Total sales", format="$%.2f"),
            "total_profit": st.column_config.NumberColumn("Total profit", format="$%.2f"),
            "shipping_cost": st.column_config.NumberColumn("Shipping cost", format="$%.2f"),
            "profit_margin_percent": st.column_config.NumberColumn("Profit margin", format="%.2f%%"),
            "shipping_to_sales_percent": st.column_config.NumberColumn("Shipping-to-sales", format="%.2f%%"),
        },
    )


def show_raw_data(df: pd.DataFrame) -> None:
    render_page_header(
        "Data Explorer",
        "Tabel gabungan PostgreSQL + MongoDB berdasarkan order_id. Gunakan filter di sidebar untuk eksplorasi OLAP.",
        "Exploration",
    )
    st.dataframe(df, use_container_width=True, hide_index=True)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Export filtered data to CSV",
        data=csv,
        file_name="filtered_ecommerce_olap.csv",
        mime="text/csv",
        use_container_width=True,
    )


def main() -> None:
    inject_css()

    try:
        df = load_merged_data()
    except Exception as exc:
        st.error("Data belum tersedia atau koneksi database gagal.")
        st.code(str(exc), language="text")
        st.info("Jalankan MongoDB, PostgreSQL, lalu ETL: `python -m src.etl`.")
        st.stop()

    filtered_df = apply_filters(df)
    if filtered_df.empty:
        st.warning("Tidak ada data yang sesuai dengan filter yang dipilih.")
        st.stop()

    st.markdown(
        """
        <div class="hero">
            <span class="eyebrow">PostgreSQL + MongoDB · OLAP Dashboard</span>
            <h1>Global E-Commerce Analytics</h1>
            <p>Dashboard analitik untuk membaca profitabilitas, tren penjualan, efektivitas diskon, dan efisiensi biaya pengiriman. Dirancang untuk presentasi proyek pemodelan data dengan filter OLAP yang ringkas dan visual yang lebih rapi.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    metric_cards(filtered_df)

    tab0, tab1, tab2, tab3, tab4 = st.tabs(
        [
            "Overview",
            "Profitabilitas",
            "Tren Penjualan",
            "Diskon & Pengiriman",
            "Data Explorer",
        ]
    )

    with tab0:
        show_methodology(filtered_df)
    with tab1:
        show_problem_1(filtered_df)
    with tab2:
        show_problem_2(filtered_df)
    with tab3:
        show_problem_3(filtered_df)
    with tab4:
        show_raw_data(filtered_df)


if __name__ == "__main__":
    main()
