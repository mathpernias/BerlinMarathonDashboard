'''
    Design tokens + Plotly template "berlin" (dark editorial theme).
    Import this module before building any figure.
'''
import plotly.graph_objects as go
import plotly.io as pio

# Surfaces & ink
BG = "#0b0c0f"
SURFACE = "#14161b"
SURFACE_2 = "#1b1e25"
LINE = "#262a33"
GRID = "#22262e"
TEXT = "#f0efec"
TEXT_2 = "#c3c2b7"
MUTED = "#8b8a84"

# UI accent (not a data colour)
GOLD = "#f2c14e"

# Validated categorical palette (dark steps), fixed order
CATEGORICAL = ["#3987e5", "#d95926", "#199e70", "#c98500",
               "#d55181", "#008300", "#9085e9", "#e66767"]
MEN = CATEGORICAL[0]
WOMEN = CATEGORICAL[1]
SEX_COLORS = {"M": MEN, "W": WOMEN, "Homme": MEN, "Femme": WOMEN}

# Ordinal ramps (dark mode: stop before the steps that vanish on the surface)
BLUE_RAMP = ["#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7",
             "#3987e5", "#2a78d6", "#256abf", "#1c5cab", "#184f95"]
ORANGE_RAMP = ["#fbd9c8", "#f8c6ae", "#f5b393", "#f19f78", "#ec8b5e", "#e57845",
               "#d95926", "#c24e20", "#a9441c", "#913a18", "#7a3114"]

FONT_BODY = "Inter, system-ui, sans-serif"
FONT_MONO = "'JetBrains Mono', ui-monospace, monospace"


def ramp_color(ramp, i, n):
    '''Pick an evenly spaced step of a ramp for item i of n.'''
    if n <= 1:
        return ramp[len(ramp) // 2]
    lo, hi = 2, len(ramp) - 1
    return ramp[round(lo + (hi - lo) * i / (n - 1))]


_axis = dict(
    gridcolor=GRID, linecolor=LINE, zerolinecolor=LINE, tickcolor=LINE,
    tickfont=dict(color=MUTED, size=11), title_font=dict(color=MUTED, size=12),
    showline=False, ticks="",
)

pio.templates["berlin"] = go.layout.Template(layout=dict(
    separators=", ",
    font=dict(family=FONT_BODY, color=TEXT_2, size=12),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    colorway=CATEGORICAL,
    xaxis=_axis, yaxis=_axis,
    hoverlabel=dict(bgcolor=SURFACE_2, bordercolor=LINE,
                    font=dict(color=TEXT, family=FONT_BODY, size=12)),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT_2, size=12),
                orientation="h", yanchor="bottom", y=1.02, x=0),
    title=dict(font=dict(color=TEXT, size=15)),
    annotationdefaults=dict(font=dict(color=TEXT_2, size=12)),
    margin=dict(l=56, r=24, t=40, b=48),
    bargap=0.08,
    hovermode="closest",
    polar=dict(bgcolor="rgba(0,0,0,0)"),
))
pio.templates.default = "berlin"

GRAPH_CONFIG = {"displaylogo": False,
                "modeBarButtonsToRemove": ["lasso2d", "autoScale2d", "toggleSpikelines"]}
