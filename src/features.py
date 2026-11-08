'''
    New dashboard features:
      - Palmarès : winning times per edition (men / women) with world records
      - Explorateur d'édition : one edition at a glance
      - Ma course : place a finish time among 780k Berlin finishers
'''
import numpy as np
import pandas as pd
import plotly.graph_objects as go

import theme as T
from data import df

MARATHON_KM = 42.195

_valid = df.loc[df["tps_fin_p"] > 0, ["year", "sex", "nation", "nom", "prenom",
                                      "class_age", "tps_fin_p"]].copy()
_valid = _valid[_valid["sex"].isin(["M", "W"])]
_valid["class_age"] = _valid["class_age"].astype(str)

YEARS = sorted(int(y) for y in _valid["year"].unique())
AGE_CLASSES = ["20", "25", "30", "35", "40", "45", "50", "55", "60", "65", "70", "75", "80"]

# World records set in Berlin (year -> sex)
WORLD_RECORDS = {("M", 2003), ("M", 2007), ("M", 2008), ("M", 2011), ("M", 2013),
                 ("M", 2014), ("M", 2018), ("M", 2022), ("W", 2001), ("W", 2023)}

# ---------------------------------------------------------------- formatting

def fmt_time(seconds, with_seconds=True):
    if seconds is None or pd.isna(seconds):
        return "—"
    seconds = int(round(seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if with_seconds else f"{h}:{m:02d}"


def fmt_pace(seconds_total):
    per_km = seconds_total / MARATHON_KM
    m, s = divmod(int(round(per_km)), 60)
    return f"{m}:{s:02d}"


def fmt_int(n):
    return f"{int(n):,}".replace(",", " ")


def parse_time(text):
    '''"3:45", "03:45:30", "3h45" -> seconds (or None).'''
    if not text:
        return None
    cleaned = str(text).strip().lower().replace("h", ":").replace("'", ":").replace(" ", "")
    parts = [p for p in cleaned.split(":") if p != ""]
    try:
        nums = [int(p) for p in parts]
    except ValueError:
        return None
    if len(nums) == 2:
        h, m, s = nums[0], nums[1], 0
    elif len(nums) == 3:
        h, m, s = nums
    else:
        return None
    if not (0 <= m < 60 and 0 <= s < 60) or h > 12:
        return None
    total = h * 3600 + m * 60 + s
    return total if total >= 2 * 3600 else None


def _to_dt(seconds):
    '''Seconds -> datetime on 1970-01-01 so Plotly can draw H:MM axes.'''
    return pd.to_datetime(np.asarray(seconds, dtype=float), unit="s")

# ---------------------------------------------------------------- aggregates

_g = _valid.groupby("year")
SUMMARY = pd.DataFrame({
    "finishers": _g.size(),
    "women_share": _g["sex"].apply(lambda s: (s == "W").mean()),
    "median": _g["tps_fin_p"].median(),
    "nations": _g["nation"].nunique(),
})


def _winners(sex):
    sub = _valid[_valid["sex"] == sex]
    rows = sub.loc[sub.groupby("year")["tps_fin_p"].idxmin()].set_index("year")
    return rows


WINNERS = {"M": _winners("M"), "W": _winners("W")}

GLOBAL = {
    "editions": len(YEARS),
    "first": YEARS[0],
    "last": YEARS[-1],
    "finishers": len(_valid),
    "nations": _valid["nation"].nunique(),
    "median": _valid["tps_fin_p"].median(),
    "best_m": WINNERS["M"]["tps_fin_p"].min(),
    "best_w": WINNERS["W"]["tps_fin_p"].min(),
    "growth": SUMMARY["finishers"].iloc[-1] / SUMMARY["finishers"].iloc[0] - 1,
}


def winner_info(sex, year):
    row = WINNERS[sex].loc[year]
    return {
        "name": f"{row['prenom']} {row['nom']}".strip(),
        "nation": row["nation"],
        "time": fmt_time(row["tps_fin_p"]),
        "pace": fmt_pace(row["tps_fin_p"]),
        "wr": (sex, year) in WORLD_RECORDS,
    }

# ---------------------------------------------------------------- figures

def records_figure():
    fig = go.Figure()
    for sex, label, color in (("M", "Hommes", T.MEN), ("W", "Femmes", T.WOMEN)):
        w = WINNERS[sex].reindex(range(YEARS[0], YEARS[-1] + 1))  # 2020: no race -> gap
        names = (w["prenom"].fillna("").astype(str) + " " + w["nom"].fillna("").astype(str)).values
        custom = np.stack([names, w["nation"].values,
                           [fmt_time(s) for s in w["tps_fin_p"]],
                           [fmt_pace(s) if pd.notna(s) else "" for s in w["tps_fin_p"]]], axis=-1)
        fig.add_trace(go.Scatter(
            x=w.index, y=_to_dt(w["tps_fin_p"]), name=label, mode="lines+markers",
            connectgaps=False, showlegend=False,
            line=dict(color=color, width=2, shape="spline", smoothing=0.4),
            marker=dict(size=8, color=color, line=dict(color=T.SURFACE, width=2)),
            customdata=custom,
            hovertemplate=(f"<b>%{{x}} · {label}</b><br>%{{customdata[0]}} "
                           "(%{customdata[1]})<br>%{customdata[2]} · %{customdata[3]} /km<extra></extra>"),
        ))
        # world records ring
        wr_years = [y for (s, y) in WORLD_RECORDS if s == sex and y in w.index]
        fig.add_trace(go.Scatter(
            x=wr_years, y=_to_dt(w.loc[wr_years, "tps_fin_p"]), mode="markers",
            marker=dict(size=17, color="rgba(0,0,0,0)", line=dict(color=T.GOLD, width=2)),
            showlegend=False, hoverinfo="skip",
        ))
        # direct label at the line end
        last = w["tps_fin_p"].last_valid_index()
        fig.add_annotation(x=last, y=_to_dt([w.loc[last, "tps_fin_p"]])[0], text=f"<b>{label}</b>",
                           showarrow=False, xanchor="left", xshift=12,
                           font=dict(color=T.TEXT, size=12))

    fig.update_layout(
        height=430, margin=dict(l=56, r=80, t=44, b=36),
        hovermode="closest",
        yaxis=dict(tickformat="%-H:%M", title=None),
        xaxis=dict(dtick=2, title=None, range=[YEARS[0] - 0.6, YEARS[-1] + 0.6]),
    )
    return fig


def year_distribution_figure(year):
    sub = _valid[_valid["year"] == year]
    bins = np.arange(2 * 3600, 7 * 3600 + 1, 300)
    centers = (bins[:-1] + bins[1:]) / 2
    fig = go.Figure()
    for sex, label, color in (("M", "Hommes", T.MEN), ("W", "Femmes", T.WOMEN)):
        counts, _ = np.histogram(sub.loc[sub["sex"] == sex, "tps_fin_p"], bins=bins)
        labels = [f"{fmt_time(a, False)}–{fmt_time(b, False)}" for a, b in zip(bins[:-1], bins[1:])]
        fig.add_trace(go.Bar(
            x=_to_dt(centers), y=counts, name=label, marker_color=color,
            marker_line=dict(color=T.SURFACE, width=1),
            customdata=labels,
            hovertemplate=f"<b>%{{customdata}}</b><br>{label} : %{{y:,}}<extra></extra>",
        ))
    med = sub["tps_fin_p"].median()
    m = _to_dt([med])[0]
    fig.add_shape(type="line", x0=m, x1=m, y0=0, y1=1, yref="paper",
                  line=dict(color=T.TEXT_2, width=1, dash="dot"))
    fig.add_annotation(x=_to_dt([med])[0], y=1, yref="paper", text=f"médiane {fmt_time(med, False)}",
                       showarrow=False, xanchor="left", xshift=6, font=dict(color=T.TEXT_2, size=11))
    fig.update_layout(
        barmode="stack", height=330, bargap=0.06, showlegend=False,
        margin=dict(l=48, r=16, t=36, b=36),
        xaxis=dict(tickformat="%-H:%M", title=None, range=_to_dt([2 * 3600, 7 * 3600])),
        yaxis=dict(title=None, separatethousands=True),
        hovermode="x unified",
    )
    return fig


def growth_figure(highlight_year):
    s = SUMMARY
    colors = [T.GOLD if y == highlight_year else "#3a3f4b" for y in s.index]
    fig = go.Figure(go.Bar(
        x=s.index, y=s["finishers"], marker_color=colors,
        customdata=np.stack([s["women_share"] * 100, [fmt_time(m, False) for m in s["median"]]], axis=-1),
        hovertemplate="<b>%{x}</b><br>%{y:,} finishers<br>%{customdata[0]:.1f} % de femmes"
                      "<br>médiane %{customdata[1]}<extra></extra>",
    ))
    fig.update_layout(height=140, margin=dict(l=8, r=8, t=4, b=24), bargap=0.25,
                      yaxis=dict(visible=False), xaxis=dict(dtick=4, title=None, showgrid=False))
    return fig

# ---------------------------------------------------------------- Ma course

def _population(sex, year, age):
    sub = _valid
    if sex in ("M", "W"):
        sub = sub[sub["sex"] == sex]
    if year not in (None, "ALL"):
        sub = sub[sub["year"] == int(year)]
    if age not in (None, "ALL"):
        sub = sub[sub["class_age"] == str(age)]
    return sub


def my_race(seconds, sex="ALL", year="ALL", age="ALL"):
    pop = _population(sex, year, age)
    times = np.sort(pop["tps_fin_p"].to_numpy())
    n = len(times)
    if n == 0:
        return None, empty_figure("Aucun coureur pour ce filtre")
    faster = int(np.searchsorted(times, seconds, side="left"))
    rank = faster + 1
    beat = (n - np.searchsorted(times, seconds, side="right")) / n * 100

    best = times[0]
    stats = {
        "rank": rank, "n": n, "beat": beat, "top": 100 - beat,
        "pace": fmt_pace(seconds), "speed": MARATHON_KM / (seconds / 3600),
        "gap": fmt_time(seconds - best), "best": fmt_time(best),
        "splits": [(label, fmt_time(seconds * km / MARATHON_KM))
                   for label, km in (("5 km", 5), ("10 km", 10), ("Semi", 21.0975),
                                     ("30 km", 30), ("40 km", 40))],
        "median": fmt_time(np.median(times)),
    }

    bins = np.arange(2 * 3600, 7 * 3600 + 1, 120)
    counts, _ = np.histogram(times, bins=bins)
    centers = (bins[:-1] + bins[1:]) / 2
    is_faster = centers < seconds
    fig = go.Figure()
    for mask, color, label in ((is_faster, T.CATEGORICAL[0], "Plus rapides que vous"),
                               (~is_faster, "#3a3f4b", "Plus lents que vous")):
        fig.add_trace(go.Bar(
            x=_to_dt(centers[mask]), y=counts[mask], marker_color=color, name=label,
            hovertemplate="<b>%{x|%-H:%M}</b> · %{y:,} coureurs<extra></extra>",
        ))
    you = _to_dt([seconds])[0]
    fig.add_shape(type="line", x0=you, x1=you, y0=0, y1=1, yref="paper",
                  line=dict(color=T.GOLD, width=2))
    fig.add_annotation(x=you, y=1, yref="paper", yanchor="bottom",
                       text=f"<b>Vous · {fmt_time(seconds)}</b>", showarrow=False,
                       font=dict(color=T.BG, size=12), bgcolor=T.GOLD, borderpad=5)
    fig.update_layout(
        barmode="overlay", bargap=0.04, height=320, showlegend=True,
        margin=dict(l=48, r=16, t=48, b=36),
        legend=dict(y=1.14, x=1, xanchor="right"),
        xaxis=dict(tickformat="%-H:%M", title=None, range=_to_dt([2 * 3600, 7 * 3600])),
        yaxis=dict(title=None, separatethousands=True),
    )
    return stats, fig


def empty_figure(message):
    fig = go.Figure()
    fig.add_annotation(text=message, showarrow=False, x=0.5, y=0.5, xref="paper", yref="paper",
                       font=dict(color=T.MUTED, size=14))
    fig.update_layout(xaxis=dict(visible=False), yaxis=dict(visible=False), height=320)
    return fig
