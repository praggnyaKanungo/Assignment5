#Praggnya Kanungo
#DS 4003
        
#First I am importing the necessary libraries for the web application, data visualization, and data manipulation for my dashboard
import dash 
from dash import dcc, html 
from dash.dependencies import Input, Output
import plotly.express as px  
import pandas as pd  

# First, because I am using a stylesheet, ill do the following line
#this defines a list of external stylesheets to use for styling the Dash application
stylesheets = ['https://cdn.jsdelivr.net/npm/picnic']

# Then, i am reading the GDP per capita data from a CSV file into a Pandas DataFrame 
#Then, i am also transforming it from wide format to long format, because that is suitable for Plotly
df = pd.read_csv("data/gdp_pcap.csv")
# i am using melt to do that
df_long = df.melt(id_vars=['country'], var_name='year', value_name='gdpPercap')
df_long['year'] = pd.to_numeric(df_long['year'])

#then I am trying understand the year values in the data set
# First I am calculateing the minimum and maximum year from the dataset for the year slider
min_year = df_long['year'].min()
max_year = df_long['year'].max()

# here I am extracting the unique countries for the country dropdown menu
countries = df_long['country'].unique()

# Then i begin builidng the dashboard
# here I first have to initialize the Dash application and its server
app = dash.Dash(__name__, external_stylesheets=stylesheets)
server = app.server

# I am setting the title of the Dash application
app.title = "Gapminder GDP Per Capita Analysis"

# I am starting by creating an initial line plot of GDP per capita over time for all countries
fig = px.line(df_long, x="year", y="gdpPercap", color="country", title="GDP Per Capita Over Time",
              labels={"gdpPercap": "GDP per Capita", "year": "Year"})
fig.update_layout(transition_duration=500)

# The blow code is defining the layout of the Dash application, including Markdown text for description,
# a dropdown menu for selecting countries, a range slider for selecting years, and
# a Graph component for displaying the GDP per capita line plot
app.layout = html.Div(children=[
    #this is my code for the markdown, which I am using for the title and dashboard description
    # My first element of the layout is a Markdown
    # the follwowing code is something i learned from class8 and i looked at Prof Kupperman's code as a reference.
    # this adds a Markdown section for the title and description of the dashboard
    dcc.Markdown('''
        # Gapminder GDP Per Capita Analysis

        This app explores the GDP per capita across various countries over time using this interactive dashboard. 
        Components of this app allow for in-depth analysis of the GDP per capita of different countries across time
        by using a dropdown menu that allows you to pick different countries and a slider that allows you to choose a 
        range of years. A line graph plots the GDP per capita of different countries in different colors and shows the fluctuation over time.
        This is an important app because it analyzes the GDP per capita. The GDP per capita data, which is being drawn from the Gapminder dataset, 
        is something that illustrates the average income per person in a country's population. It gives insight into the economic health and living standards
        of a given country at a given time.
    ''', style={'textAlign': 'center'}), # the style={} is just styling the markdown further, such as aligning it in the middle

    #The next elements I coded is  the dropdown and slider
    # the code for the those two elements are shown in the following
    html.Div(style={'padding': '20px 0px'}, children=[
        # The following is my code for the dropdown
        # this dropdown menu for selecting countries
        # For writing this code, i referred to class 8
        html.Div([
            dcc.Dropdown(
                id='country-dropdown',
                options=[{'label': country, 'value': country} for country in countries], # This line is setting dropdown options based on countries
                value=[countries[0]], # This is just my selected default value
                multi=True,
                style={'width': '100%'}
            )
        ], style={'width': '45%', 'display': 'inline-block'}), # This style={} is styling the dropdown container by making it 45% of the width of the page
        
        html.Div([
        # the following is my code for the slider
        # I've created the Range slider for selecting the year range
        # For writing this code, I referred to class 8
            dcc.RangeSlider(
                id='year-slider',  # this is just the id of this slider
                min=min_year, # this is the setting minimum value
                max=max_year, # this is setting maximum value
                step=1, # this is just setting the step size
                value=[min_year, max_year], # I am setting a default selected range
                marks={str(year): str(year) for year in range(min_year, max_year+1, 10)}, # Marks for years
                className="slider",
            )
        ], style={'width': '50%', 'display': 'inline-block', 'marginLeft': '5%'}), # this simply further styles the slider container by making it a smaller width
    ]),
    # Now, finally, I am adding the graph component for displaying the GDP per capita chart
    dcc.Graph(
        id='gdp-percap-graph',
        figure=fig,
        style={'width': '100%'} # this just styles the graph component. I want it to be as wide as the page
    ),
])

# The following is basically the part I changed from assignment 4
# this following part defines the callback functio
#this is the function that that updates the line plot based on the selected countries and year range. 
# i've also added dode to filter the years
@app.callback(
    Output('gdp-percap-graph', 'figure'),
    [Input('country-dropdown', 'value'),
     Input('year-slider', 'value')]
)
def update_graph(selected_countries, selected_years):
    
    # This part of my code filters the DataFrame based on the user's selections:
    # It makes sure it only includes the rows where the 'country' column matches any of the selected countries.
    # It makes sure it only includes the rows where the 'year' column falls within the selected year range.

    filtered_df = df_long[(df_long['country'].isin(selected_countries)) & 
                          (df_long['year'] >= selected_years[0]) & 
                          (df_long['year'] <= selected_years[1])]
    
    # Then I am simply using Plotly Express to create a line plot from the filtered DataFrame (we learned this in class!)
    # The plot shows GDP per capita ('gdpPercap') on the y-axis and year on the x-axis, 
    fig = px.line(filtered_df, x="year", y="gdpPercap", color="country",
                  title="GDP Per Capita Over Time",
                  labels={"gdpPercap": "GDP per Capita", "year": "Year"})

    # Here I am determine the min and max values for GDP per capita within the filtered dataset
    # I am doing this in order to make sure my y-axis looks neat and sorted
    min_gdp = filtered_df['gdpPercap'].min()
    max_gdp = filtered_df['gdpPercap'].max()

    # I am using this technique: I am setting the y-axis range with a small buffer
    buffer = (max_gdp - min_gdp) * 0.1  # 10% buffer on each side is conventional for many  small dashboards from what I learned in high school
    fig.update_yaxes(range=[min_gdp - buffer, max_gdp + buffer])
    
    fig.update_layout(transition_duration=500) # this is for smooth transition
    
    return fig


# This is the final line that runs the app if this script is executed as the main program
if __name__ == '__main__':
    app.run_server(debug=True)

