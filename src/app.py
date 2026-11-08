# -*- coding: utf-8 -*-
'''
    Berlin Marathon Dashboard — application Dash.
    Course: INF8808
'''
import sys
import os
sys.path.append(os.path.dirname(__file__))

import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import pandas as pd

import theme as T
import preprocess
from data import df
from visualizations_1 import make_viz1_noSelect, make_viz1_select, AGES
from visualizations_2 import create_dashboard, update_plots
from visualizations_3 import generate_marathon_chart, runner_profile, top10_average_text
import features as F

FONTS = ("https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1"
         "&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap")

app = dash.Dash(__name__, external_stylesheets=[FONTS], title="Berlin Marathon · 1999–2023",
                meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}])
server = app.server

df_temp, df_preci = preprocess.preprocess_meteo(
    pd.read_csv('./src/assets/data/Berlin_Marathon_weather_data_since_1974.csv'))
dict_All_viz1 = preprocess.process_data_courreur_viz1(df)
TEMPS = {int(k): float(v) for k, v in df_temp.loc['AVG_TEMP_C'].items()}

G = F.GLOBAL
CFG = T.GRAPH_CONFIG


# ------------------------------------------------------------------ components

def kpi(value, label, cls=""):
    return html.Div([html.Div(value, className="kpi-value"), html.Div(label, className="kpi-label")],
                    className=f"kpi {cls}")


def card(*children, cls=""):
    return html.Div(list(children), className=f"card {cls}")


def card_head(eyebrow, title, extra=None):
    return html.Div([
        html.Div([html.Div(eyebrow, className="eyebrow"), html.H3(title)]),
        extra if extra is not None else html.Span(),
    ], className="card-head")


def story(eyebrow, title, paragraphs, insights=None, extra=None):
    body = [html.Div(eyebrow, className="eyebrow"), html.H2(title)]
    body += [html.P(p) for p in paragraphs]
    if insights:
        body.append(html.Div("À retenir", className="eyebrow eyebrow--muted"))
        body.append(html.Ul([html.Li(i) for i in insights], className="insights"))
    if extra is not None:
        body.append(extra)
    return html.Aside(body, className="story")


def segmented(id_, options, value):
    return dcc.RadioItems(id=id_, options=options, value=value, className="segmented",
                          inputClassName="segmented-input", labelClassName="segmented-label")


def legend_dot(color, label):
    return html.Span([html.I(style={"background": color}), label], className="legend-dot")


def fmt_pct(x, digits=1):
    return f"{x:.{digits}f}".replace(".", ",") + " %"


AGE_OPTIONS = [{"label": "Tous âges", "value": "ALL"}] + [{"label": f"{a} ans", "value": a} for a in AGES]
SEX_OPTIONS = [{"label": "Tous", "value": "ALL"}, {"label": "Hommes", "value": "M"},
               {"label": "Femmes", "value": "W"}]

LEGENDS = [
    ("Eliud Kipchoge", "Kenya", "Cinq victoires (2015, 2017, 2018, 2022, 2023) et deux records du monde : "
     "2:01:39 en 2018 puis 2:01:09 en 2022."),
    ("Tigst Assefa", "Éthiopie", "En 2023 elle pulvérise le record du monde féminin en 2:11:53 — plus de "
     "deux minutes de mieux que l'ancienne marque."),
    ("Haile Gebrselassie", "Éthiopie", "Quatre victoires consécutives (2006–2009) et deux records du monde : "
     "2:04:26 en 2007, 2:03:59 en 2008."),
    ("Naoko Takahashi", "Japon", "En 2001, première femme de l'histoire sous les 2h20 : 2:19:46."),
]


def wr_timeline():
    items = []
    for sex, year in sorted(F.WORLD_RECORDS, key=lambda t: t[1], reverse=True):
        w = F.winner_info(sex, year)
        items.append(html.Li([
            html.Span(str(year), className="tl-year"),
            html.Span([html.I(style={"background": T.SEX_COLORS[sex]}), w["name"]], className="tl-name"),
            html.Span(w["time"], className="tl-time"),
        ]))
    return html.Ol(items, className="timeline")


# ------------------------------------------------------------------ tabs

