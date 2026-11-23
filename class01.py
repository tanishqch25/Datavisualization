import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, Input, Output

url = "https://raw.githubusercontent.com/Coding-with-Adam/Dash-by-Plotly/master/Other/Monterrey/airbnb.csv"

df = pd.read_csv(url)
print(df.shape)
print(df.columns.tolist())

req_col = ['latitude', 'longitude', 'price', 'minimum_nights']
missing = [c for c in req_col if c not in df.columns]

if missing:
    raise ValueError(f"Missing columns: {missing}")

for col in req_col:
    if col == 'price':
        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce'
        )
    else:
        df[col] = pd.to_numeric(df[col], errors='coerce')

df = df.dropna(subset=req_col)

app = Dash(__name__)

max_price_val = int(df['price'].max())
safe_upper_bound = min(2500, max(1000, max_price_val))

app.layout = html.Div(children=[
    html.H1(children='Dash App', style={'textAlign': 'center'}),

    html.H3("Select minimum nights"),
    dcc.Slider(
        id='slider', min=1, max=30, step=1, value=3,
        marks={i: str(i) for i in range(1, 31, 5)}
    ),

    html.Br(),
    html.H3('Select price'),
    dcc.RangeSlider(
        id='slider2',
        min=0,
        max=max(1000, max_price_val),
        value=[0, safe_upper_bound],
        step=100,
        marks=None,
        tooltip={'placement': 'top', 'always_visible': True}
    ),

    html.Br(),
    html.Div(id='count', style={'textAlign': 'center', 'fontWeight': 'bold'}),
    dcc.Graph(id='scatter_plot', style={'height': '720px'})
])

@app.callback(
    Output('scatter_plot', 'figure'),
    Output('count', 'children'),
    Input('slider', 'value'),
    Input('slider2', 'value')
)
def update_scatter(min_nights, price_range):
    min_price, max_price = price_range

    filtered_df = df[
        (df['minimum_nights'] <= min_nights) &
        (df['price'] >= min_price) &
        (df['price'] <= max_price)
    ]

    # FIXED: Standard 2D scatter plot
    fig = px.scatter(
        filtered_df,
        x='longitude',
        y='latitude',
        color='price',
        size='price',
        color_continuous_scale=px.colors.sequential.Viridis,
        size_max=15,
        hover_data=['minimum_nights', 'price']
    )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    return fig, f"Properties shown: {len(filtered_df)}"

if __name__ == '__main__':
    app.run(debug=True)