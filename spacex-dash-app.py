# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc, callback 
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Get distinct launch sites
launch_sites = spacex_df['Launch Site'].unique()

# Create the options list dynamically for selecting launch_site
dd_options_list = [{'label': 'All Sites', 'value': 'ALL'}]
for site in launch_sites:
    dd_options_list.append({'label': site, 'value': site})

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown', 
                                                options=dd_options_list, 
                                            value='ALL', 
                                            placeholder='Select a Launch Site', 
                                            searchable=True
                                        ),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider', min=0, max=10000, step=1000, value=[min_payload, max_payload], marks={0:'0', 100:'100'}),


                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    
    if entered_site == 'ALL':
        # For ALL sites, we use the full dataframe (spacex_df)
        # values='class' sums up the 1s (successes)
        # names='Launch Site' splits the pie slices by site
        fig = px.pie(spacex_df, 
                     values='class', 
                     names='Launch Site', 
                     title='Total Success Launches By Site')
        return fig
    else:
        # 1. Filter data
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site].copy()
        
        # 2. Rename 0/1 to Failure/Success for better readability
        filtered_df['class'] = filtered_df['class'].map({1: 'Success', 0: 'Failure'})
        
        # 3. Create chart with custom colors and labels
        fig = px.pie(filtered_df, 
                     names='class', 
                     title=f'Total Success Launches for site {entered_site}',
                     
                     # Pick specific colors (Optional but recommended)
                     color='class',
                     color_discrete_map={'Success': 'green', 'Failure': 'red'},
                     
                     # Rename 'class' to 'Outcome' in the tooltip/legend
                     labels={'class': 'Launch Outcome'}
                     )
        return fig


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'), 
    Input(component_id="payload-slider", component_property="value")],
)
def get_scatter_chart(entered_site, payload_range): # 2. Add arguments here
    
    # The payload_range comes from the slider as a list: [min, max]
    low, high = payload_range
    
    # Filter the data based on the slider range first
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    filtered_df = spacex_df[mask]
    
    # Logic for "ALL" sites vs Specific Site
    if entered_site == 'ALL':
        # Render scatter plot for all sites
        fig = px.scatter(filtered_df, 
                         x='Payload Mass (kg)', 
                         y='class', 
                         color='Booster Version Category',
                         title='Correlation between Payload and Success for all Sites')
        return fig
    else:
        # Filter specifically for the selected site
        site_filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        
        # Render scatter plot for that specific site
        fig = px.scatter(site_filtered_df, 
                         x='Payload Mass (kg)', 
                         y='class', 
                         color='Booster Version Category',
                         title=f'Correlation between Payload and Success for {entered_site}')
        return fig

# Run the app
if __name__ == '__main__':
    app.run()
