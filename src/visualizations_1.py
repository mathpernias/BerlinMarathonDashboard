import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

import theme as T
from data import years

LEVEL_COLORS = dict(zip(["Top 10", "Pros", "Semi-pro", "Passionnés", "Amateurs"], T.CATEGORICAL))
AGES = ["20", "25", "30", "35", "40", "45", "50", "55", "60", "65", "70", "75", "80"]


def initSubplot(df_temp, df_preci):
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.08,
                        row_heights=[0.62, 0.19, 0.19],
                        subplot_titles=("Temps moyen indexé (1999 = 1)",
                                        "Température moyenne · °C", "Précipitations · mm"))
    fig.update_layout(height=680, margin=dict(l=48, r=24, t=56, b=32),
                      hovermode="x unified",
                      legend=dict(orientation="h", y=1.07, x=0))
    for ann in fig.layout.annotations:
        ann.font = dict(color=T.TEXT_2, size=12)
        ann.x = 0
        ann.xanchor = "left"

    fig.add_hline(y=1, line=dict(color=T.MUTED, width=1, dash="dot"), row=1, col=1)

    fig.add_trace(go.Scatter(x=years, y=df_temp.loc['AVG_TEMP_C'], name="Température",
                             showlegend=False, mode="lines+markers",
                             line=dict(color=T.CATEGORICAL[7], width=2),
                             marker=dict(size=5),
                             hovertemplate="%{y:.1f} °C<extra>Temp.</extra>"), row=2, col=1)
    fig.add_trace(go.Bar(x=years, y=df_preci.loc['PRECIP_mm'], name="Précipitations",
                         showlegend=False, marker_color=T.CATEGORICAL[0],
                         hovertemplate="%{y:.1f} mm<extra>Pluie</extra>"), row=3, col=1)
    fig.update_xaxes(dtick=2, row=3, col=1)
    return fig


def _indexed(df_courreur, indexage):
    result = df_courreur.applymap(lambda td: td.total_seconds() if pd.notnull(td) else None)
    return result.div(result[indexage], axis=0)


def _line(x, y, name, color):
    return go.Scatter(x=x, y=y, name=name, mode="lines",
                      line=dict(color=color, width=2, shape="spline", smoothing=0.3),
                      hovertemplate="%{y:.3f}")


def make_viz1_noSelect(df_courreur, df_temp, df_preci, indexage):
    fig = initSubplot(df_temp, df_preci)
    result = _indexed(df_courreur, indexage)
    for i, idx in enumerate(result.index):
        color = LEVEL_COLORS.get(idx) or T.SEX_COLORS.get(idx) or T.CATEGORICAL[i % 8]
        fig.add_trace(_line(result.columns, result.loc[idx], idx, color), row=1, col=1)
    return fig


def make_viz1_select(df_courreur, df_temp, df_preci, indexage, selection):
    '''Age is ordinal: colour by a single-hue ramp (blue = men / all, orange = women).'''
    fig = initSubplot(df_temp, df_preci)
    result = _indexed(df_courreur, indexage)
    selection = sorted(selection or [], key=int)
    for idx in result.index:
        if isinstance(idx, str):
            if idx in selection:
                c = T.ramp_color(T.BLUE_RAMP, AGES.index(idx), len(AGES))
                fig.add_trace(_line(result.columns, result.loc[idx], f"{idx} ans", c), row=1, col=1)
        else:
            age, sex = idx
            if age in selection and sex in ("M", "W"):
                ramp = T.BLUE_RAMP if sex == "M" else T.ORANGE_RAMP
                c = T.ramp_color(ramp, AGES.index(age), len(AGES))
                label = f"{'H' if sex == 'M' else 'F'} {age} ans"
                fig.add_trace(_line(result.columns, result.loc[idx], label, c), row=1, col=1)
    return fig
