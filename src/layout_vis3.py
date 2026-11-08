import theme as T


def _callout(fig, nations_sorted, nation, text):
    if nation not in nations_sorted:
        return
    y = nations_sorted.index(nation)
    fig.add_annotation(
        x=2023.3, y=y, ax=2024.6, ay=y + 0.55, xref="x", yref="y", axref="x", ayref="y",
        text=text, showarrow=True, arrowhead=0, arrowwidth=1, arrowcolor=T.GOLD,
        font=dict(size=11, color=T.TEXT), bgcolor=T.SURFACE_2, bordercolor=T.GOLD,
        borderwidth=1, borderpad=5, align="left", xanchor="left",
    )


def configure_layout(fig, nations_sorted, selected_category, selected_genre):
    if selected_category == "ALL":
        if selected_genre == "ALL":
            _callout(fig, nations_sorted, "Kenya", "<b>Kipchoge</b><br>5 victoires")
        elif selected_genre == "W":
            _callout(fig, nations_sorted, "Ethiopia", "<b>Assefa</b><br>2:11:53 · RM")
    return fig
