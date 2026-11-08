from functools import lru_cache

import numpy as np
import pandas as pd
import plotly.graph_objects as go

import theme as T
import preprocess
from data import marathon_df, years
from layout_vis3 import configure_layout


def generate_circle_points(center_x, center_y, count, radius=0.3):
    if count == 1:
        return [center_x], [center_y]
    angles = np.linspace(0, 2 * np.pi, count, endpoint=False) + np.pi / 2
    return center_x + radius * np.cos(angles), center_y + radius * 0.9 * np.sin(angles)


@lru_cache(maxsize=16)
def _top10(category):
    return preprocess.get_top_10(marathon_df, selected_category_age=category)


def filtered_top10(selected_gender, selected_category):
    top = _top10(selected_category).copy()
    if selected_gender != "ALL":
        top = top[top["gender"] == selected_gender]
    top = top[top["gender"].isin(["M", "W"])]
    top["full_name"] = top["nom"].astype(str) + " " + top["prenom"].astype(str)
    # rank within (year, gender) — women are ranked among women
    top["relative_place"] = top.groupby(["year", "gender"])["place"].rank(method="first").astype(int)
    return top


def runner_profile(selected_runner, selected_category="ALL"):
    '''All Berlin finishes (any rank) of a runner picked on the chart.'''
    if not selected_runner:
        return None
    top = _top10(selected_category)
    match = top[(top["nom"].astype(str) + " " + top["prenom"].astype(str)) == selected_runner]
    if match.empty:
        return None
    nom, prenom = match.iloc[0]["nom"], match.iloc[0]["prenom"]
    runs = marathon_df[(marathon_df["nom"] == nom) & (marathon_df["prenom"] == prenom)]
    runs = runs[runs["tps_fin_p"] > 0].sort_values("year")
    if runs.empty:
        return None
    gender = runs.iloc[0]["gender"]
    best = runs.loc[runs["tps_fin_p"].idxmin()]
    return {
        "name": f"{prenom} {nom}",
        "nation": runs.iloc[0]["nation"],
        "gender": gender,
        "starts": len(runs),
        "best_time": float(best["tps_fin_p"]),
        "best_year": int(best["year"]),
        "runs": [(int(r.year), float(r.tps_fin_p)) for r in runs.itertuples()],
    }


def generate_marathon_chart(selected_gender="ALL", selected_runner=None, selected_category="ALL"):
    fig = go.Figure()
    filtered_df = filtered_top10(selected_gender, selected_category)
    if filtered_df.empty:
        fig.add_annotation(text="Aucune donnée pour ce genre ou cette catégorie d'âge",
                           showarrow=False, x=0.5, y=0.5, xref="paper", yref="paper")
        fig.update_layout(xaxis=dict(visible=False), yaxis=dict(visible=False))
        return fig

    nations_sorted = filtered_df["nation"].value_counts().index.tolist()
    # keep "Other" at the bottom
    if "Other" in nations_sorted:
        nations_sorted.remove("Other")
        nations_sorted.append("Other")
    nations_sorted = nations_sorted[::-1]  # most frequent on top

    pts = {g: {"x": [], "y": [], "text": [], "name": [], "op": [], "size": [], "line": []}
           for g in ("M", "W")}
    for (year, nation), group in filtered_df.groupby(["year", "nation"]):
        group = group.sort_values(["gender", "relative_place"])
        xs, ys = generate_circle_points(year, nations_sorted.index(nation), len(group))
        for k, row in enumerate(group.itertuples()):
            p = pts[row.gender]
            is_sel = selected_runner == row.full_name
            p["x"].append(xs[k])
            p["y"].append(ys[k])
            p["name"].append(row.full_name)
            p["text"].append(f"<b>{row.prenom} {row.nom}</b><br>{nation} · {year}<br>"
                             f"{'Homme' if row.gender == 'M' else 'Femme'} · {row.relative_place}ᵉ"
                             f"<br>{pd.to_timedelta(row.tps_fin_p, unit='s')}".replace("0 days ", ""))
            p["op"].append(1.0 if is_sel else (0.12 if selected_runner else 0.85))
            p["size"].append(15 if is_sel else 9)
            p["line"].append(T.GOLD if is_sel else T.SURFACE)

    for g, label, color in (("M", "Hommes", T.MEN), ("W", "Femmes", T.WOMEN)):
        p = pts[g]
        if not p["x"]:
            continue
        fig.add_trace(go.Scatter(
            x=p["x"], y=p["y"], mode="markers", name=label,
            marker=dict(color=color, size=p["size"], opacity=p["op"],
                        line=dict(color=p["line"], width=2)),
            text=p["text"], customdata=p["name"],
            hovertemplate="%{text}<extra></extra>",
        ))

    # Cell grid
    shapes = []
    for i in years:
        shapes.append(dict(type="line", x0=i - 0.5, x1=i - 0.5, y0=-0.5, y1=len(nations_sorted) - 0.5,
                           line=dict(color=T.GRID, width=1), xref="x", yref="y", layer="below"))
    for i in range(len(nations_sorted) + 1):
        shapes.append(dict(type="line", x0=years[0] - 0.5, x1=years[-1] + 0.5, y0=i - 0.5, y1=i - 0.5,
                           line=dict(color=T.GRID, width=1), xref="x", yref="y", layer="below"))
    fig.update_layout(shapes=shapes)

    fig.update_xaxes(showgrid=False, zeroline=False, tickvals=years,
                     ticktext=[f"’{str(y)[2:]}" for y in years],
                     range=[years[0] - 0.6, years[-1] + 2.6])
    fig.update_yaxes(showgrid=False, zeroline=False, tickvals=list(range(len(nations_sorted))),
                     ticktext=nations_sorted, tickfont=dict(color=T.TEXT_2, size=12))
    fig.update_layout(
        height=max(420, 64 * len(nations_sorted) + 120),
        margin=dict(l=110, r=16, t=40, b=40),
        clickmode="event", hovermode="closest",
        legend=dict(y=1.02, x=0),
    )
    return configure_layout(fig, nations_sorted, selected_category, selected_gender)


def top10_average_text(selected_gender, selected_category):
    df = filtered_top10(selected_gender, selected_category)
    if df.empty:
        return {}
    means = df.groupby("gender")["tps_fin_p"].mean()
    return {g: float(v) for g, v in means.items()}