tab_records = html.Div([
    html.Div([
        card(
            card_head("Palmarès · 1999 → 2023", "Le temps du vainqueur, édition après édition",
                      html.Div([legend_dot(T.MEN, "Hommes"), legend_dot(T.WOMEN, "Femmes"),
                                html.Span([html.I(className="ring"), "Record du monde"],
                                          className="legend-dot")], className="legend")),
            dcc.Graph(figure=F.records_figure(), config=CFG),
            cls="card--wide"),
        card(
            card_head("Le parcours le plus rapide du monde", "Records du monde battus à Berlin"),
            wr_timeline(),
            cls="card--side"),
    ], className="grid grid--2-1"),
    html.Div([
        html.Div("Légendes", className="eyebrow"),
        html.Div([
            html.Details([
                html.Summary([html.Span(name, className="legend-name"),
                              html.Span(country, className="legend-country")]),
                html.P(text),
            ], className="legend-card") for name, country, text in LEGENDS
        ], className="legends-grid"),
    ], className="legends"),
], className="tab-body")

tab_my_race = html.Div([
    card(
        card_head("Simulateur", "Et vous, où auriez-vous fini ?"),
        html.Div([
            html.Div([
                html.Label("Votre temps", htmlFor="race-time"),
                dcc.Input(id="race-time", type="text", value="3:45:00", placeholder="h:mm:ss",
                          className="time-input", debounce=False, autoComplete="off"),
                html.Div(id="race-time-hint", className="hint"),
            ], className="field field--time"),
            html.Div([html.Label("Comparé à"), segmented("race-sex", SEX_OPTIONS, "ALL")], className="field"),
            html.Div([html.Label("Édition"),
                      dcc.Dropdown(id="race-year", clearable=False, value="ALL", className="dd",
                                   options=[{"label": "Toutes", "value": "ALL"}] +
                                   [{"label": str(y), "value": y} for y in F.YEARS][::-1])],
                     className="field"),
            html.Div([html.Label("Catégorie"),
                      dcc.Dropdown(id="race-age", clearable=False, value="ALL", className="dd",
                                   options=AGE_OPTIONS)], className="field"),
        ], className="controls controls--race"),
        html.Div(id="race-result"),
        dcc.Graph(id="race-graph", config=CFG),
        cls="card--race"),
], className="tab-body")

tab_edition = html.Div([
    card(
        card_head("Explorateur", "Une édition à la loupe",
                  html.Div(id="edition-badge", className="badge")),
        html.Div([
            dcc.Graph(id="growth-graph", config={"displayModeBar": False}),
            html.Div("Cliquez sur une barre ou utilisez le curseur", className="hint hint--center"),
            dcc.Slider(id="year-slider", min=F.YEARS[0], max=F.YEARS[-1], step=None,
                       value=F.YEARS[-1], marks={y: (str(y) if y in (F.YEARS[0], F.YEARS[-1]) or y % 4 == 3 else "")
                                                 for y in F.YEARS},
                       className="year-slider"),
        ], className="edition-nav"),
        html.Div(id="edition-kpis", className="kpi-row kpi-row--4"),
        html.Div([
            html.Div(id="edition-winners", className="winners"),
            html.Div([
                html.Div([html.Div("Distribution des arrivées · tranches de 5 min", className="eyebrow"),
                          html.Div([legend_dot(T.MEN, "Hommes"), legend_dot(T.WOMEN, "Femmes")],
                                   className="legend")], className="mini-head"),
                dcc.Graph(id="edition-graph", config=CFG),
            ], className="edition-dist"),
        ], className="grid grid--1-2"),
    ),
], className="tab-body")

