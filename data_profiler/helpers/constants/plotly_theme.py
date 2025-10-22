
import plotly.graph_objects as go

apex_template = go.layout.Template(
    layout=go.Layout(
        title=dict(
            font=dict(size=18, weight="bold"),
            xref='container', x=0.05,
            yref='container', y=0.95,  
        ),
        font_family="Tahoma",
        font_color="black",
        paper_bgcolor="#f3f3f3",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            zeroline=False,
            showgrid=True,
            gridcolor="#cdcdcd",
            gridwidth=1,
            ticks="outside",
            tickcolor="#cdcdcd",
            griddash="dot",
            title=dict(
                font=dict(size=14, weight="bold")  
            ),
            tickfont=dict(size=12),
        ),
        yaxis=dict(
            zeroline=False,
            showgrid=True,
            gridcolor="#cdcdcd",
            gridwidth=1,
            ticks="outside",
            tickcolor="#cdcdcd",
            griddash="dot",
            title=dict(font=dict(size=14, weight="bold")),
            tickfont=dict(size=12),
        ),
        colorway=["#44546a", "#95b2ba", "#ee6f3c", '#B0A89D', '#6D766B', '#A48E96', '#9E940F', '#B8B8B8'],  # Custom color palette
    )
)
