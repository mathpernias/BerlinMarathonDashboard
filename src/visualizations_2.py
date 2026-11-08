import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import theme as T
from data import df, initial_sex_values, initial_nation_counts, time_counts, time_labels

SUBPLOT_TITLES = ("Distribution des temps d'arrivée · glissez pour sélectionner une plage",
                  "Répartition par sexe", "Top 15 nationalités")
NATION_COLOR = T.CATEGORICAL[2]


def _fmt_td(td):
    total = int(td.total_seconds())
    return f"{total // 3600}:{(total % 3600) // 60:02d}"


def update_plots(trace, points, selector, fig):
    if isinstance(fig, dict):
        fig = go.Figure(fig)
    if not points or not isinstance(points, list):
        return fig

    selected_times = sorted({time_counts.index[p["pointIndex"]] for p in points
                             if p.get("curveNumber", 0) == 0})
    if not selected_times:
        return fig

    selected_df = df[df['tps_fin_rounded'].isin(selected_times)]

    sex_counts = selected_df['sex'].value_counts()
    sex_values = [int(sex_counts.get('M', 0)), int(sex_counts.get('W', 0))]
    fig.update_traces(values=sex_values, selector=dict(type='pie'))

    nation_counts = selected_df['nation'].value_counts().head(15)
    if nation_counts.empty:
        fig.update_traces(x=["Aucune donnée"], y=[0], selector=dict(name="Top nationalités"))
    else:
        fig.update_traces(x=list(nation_counts.index), y=list(nation_counts.values),
                          selector=dict(name="Top nationalités"))

    end = selected_times[-1] + pd.Timedelta(minutes=10)
    label = (f"<b>{_fmt_td(selected_times[0])} → {_fmt_td(end)}</b>  ·  "
             f"{len(selected_df):,} coureurs".replace(",", " "))
    fig.layout.annotations = [a for a in fig.layout.annotations if a.text in SUBPLOT_TITLES]
    fig.add_annotation(xref="paper", yref="paper", x=1, y=1.0, xanchor="right", yanchor="bottom",
                       showarrow=False, text=label, font=dict(size=13, color=T.BG),
                       bgcolor=T.GOLD, borderpad=6)
    return fig


def create_dashboard():
    x_labels = [_fmt_td(td) for td in pd.to_timedelta(time_labels)]

    fig = make_subplots(
        rows=2, cols=2,
        specs=[[{"colspan": 2}, None], [{"type": "domain"}, {}]],
        subplot_titles=SUBPLOT_TITLES,
        vertical_spacing=0.16, horizontal_spacing=0.12,
        row_heights=[0.55, 0.45],
    )
    for ann in fig.layout.annotations:
        ann.font = dict(color=T.TEXT_2, size=12)

    fig.add_trace(go.Bar(
        x=x_labels, y=time_counts.values, name="",
        marker=dict(color=T.CATEGORICAL[0], line=dict(color=T.SURFACE, width=1)),
        selected=dict(marker=dict(color=T.GOLD)),
        unselected=dict(marker=dict(opacity=0.35)),
        hovertemplate='<b>%{x}</b> · %{y:,} coureurs<extra></extra>',
    ), row=1, col=1)

    fig.add_trace(go.Pie(
        labels=["Hommes", "Femmes"], values=initial_sex_values, name="Répartition par sexe",
        marker=dict(colors=[T.MEN, T.WOMEN], line=dict(color=T.SURFACE, width=3)),
        textinfo='percent+label', textposition='inside', insidetextorientation='horizontal',
        textfont=dict(color=T.TEXT, size=13),
        hole=0.62, sort=False,
        hovertemplate='%{label} : %{value:,} (%{percent})<extra></extra>',
    ), row=2, col=1)

    fig.add_trace(go.Bar(
        x=list(initial_nation_counts.index), y=list(initial_nation_counts.values),
        name="Top nationalités", marker_color=NATION_COLOR,
        hovertemplate='%{x} · %{y:,} coureurs<extra></extra>',
    ), row=2, col=2)

    fig.update_layout(
        height=860, margin=dict(t=56, b=110, l=56, r=24),
        dragmode="select", selectdirection="h", showlegend=False,
    )
    fig.update_xaxes(tickvals=x_labels[::3], tickangle=0, row=1, col=1)
    fig.update_yaxes(separatethousands=True, row=1, col=1)
    fig.update_xaxes(tickangle=-40, row=2, col=2)
    fig.update_yaxes(separatethousands=True, row=2, col=2)
    return fig