tab_weather = html.Div([
    html.Div([
        story("Temps & météo", "La chaleur ralentit tout le monde… presque.",
              ["Chaque courbe suit le temps moyen d'un groupe de coureurs, rapporté à sa valeur de 1999. "
               "Au-dessus de 1 : plus lent qu'en 1999. En dessous : plus rapide.",
               "Les groupes de niveau découpent chaque édition en quartiles : Pros (25 % les plus rapides), "
               "Semi-pro, Passionnés, Amateurs — et le Top 10."],
              ["La croissance du peloton tire les temps des amateurs vers le haut.",
               "2006 et 2021, éditions chaudes, montrent un pic net — atténué chez l'élite.",
               "L'effet de la température se retrouve quels que soient le sexe et l'âge."]),
        card(
            html.Div([
                html.Div([html.Label("Regrouper par"),
                          segmented("radio-vis1", [
                              {"label": "Niveau", "value": "Par niveaux"},
                              {"label": "Sexe", "value": "Par sex"},
                              {"label": "Âge", "value": "Par age"},
                              {"label": "Âge & sexe", "value": "Par sex-age"}], "Par niveaux")],
                         className="field"),
                html.Div([html.Label("Catégories d'âge"),
                          dcc.Checklist(id="age-checklist", options=[{"label": a, "value": a} for a in AGES],
                                        value=["30", "40", "50"], className="chips",
                                        inputClassName="chip-input", labelClassName="chip")],
                         id="age-field", className="field", style={"display": "none"}),
            ], className="controls"),
            dcc.Graph(id='vis1', config=CFG,
                      figure=make_viz1_noSelect(dict_All_viz1["Par niveaux"], df_temp, df_preci, 1999)),
            cls="card--wide"),
    ], className="grid grid--story"),
], className="tab-body")

tab_nations = html.Div([
    html.Div([
        story("Sexe & nationalités", "Qui court à quelle vitesse ?",
              ["Glissez horizontalement sur l'histogramme pour isoler une plage de temps d'arrivée : "
               "le donut et le classement des nationalités se recalculent pour cette tranche."],
              ["Les meilleurs temps sont dominés par les coureurs d'Afrique de l'Est.",
               "La part des femmes grimpe à mesure qu'on s'éloigne des temps élite.",
               "L'Allemagne domine le volume, quel que soit le niveau."]),
        card(dcc.Graph(id="vis2", figure=create_dashboard(), config=CFG), cls="card--wide"),
    ], className="grid grid--story"),
], className="tab-body")

tab_top10 = html.Div([
    html.Div([
        story("Top 10 par nationalité", "Kenya, Éthiopie… et l'Allemagne chez les vétérans.",
              ["Chaque point est un coureur du Top 10 d'une édition, placé dans la case de sa nation. "
               "Cliquez sur un point pour suivre ce coureur à travers les années."],
              ["Le Kenya écrase le Top 10 depuis 25 ans.",
               "L'Éthiopie perce, surtout chez les femmes.",
               "Dans les catégories d'âge élevées, les Allemands jouent à domicile."],
              extra=html.Div(id="runner-card", className="runner-card")),
        card(
            html.Div([
                html.Div([html.Label("Genre"), segmented("gender-dropdown", SEX_OPTIONS, "ALL")],
                         className="field"),
                html.Div([html.Label("Catégorie d'âge"),
                          dcc.Dropdown(id="category-dropdown", options=AGE_OPTIONS, value="ALL",
                                       clearable=False, className="dd")], className="field field--narrow"),
                html.Button("Désélectionner", id="deselect-button", n_clicks=0, className="btn-ghost"),
            ], className="controls"),
            dcc.Loading(dcc.Graph(id="matrix-chart", config=CFG,
                                  figure=generate_marathon_chart("ALL", None, "ALL")),
                        color=T.GOLD, type="dot"),
            cls="card--wide"),
    ], className="grid grid--story"),
], className="tab-body")


def tab(label, children, value):
    return dcc.Tab(label=label, value=value, children=children, className="tab",
                   selected_className="tab--active")


# ------------------------------------------------------------------ layout

app.layout = html.Div([
    html.Header([
        html.Div([
            html.Div([html.Span(className="pulse"), "BMW Berlin-Marathon · ", html.B(f"{G['first']}–{G['last']}")],
                     className="kicker"),
            html.H1(["Berlin, ", html.Em("42,195 km"), html.Br(), "d'histoire."]),
            html.P(f"{G['editions']} éditions, {F.fmt_int(G['finishers'])} finishers et "
                   f"{G['nations']} nations : records du monde, météo, nationalités, et votre propre course "
                   "replacée dans le peloton.", className="lede"),
        ], className="hero-copy"),
        html.Div([
            kpi(F.fmt_int(G["finishers"]), "finishers"),
            kpi(str(G["editions"]), "éditions"),
            kpi(str(G["nations"]), "nations"),
            kpi(F.fmt_time(G["best_m"]), "record hommes", "kpi--men"),
            kpi(F.fmt_time(G["best_w"]), "record femmes", "kpi--women"),
            kpi(F.fmt_time(G["median"], False), "temps médian"),
        ], className="kpi-grid"),
        html.Div(html.Div(className="route-runner"), className="route"),
    ], className="hero"),

    dcc.Tabs(id="tabs", value="records", className="tabs", parent_className="tabs-parent",
             content_className="tabs-content", children=[
                 tab("Palmarès", tab_records, "records"),
                 tab("Ma course ✦", tab_my_race, "race"),
                 tab("Une édition", tab_edition, "edition"),
                 tab("Temps & météo", tab_weather, "weather"),
                 tab("Sexe & nations", tab_nations, "nations"),
                 tab("Top 10", tab_top10, "top10"),
             ]),

    html.Footer([
        html.Span("Données : bmw-berlin-marathon.com · météo DWD"),
        html.Span("INF8808 · Dash & Plotly"),
    ], className="footer"),
], className="app")


