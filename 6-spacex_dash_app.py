# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options = [
                                        {'label': 'All Sites', 'value': 'ALL'},
                                        {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                        {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                        {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                        {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
                                    ],
                                    value = 'ALL',
                                    placeholder = "Select a Lauch Site here",
                                    searchable = True
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=0,
                                    max=10000,
                                    step=1000,
                                    marks={i: f'{i}Kg' for i in range(0, 10001, 1000)},
                                    value=[min_payload, max_payload]  # Default value will be between min_payload and max_payload
                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def update_pie_chart(selected_site):
    # If 'ALL' is selected, use the entire dataframe
    if selected_site == 'ALL':
        # Group by success (class column) and count occurrences
        success_counts = spacex_df['class'].value_counts()
        # Plot the pie chart for all sites
        fig = px.pie(
            names=success_counts.index,
            values=success_counts.values,
            title='Launch Success Counts for All Sites'
        )
    else:
        # Filter the dataframe for the selected launch site
        site_data = spacex_df[spacex_df['Launch Site'] == selected_site]
        success_counts = site_data['class'].value_counts()
        # Plot the pie chart for the selected site
        fig = px.pie(
            names=success_counts.index,
            values=success_counts.values,
            title=f'Launch Success Counts for {selected_site}'
        )

    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(selected_site, payload_range):
    # Unpack the payload range into low and high values
    low_payload, high_payload = payload_range
    
    # Filter the dataframe based on the selected payload range
    if selected_site == 'ALL':
        # If all sites are selected, filter the data for the selected payload range
        filtered_data = spacex_df[(spacex_df['Payload Mass (kg)'] >= low_payload) &
                                  (spacex_df['Payload Mass (kg)'] <= high_payload)]
    else:
        # If a specific site is selected, filter the data by site and payload range
        filtered_data = spacex_df[(spacex_df['Launch Site'] == selected_site) &
                                  (spacex_df['Payload Mass (kg)'] >= low_payload) &
                                  (spacex_df['Payload Mass (kg)'] <= high_payload)]
    
    # Create the scatter plot with the filtered data
    fig = px.scatter(
        filtered_data, 
        x='Payload Mass (kg)', 
        y='class',  # Success/failure: 1 = Success, 0 = Failure
        color='Booster Version Category',  # Color by the booster version
        title=f'Launch Success vs Payload Mass for {selected_site if selected_site != "ALL" else "All Sites"}',
        labels={'Payload Mass (kg)': 'Payload Mass (kg)', 'class': 'Launch Outcome', 'Booster Version Category': 'Booster Version'},
        category_orders={"Booster Version Category": sorted(filtered_data['Booster Version Category'].unique())}  # Ensures consistent order of boosters
    )
    
    # Return the figure to be displayed in the scatter plot
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
