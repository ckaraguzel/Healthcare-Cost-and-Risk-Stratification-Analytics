"""
04_dashboard.py
Healthcare Cost & Risk Stratification Analytics
------------------------------------------------
Interactive dashboard built with Plotly Dash.
Replaces Tableau — run this file and open http://127.0.0.1:8050

Install deps first (in terminal):
    pip install dash plotly pandas
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
import sqlite3
import os

# ── Load data ───────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH  = os.path.join(BASE_DIR, "data", "healthcare.db")

conn = sqlite3.connect(DB_PATH)
df   = pd.read_sql("SELECT * FROM patients", conn)
conn.close()

age_order = ["Under 30", "30-50", "50+"]
bmi_order = ["Underweight", "Normal", "Overweight", "Obese"]
df["age_group"]    = pd.Categorical(df["age_group"],    categories=age_order,  ordered=True)
df["bmi_category"] = pd.Categorical(df["bmi_category"], categories=bmi_order,  ordered=True)
df["smoker_label"] = df["smoker"].map({"yes": "Smoker", "no": "Non-Smoker"})

# ── Color scheme ─────────────────────────────────────────────────────────────
COLOR_PRIMARY   = "#2563EB"
COLOR_DANGER    = "#DC2626"
COLOR_WARNING   = "#D97706"
COLOR_SUCCESS   = "#16A34A"
COLOR_BG        = "#F8FAFC"
COLOR_CARD      = "#FFFFFF"
COLOR_TEXT      = "#1E293B"
COLOR_MUTED     = "#64748B"

SMOKE_COLORS = {"Smoker": COLOR_DANGER, "Non-Smoker": COLOR_PRIMARY}

# ── KPI helpers ─────────────────────────────────────────────────────────────
def kpi_card(title, value, subtitle="", color=COLOR_PRIMARY):
    return html.Div([
        html.P(title, style={"margin": "0 0 4px", "fontSize": "12px",
                              "color": COLOR_MUTED, "fontWeight": "600",
                              "textTransform": "uppercase", "letterSpacing": "0.05em"}),
        html.H2(value, style={"margin": "0 0 2px", "fontSize": "28px",
                               "color": color, "fontWeight": "700"}),
        html.P(subtitle, style={"margin": 0, "fontSize": "12px", "color": COLOR_MUTED}),
    ], style={
        "background":    COLOR_CARD,
        "borderRadius":  "12px",
        "padding":       "20px 24px",
        "boxShadow":     "0 1px 4px rgba(0,0,0,0.08)",
        "flex":          "1",
        "minWidth":      "160px",
    })

# ── Pre-compute KPIs ─────────────────────────────────────────────────────────
total_patients  = len(df)
avg_cost        = df["charges"].mean()
smoker_avg      = df[df["smoker"] == "yes"]["charges"].mean()
nonsmoker_avg   = df[df["smoker"] == "no"]["charges"].mean()
high_risk_count = df["high_risk_flag"].sum()
high_risk_pct   = high_risk_count / total_patients * 100
hr_cost_pct     = df[df["high_risk_flag"] == 1]["charges"].sum() / df["charges"].sum() * 100

# ── App Layout ───────────────────────────────────────────────────────────────
app = Dash(__name__, title="Healthcare Cost Analytics")

app.layout = html.Div(style={"background": COLOR_BG, "minHeight": "100vh",
                              "fontFamily": "'Inter', 'Segoe UI', sans-serif",
                              "color": COLOR_TEXT}, children=[

    # ── Header ──
    html.Div([
        html.H1("Healthcare Cost & Risk Stratification",
                style={"margin": "0", "fontSize": "22px", "fontWeight": "700", "color": "white"}),
        html.P("Medical Cost Personal Dataset  ·  ~1,300 Patients",
               style={"margin": "4px 0 0", "fontSize": "13px", "color": "rgba(255,255,255,0.75)"}),
    ], style={"background": COLOR_PRIMARY, "padding": "20px 32px"}),

    html.Div(style={"padding": "24px 32px"}, children=[

        # ── Filters ──
        html.Div([
            html.Label("Filter by Smoking Status", style={"fontWeight": "600", "fontSize": "13px"}),
            dcc.Checklist(
                id="filter-smoker",
                options=[{"label": " Smoker", "value": "yes"},
                         {"label": " Non-Smoker", "value": "no"}],
                value=["yes", "no"],
                inline=True,
                style={"marginTop": "6px", "gap": "16px"}
            ),
        ], style={"background": COLOR_CARD, "borderRadius": "10px",
                   "padding": "14px 20px", "marginBottom": "20px",
                   "boxShadow": "0 1px 4px rgba(0,0,0,0.06)", "display": "flex",
                   "alignItems": "center", "gap": "24px"}),

        # ── KPI Row ──
        html.Div(id="kpi-row", style={"display": "flex", "gap": "16px",
                                        "flexWrap": "wrap", "marginBottom": "24px"}),

        # ── Row 1: Scatter + Smoking Bar ──
        html.Div([
            html.Div([
                dcc.Graph(id="scatter-age-charges", style={"height": "380px"})
            ], style={"flex": "2", "background": COLOR_CARD, "borderRadius": "12px",
                       "padding": "16px", "boxShadow": "0 1px 4px rgba(0,0,0,0.08)"}),

            html.Div([
                dcc.Graph(id="bar-smoking", style={"height": "380px"})
            ], style={"flex": "1", "background": COLOR_CARD, "borderRadius": "12px",
                       "padding": "16px", "boxShadow": "0 1px 4px rgba(0,0,0,0.08)"}),
        ], style={"display": "flex", "gap": "16px", "marginBottom": "16px"}),

        # ── Row 2: Age Group + BMI + Region ──
        html.Div([
            html.Div([dcc.Graph(id="bar-age", style={"height": "320px"})],
                     style={"flex": "1", "background": COLOR_CARD, "borderRadius": "12px",
                             "padding": "16px", "boxShadow": "0 1px 4px rgba(0,0,0,0.08)"}),
            html.Div([dcc.Graph(id="bar-bmi", style={"height": "320px"})],
                     style={"flex": "1", "background": COLOR_CARD, "borderRadius": "12px",
                             "padding": "16px", "boxShadow": "0 1px 4px rgba(0,0,0,0.08)"}),
            html.Div([dcc.Graph(id="bar-region", style={"height": "320px"})],
                     style={"flex": "1", "background": COLOR_CARD, "borderRadius": "12px",
                             "padding": "16px", "boxShadow": "0 1px 4px rgba(0,0,0,0.08)"}),
        ], style={"display": "flex", "gap": "16px", "marginBottom": "16px"}),

        # ── Row 3: Heatmap + High-Risk donut ──
        html.Div([
            html.Div([dcc.Graph(id="heatmap", style={"height": "320px"})],
                     style={"flex": "2", "background": COLOR_CARD, "borderRadius": "12px",
                             "padding": "16px", "boxShadow": "0 1px 4px rgba(0,0,0,0.08)"}),
            html.Div([dcc.Graph(id="donut-risk", style={"height": "320px"})],
                     style={"flex": "1", "background": COLOR_CARD, "borderRadius": "12px",
                             "padding": "16px", "boxShadow": "0 1px 4px rgba(0,0,0,0.08)"}),
        ], style={"display": "flex", "gap": "16px"}),
    ]),
])

# ── Callbacks ────────────────────────────────────────────────────────────────
@app.callback(
    Output("kpi-row",          "children"),
    Output("scatter-age-charges", "figure"),
    Output("bar-smoking",       "figure"),
    Output("bar-age",           "figure"),
    Output("bar-bmi",           "figure"),
    Output("bar-region",        "figure"),
    Output("heatmap",           "figure"),
    Output("donut-risk",        "figure"),
    Input("filter-smoker",      "value"),
)
def update_all(smoker_filter):
    filtered = df[df["smoker"].isin(smoker_filter)]

    # ── KPIs ──
    n        = len(filtered)
    avg      = filtered["charges"].mean() if n > 0 else 0
    hr_n     = filtered["high_risk_flag"].sum()
    hr_share = filtered[filtered["high_risk_flag"]==1]["charges"].sum() / filtered["charges"].sum() * 100 if n > 0 else 0

    kpis = html.Div([
        kpi_card("Total Patients",       f"{n:,}",          "in filtered view"),
        kpi_card("Avg Annual Cost",       f"${avg:,.0f}",    "per patient",       color=COLOR_PRIMARY),
        kpi_card("Smoker Avg Cost",       f"${smoker_avg:,.0f}",  f"{smoker_avg/nonsmoker_avg:.1f}× non-smoker", color=COLOR_DANGER),
        kpi_card("High-Risk Patients",    f"{int(hr_n):,}",  f"{hr_share:.0f}% of total cost", color=COLOR_WARNING),
        kpi_card("High-Risk Cost Share",  f"{hr_share:.1f}%", "smoker + obese",   color=COLOR_DANGER),
    ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap"})

    LAYOUT = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Segoe UI, sans-serif", color=COLOR_TEXT, size=12),
        margin=dict(t=40, b=40, l=50, r=20),
    )

    # ── Scatter ──
    scatter = px.scatter(
        filtered, x="age", y="charges", color="smoker_label",
        color_discrete_map=SMOKE_COLORS,
        opacity=0.55, title="Age vs Annual Charges",
        labels={"age": "Age", "charges": "Annual Charges ($)", "smoker_label": "Status"},
    )
    scatter.update_yaxes(tickformat="$,.0f")
    scatter.update_layout(**LAYOUT)

    # ── Smoking bar ──
    sm = filtered.groupby("smoker_label")["charges"].mean().reset_index()
    sm.columns = ["smoker_label", "avg_charges"]
    smoke_bar = px.bar(sm, x="smoker_label", y="avg_charges",
                        color="smoker_label", color_discrete_map=SMOKE_COLORS,
                        title="Avg Cost by Smoking Status",
                        labels={"smoker_label": "", "avg_charges": "Avg Charges ($)"},
                        text_auto="$,.0f")
    smoke_bar.update_yaxes(tickformat="$,.0f")
    smoke_bar.update_traces(texttemplate="$%{y:,.0f}", textposition="outside")
    smoke_bar.update_layout(**LAYOUT, showlegend=False)

    # ── Age group bar ──
    ag = filtered.groupby("age_group", observed=True)["charges"].mean().reset_index()
    age_bar = px.bar(ag, x="age_group", y="charges",
                      color="age_group",
                      color_discrete_sequence=[COLOR_PRIMARY, COLOR_WARNING, COLOR_DANGER],
                      title="Avg Cost by Age Group",
                      labels={"age_group": "", "charges": "Avg Charges ($)"})
    age_bar.update_yaxes(tickformat="$,.0f")
    age_bar.update_traces(texttemplate="$%{y:,.0f}", textposition="outside")
    age_bar.update_layout(**LAYOUT, showlegend=False)

    # ── BMI bar ──
    bmi = filtered.groupby("bmi_category", observed=True)["charges"].mean().reset_index()
    bmi_bar = px.bar(bmi, x="bmi_category", y="charges",
                      color="bmi_category",
                      color_discrete_sequence=["#7ED6C8","#4A90D9","#F5A623","#E05252"],
                      title="Avg Cost by BMI Category",
                      labels={"bmi_category": "", "charges": "Avg Charges ($)"})
    bmi_bar.update_yaxes(tickformat="$,.0f")
    bmi_bar.update_traces(texttemplate="$%{y:,.0f}", textposition="outside")
    bmi_bar.update_layout(**LAYOUT, showlegend=False)

    # ── Region bar ──
    reg = filtered.groupby("region")["charges"].mean().reset_index().sort_values("charges", ascending=False)
    reg_bar = px.bar(reg, x="region", y="charges",
                      color_discrete_sequence=[COLOR_PRIMARY],
                      title="Avg Cost by Region",
                      labels={"region": "", "charges": "Avg Charges ($)"})
    reg_bar.update_yaxes(tickformat="$,.0f")
    reg_bar.update_traces(texttemplate="$%{y:,.0f}", textposition="outside",
                           marker_color=COLOR_PRIMARY)
    reg_bar.update_layout(**LAYOUT, showlegend=False)

    # ── Heatmap ──
    pivot = filtered.pivot_table(values="charges", index="smoker_label",
                                  columns="bmi_category", aggfunc="mean", observed=True)
    heatmap_fig = go.Figure(go.Heatmap(
        z=pivot.values, x=list(pivot.columns.astype(str)), y=list(pivot.index),
        colorscale="YlOrRd",
        text=[[f"${v:,.0f}" for v in row] for row in pivot.values],
        texttemplate="%{text}", showscale=True,
    ))
    heatmap_fig.update_layout(title="Avg Cost: Smoking × BMI", **LAYOUT)

    # ── Donut ──
    hr_vals = [
        filtered[filtered["high_risk_flag"] == 0]["charges"].sum(),
        filtered[filtered["high_risk_flag"] == 1]["charges"].sum(),
    ]
    donut = go.Figure(go.Pie(
        labels=["Standard Risk", "High Risk (Smoker + Obese)"],
        values=hr_vals,
        hole=0.55,
        marker_colors=[COLOR_PRIMARY, COLOR_DANGER],
        textinfo="label+percent",
        showlegend=False,
    ))
    donut.update_layout(title="Total Cost Share by Risk Level", **LAYOUT)

    return kpis, scatter, smoke_bar, age_bar, bmi_bar, reg_bar, heatmap_fig, donut


# ── Run ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Starting dashboard → http://127.0.0.1:8050")
    app.run(debug=True)
