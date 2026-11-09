import theme as T


def _callout(fig, anchors, last_year, runner, year, text):
    '''Label in the right margin, arrow landing exactly on the runner's dot.'''
    if (runner, year) not in anchors:
        return
    x, y = anchors[(runner, year)]
    fig.add_annotation(
        x=x, y=y, ax=last_year + 0.75, ay=y + 0.45, xref="x", yref="y", axref="x", ayref="y",
        text=text, showarrow=True, arrowhead=0, arrowwidth=1, arrowcolor=T.GOLD, standoff=7,
        font=dict(size=11, color=T.TEXT), bgcolor=T.SURFACE_2, bordercolor=T.GOLD,
        borderwidth=1, borderpad=5, align="left", xanchor="left",
    )


# (runner, year) each callout points to, per (category, gender) filter
CALLOUTS = {
    ("ALL", "ALL"): ("Kipchoge Eliud", 2023, "<b>Kipchoge</b><br>5 victoires"),
    ("ALL", "W"): ("Assefa Tigst", 2023, "<b>Assefa</b><br>2:11:53 · RM"),
}


def callout_target(selected_category, selected_genre):
    c = CALLOUTS.get((selected_category, selected_genre))
    return (c[0], c[1]) if c else None


def configure_layout(fig, anchors, last_year, selected_category, selected_genre):
    c = CALLOUTS.get((selected_category, selected_genre))
    if c:
        _callout(fig, anchors, last_year, *c)
    return fig
