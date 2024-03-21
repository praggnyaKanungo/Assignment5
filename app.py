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

# Converting 'country' column to a categorical data type
df['country'] = df['country'].astype('category')
# Converting 'year' to numeric
df_long['year'] = pd.to_numeric(df_long['year'], errors='coerce')

# Converting 'gdpPercap' to numeric
df_long['gdpPercap'] = pd.to_numeric(df_long['gdpPercap'], errors='coerce')

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
@app.callback(
    Output('gdp-percap-graph', 'figure'),
    [Input('country-dropdown', 'value'),
     Input('year-slider', 'value')]
)
#This is the function that updates the plot based on selected countries and years
def update_graph(selected_countries, selected_years):
    # First i am checking if selected_countries is a list, if not, I am converting it to one list
    #Why am i doing this? its because iam using.isin after this for filtering properly and its expects lists
    if not isinstance(selected_countries, list):
        selected_countries = [selected_countries]  # Wrapping the single country in a list

    # This part of my code filters the DataFrame based on the user's selections:
    # It makes sure it only includes the rows where the 'country' column matches any of the selected countries.
    # It makes sure it only includes the rows where the 'year' column falls within the selected year range.
    filtered_df = df_long[df_long['country'].isin(selected_countries) &
                          (df_long['year'] >= selected_years[0]) &
                          (df_long['year'] <= selected_years[1])]
    # I ran my app before this and i realized that theres some chunky lines or discontinous lines.
    #i cant just drop this data because that doesn't help the data visualization
    #thats why I am going to aggregate teh data (by doing the mean gdp for missing data just to help the data visualization)
    # I will be replacing missing values in the 'gdpPercap' column with the mean GDP per capita of the respective country
    # I am using the transform function applies the lambda to each group of rows with the same country
    #what is does is that it basically puts the mean to fill in the missing data for each country group
    filtered_df['gdpPercap'] = filtered_df.groupby('country')['gdpPercap'].transform(lambda x: x.fillna(x.mean()))

    # In case anything is still NaN, I am dropping the rows where 'gdpPercap' is still NaN
    filtered_df = filtered_df.dropna(subset=['gdpPercap'])

    # Sorting by 'year' to ensure that the lines on the plot are drawn nicely
    filtered_df = filtered_df.sort_values(by='year')

    # Then I am simply using Plotly Express to create a line plot from the filtered DataFrame (we learned this in class!)
    # The plot shows GDP per capita ('gdpPercap') on the y-axis and year on the x-axis, 
    fig = px.line(filtered_df, x="year", y="gdpPercap", color="country",
                  title="GDP Per Capita Over Time",  # Set the title of the plot
                  labels={"gdpPercap": "GDP per Capita", "year": "Year"})  # Set the labels of the axes

    # For smooth transition
    fig.update_layout(transition_duration=500)

    # Return the figure object which contains the line plot
    return fig




if __name__ == '__main__':
    app.run_server(debug=True)