# ------------------------------------------------------------------ callbacks

@app.callback(Output('vis1', "figure"), Output("age-field", "style"),
              Input('radio-vis1', "value"), Input("age-checklist", "value"))
def update_vis1(category, selection):
    show = {"display": "block"} if category in ("Par age", "Par sex-age") else {"display": "none"}
    data = dict_All_viz1.get(category, dict_All_viz1["Par niveaux"])
    if category in ("Par age", "Par sex-age"):
        return make_viz1_select(data, df_temp, df_preci, 1999, selection), show
    return make_viz1_noSelect(data, df_temp, df_preci, 1999), show


@app.callback(Output("vis2", "figure"), Input("vis2", "selectedData"), State("vis2", "figure"),
              prevent_initial_call=True)
def update_vis2_from_selection(selected_data, fig):
    if selected_data and selected_data.get("points"):
        return update_plots(None, selected_data["points"], None, fig)
    return dash.no_update


@app.callback(Output("matrix-chart", "figure"), Output("runner-card", "children"),
              Input("gender-dropdown", "value"), Input("category-dropdown", "value"),
              Input("matrix-chart", "clickData"))
def update_chart(selected_gender, selected_category, click_data):
    selected_runner = None
    if click_data and click_data.get("points"):
        selected_runner = click_data["points"][0].get("customdata")
    fig = generate_marathon_chart(selected_gender, selected_runner, selected_category)

    profile = runner_profile(selected_runner, selected_category)
    if profile:
        color = T.SEX_COLORS[profile["gender"]]
        best = max(1, min(t for _, t in profile["runs"]))
        card_children = [
            html.Div("Coureur sélectionné", className="eyebrow"),
            html.Div([html.I(style={"background": color}), profile["name"]], className="runner-name"),
            html.Div(f"{profile['nation']} · {profile['starts']} participation"
                     f"{'s' if profile['starts'] > 1 else ''} à Berlin", className="runner-meta"),
            html.Div([html.Span("Meilleur temps"), html.B(F.fmt_time(profile["best_time"])),
                      html.Span(f"en {profile['best_year']}")], className="runner-best"),
            html.Ul([html.Li([html.Span(str(y)), html.Span(className="bar",
                                                           style={"width": f"{min(100, best / t * 100):.0f}%",
                                                                  "background": color}),
                              html.B(F.fmt_time(t))]) for y, t in profile["runs"]], className="runner-runs"),
        ]
    else:
        avgs = top10_average_text(selected_gender, selected_category)
        card_children = [
            html.Div("Temps moyen du Top 10", className="eyebrow"),
            html.Div([html.Div([html.I(style={"background": T.SEX_COLORS[g]}),
                                "Hommes" if g == "M" else "Femmes", html.B(F.fmt_time(t))],
                               className="avg-row") for g, t in sorted(avgs.items())]),
            html.P("Cliquez sur un point pour afficher le parcours d'un coureur.", className="hint"),
        ]
    return fig, card_children


@app.callback(Output("matrix-chart", "clickData"), Input("deselect-button", "n_clicks"),
              prevent_initial_call=True)
def deselect_runner(_):
    return None


@app.callback(Output("year-slider", "value"), Input("growth-graph", "clickData"), prevent_initial_call=True)
def pick_year(click):
    if click and click.get("points"):
        return int(click["points"][0]["x"])
    return dash.no_update


@app.callback(Output("growth-graph", "figure"), Output("edition-kpis", "children"),
              Output("edition-winners", "children"), Output("edition-graph", "figure"),
              Output("edition-badge", "children"), Input("year-slider", "value"))
