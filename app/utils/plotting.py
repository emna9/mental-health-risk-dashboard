from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


CHART_COLORS = {
    "accent": "#2f6b63",
    "highlight": "#c2703d",
    "muted": "#8ba39b",
    "rose": "#a85a68",
    "gold": "#b8953a",
    "surface": "#f7f3ee",
    "ink": "#16302b",
}

PALETTE = [
    "#2f6b63",
    "#c2703d",
    "#a85a68",
    "#b8953a",
    "#5a8a7c",
    "#7a4f2e",
]


def apply_chart_theme(fig: go.Figure) -> go.Figure:
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={
            "family": "Manrope, Avenir Next, Segoe UI, sans-serif",
            "color": CHART_COLORS["ink"],
            "size": 12,
        },
        title_font={
            "family": "Cormorant Garamond, Georgia, serif",
            "size": 17,
            "color": CHART_COLORS["ink"],
        },
        margin={"l": 24, "r": 24, "t": 52, "b": 24},
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "x": 0,
            "font": {"size": 11, "family": "Manrope, sans-serif"},
            "bgcolor": "rgba(255,255,255,0.6)",
            "bordercolor": "rgba(22,48,43,0.10)",
            "borderwidth": 1,
        },
        hoverlabel={
            "bgcolor": "rgba(255,255,255,0.95)",
            "bordercolor": "rgba(22,48,43,0.15)",
            "font_family": "Manrope, sans-serif",
            "font_size": 12,
            "font_color": CHART_COLORS["ink"],
        },
    )
    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        tickfont={"size": 11, "family": "Manrope, sans-serif"},
        title_font={"size": 12, "family": "Manrope, sans-serif"},
        linecolor="rgba(22,48,43,0.12)",
        showline=True,
    )
    fig.update_yaxes(
        gridcolor="rgba(22,48,43,0.07)",
        gridwidth=1,
        zeroline=False,
        tickfont={"size": 11, "family": "Manrope, sans-serif"},
        title_font={"size": 12, "family": "Manrope, sans-serif"},
        showline=False,
    )
    return fig


def bar_chart(
    data: pd.DataFrame,
    x: str,
    y: str,
    color: str | None,
    title: str,
    horizontal: bool = False,
    color_sequence: list[str] | None = None,
) -> go.Figure:
    fig = px.bar(
        data,
        x=y if horizontal else x,
        y=x if horizontal else y,
        color=color,
        title=title,
        orientation="h" if horizontal else "v",
        color_discrete_sequence=color_sequence or PALETTE,
        template="none",
    )
    fig.update_traces(
        marker_line_width=0,
        opacity=0.92,
    )
    return apply_chart_theme(fig)


def histogram(data: pd.DataFrame, x: str, color: str | None, title: str, nbins: int = 20) -> go.Figure:
    fig = px.histogram(
        data,
        x=x,
        color=color,
        nbins=nbins,
        barmode="overlay",
        opacity=0.80,
        title=title,
        color_discrete_sequence=PALETTE,
        template="none",
    )
    fig.update_traces(marker_line_width=0)
    return apply_chart_theme(fig)


def box_chart(data: pd.DataFrame, x: str, y: str, color: str | None, title: str) -> go.Figure:
    fig = px.box(
        data,
        x=x,
        y=y,
        color=color,
        title=title,
        color_discrete_sequence=PALETTE,
        points=False,
        template="none",
    )
    return apply_chart_theme(fig)


def scatter_chart(
    data: pd.DataFrame,
    x: str,
    y: str,
    color: str | None,
    size: str | None,
    title: str,
) -> go.Figure:
    fig = px.scatter(
        data,
        x=x,
        y=y,
        color=color,
        size=size,
        title=title,
        opacity=0.85,
        color_continuous_scale=[
            [0.0, "rgba(47,107,99,0.25)"],
            [0.5, "rgba(184,149,58,0.70)"],
            [1.0, "rgba(194,112,61,0.95)"],
        ],
        template="none",
    )
    fig.update_traces(marker_line_width=0.5, marker_line_color="rgba(255,255,255,0.6)")
    fig.update_coloraxes(
        colorbar_thickness=12,
        colorbar_len=0.6,
        colorbar_tickfont_size=10,
    )
    return apply_chart_theme(fig)


def metric_comparison_chart(data: pd.DataFrame, metric: str, title: str) -> go.Figure:
    sorted_data = data.sort_values(metric, ascending=False).reset_index(drop=True)
    colors = [CHART_COLORS["accent"], CHART_COLORS["highlight"], CHART_COLORS["rose"]]
    fig = go.Figure()
    for i, row in sorted_data.iterrows():
        fig.add_trace(go.Bar(
            x=[row["Model"]],
            y=[row[metric]],
            name=row["Model"],
            marker_color=colors[i % len(colors)],
            marker_line_width=0,
            opacity=0.92,
            showlegend=False,
        ))
    fig.update_layout(title=title, barmode="group")
    return apply_chart_theme(fig)
