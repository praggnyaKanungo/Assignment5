#Praggnya Kanungo
#DS 4003


import dash 
from dash import dcc, html 
from dash.dependencies import Input, Output
import plotly.express as px  
import pandas as pd  

stylesheets = ['https://cdn.jsdelivr.net/npm/picnic']

df = pd.read_csv("data/gdp_pcap.csv")
df_long = df.melt(id_vars=['country'], var_name='year', value_name='gdpPercap')
df_long['year'] = pd.to_numeric(df_long['year'])

min_year = df_long['year'].min()
max_year = df_long['year'].max()
countries = df_long['country'].unique()

app = dash.Dash(__name__, external_stylesheets=stylesheets)
server = app.server

app.title = "Gapminder GDP Per Capita Analysis"

fig = px.line(df_long, x="year", y="gdpPercap", color="country", title="GDP Per Capita Over Time",
              labels={"gdpPercap": "GDP per Capita", "year": "Year"})
fig.update_layout(transition_duration=500)

app.layout = html.Div(children=[
    dcc.Markdown('''
        # Gapminder GDP Per Capita Analysis

        This app explores the GDP per capita across various countries over time using this interactive dashboard. 
        Components of this app allow for in-depth analysis of the GDP per capita of different countries across time
        by using a dropdown menu that allows you to pick different countries and a slider that allows you to choose a 
        range of years. A line graph plots the GDP per capita of different countries in different colors and shows the fluctuation over time.
        This is an important app because it analyzes the GDP per capita. The GDP per capita data, which is being drawn from the Gapminder dataset, 
        is something that illustrates the average income per person in a country's population. It gives insight into the economic health and living standards
        of a given country at a given time.
    ''', style={'textAlign': 'center'}),
    
    html.Div(style={'padding': '20px 0px'}, children=[
        html.Div([
            dcc.Dropdown(
                id='country-dropdown',
                options=[{'label': country, 'value': country} for country in countries],
                value=[countries[0]],
                multi=True,
                style={'width': '100%'}
            )
        ], style={'width': '45%', 'display': 'inline-block'}),
        
        html.Div([
            dcc.RangeSlider(
                id='year-slider',
                min=min_year,
                max=max_year,
                step=1,
                value=[min_year, max_year],
                marks={str(year): str(year) for year in range(min_year, max_year+1, 10)},
                className="slider",
            )
        ], style={'width': '50%', 'display': 'inline-block', 'marginLeft': '5%'}),
    ]),
    
    dcc.Graph(
        id='gdp-percap-graph',
        figure=fig,
        style={'width': '100%'}
    ),
])

@app.callback(
    Output('gdp-percap-graph', 'figure'),
    [Input('country-dropdown', 'value'),
     Input('year-slider', 'value')]
)
def update_graph(selected_countries, selected_years):
    filtered_df = df_long[(df_long['country'].isin(selected_countries)) & 
                          (df_long['year'] >= selected_years[0]) & 
                          (df_long['year'] <= selected_years[1])]
    
    fig = px.line(filtered_df, x="year", y="gdpPercap", color="country",
                  title="GDP Per Capita Over Time",
                  labels={"gdpPercap": "GDP per Capita", "year": "Year"})
    
    fig.update_layout(transition_duration=500)
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