def update_edition(year):
    s = F.SUMMARY.loc[year]
    prev = F.SUMMARY.index[F.SUMMARY.index.get_loc(year) - 1] if year != F.YEARS[0] else None
    delta = ""
    if prev is not None:
        d = s["finishers"] / F.SUMMARY.loc[prev, "finishers"] - 1
        delta = f"{'+' if d >= 0 else '−'}{fmt_pct(abs(d) * 100, 0)} vs {prev}"
    temp = TEMPS.get(year)
    kpis = [
        kpi(F.fmt_int(s["finishers"]), html.Span(["finishers", html.Small(delta)])),
        kpi(fmt_pct(s["women_share"] * 100), "de femmes"),
        kpi(F.fmt_time(s["median"], False), "temps médian"),
        kpi(f"{temp:.1f} °C".replace(".", ",") if temp is not None else "—", "température moyenne"),
    ]
    winners = []
    for sex, label in (("M", "Vainqueur"), ("W", "Vainqueure")):
        w = F.winner_info(sex, year)
        winners.append(html.Div([
            html.Div([html.Span(label, className="eyebrow"),
                      html.Span("Record du monde", className="wr-tag") if w["wr"] else None],
                     className="winner-top"),
            html.Div(w["name"], className="winner-name"),
            html.Div(w["nation"], className="winner-nation"),
            html.Div([html.B(w["time"]), html.Span(f"{w['pace']} /km")], className="winner-time"),
        ], className=f"winner winner--{sex.lower()}"))
    return (F.growth_figure(year), kpis, winners, F.year_distribution_figure(year),
            f"Édition {year}")


@app.callback(Output("race-result", "children"), Output("race-graph", "figure"),
              Output("race-time-hint", "children"),
              Input("race-time", "value"), Input("race-sex", "value"),
              Input("race-year", "value"), Input("race-age", "value"))
def update_race(text, sex, year, age):
    seconds = F.parse_time(text)
    if seconds is None:
        return (dash.no_update, dash.no_update,
                "Format attendu : 3:45 ou 3:45:30 (au-delà de 2h)")
    stats, fig = F.my_race(seconds, sex, year, age)
    if stats is None:
        return html.Div("Aucun coureur pour cette combinaison de filtres.", className="hint"), fig, ""
    top = stats["top"]
    verdict = ("Élite mondiale" if top < 0.1 else "Exceptionnel" if top < 2 else "Très rapide" if top < 10
               else "Solide" if top < 35 else "Dans le peloton" if top < 70 else "Finisher, et c'est déjà énorme")
    result = html.Div([
        html.Div([
            html.Div("Votre classement", className="eyebrow"),
            html.Div([html.Span("#", className="hash"), F.fmt_int(stats["rank"])], className="big-rank"),
            html.Div(f"sur {F.fmt_int(stats['n'])} coureurs", className="big-sub"),
            html.Div([html.Span(verdict, className="verdict"),
                      html.Span(f"Top {fmt_pct(max(top, 0.01), 1 if top >= 1 else 2)}", className="top-pill")],
                     className="verdict-row"),
            html.Div(html.Div(className="meter-fill", style={"width": f"{stats['beat']:.1f}%"}),
                     className="meter"),
            html.Div(f"Plus rapide que {fmt_pct(stats['beat'])} des coureurs", className="meter-label"),
        ], className="race-hero"),
        html.Div([
            kpi(stats["pace"], "allure / km"),
            kpi(f"{stats['speed']:.2f}".replace(".", ",") + " km/h", "vitesse moyenne"),
            kpi(f"+{stats['gap']}", f"derrière le meilleur ({stats['best']})"),
            kpi(stats["median"], "temps médian du groupe"),
        ], className="kpi-row kpi-row--4 kpi-row--compact"),
        html.Div([html.Div("Passages à allure constante", className="eyebrow")] + [
            html.Div([html.Span(lbl), html.B(t)], className="split") for lbl, t in stats["splits"]
        ] + [html.Div([html.Span("Arrivée"), html.B(F.fmt_time(seconds))], className="split split--finish")],
            className="splits"),
    ], className="race-grid")
    return result, fig, ""


if __name__ == "__main__":
    app.run_server(debug=False, port=8050)
