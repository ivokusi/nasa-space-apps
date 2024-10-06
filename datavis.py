import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State, ALL
import pandas as pd
from dash.dependencies import Input, Output
import plotly.express as px
import math


data = pd.read_csv('OSD-379/metadata/a_OSD-379_transcription-profiling_rna-sequencing-(rna-seq)_Illumina NovaSeq.txt', sep='\t', index_col=False)
data2 = pd.read_csv('OSD-379/metadata/s_OSD-379.txt', sep='\t', index_col=False)
data2.columns = data2.columns.str.strip()

# Initialize the Dash app with suppress_callback_exceptions
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Function to create graphs
def create_pie_chart(df, column, title):
    # Group by the categorical column and count occurrences
    category_counts = df[column].value_counts().reset_index()
    category_counts.columns = [column, 'Count']  # Rename columns for clarity

    # Create the pie chart using Plotly
    fig = px.pie(category_counts, 
                 names=column,  # The category names
                 values='Count',  # The counts of each category
                 title=title)
    return fig


def create_histogram(df, x_column, title):
    # Create histogram using Plotly
    print([col for col in data2.columns if x_column in col])
    x_min = data[x_column].min()
    x_max = data[x_column].max()
    bin_start = math.floor(x_min)
    bin_end = math.ceil(x_max)
    
    nbins = bin_end - bin_start #we want bind_width 1
    
    
    fig = px.histogram(df, x=x_column, hover_data=['Sample Name'], nbins=nbins)
    fig.update_layout(title=title, xaxis_title=x_column, yaxis_title="Frequency")
    
    return fig

# App layout
app.layout = html.Div([
    html.H1("RNA-Seq Data Visualization", style={
                'font-family': 'Arial',       # Font family
                'font-weight': 'bold',        # Bold font
                'color': '#333333',           # Darker gray text color
                'padding-top': '20px',        # Padding at the top
                'padding-bottom': '0.5px',     # Padding at the bottom
                'padding-left': '45px',     # Padding at the bottom
                'text-align': 'left',         # Align text to the left
                'font-size': '24px'           # Font size adjustment
            }),
    
    html.Div([
        dcc.Graph(id='rna-contamination-histogram', 
                  figure=create_histogram(data, 'Parameter Value[rRNA Contamination]', 'Histogram of RNA Contamination')),
        dcc.Graph(id='qa-score-histogram', 
                  figure=create_histogram(data, 'Parameter Value[QA Score]', 'Histogram of QA Score')),
        dcc.Graph(id='spaceflight-histogram',
                  figure=create_pie_chart(data2, 'Factor Value[Spaceflight]', 'Pie plot of factor value Spaceflight')),
        dcc.Graph(id='dissectioncond-histogram',
                  figure=create_pie_chart(data2, 'Factor Value[Dissection Condition]', 'Pie plot of Dissection Condition')),
    ]),

    html.Div([
        html.H3("Selected Samples",
                style={
                'font-family': 'Arial',       # Font family
                'font-weight': 'bold',        # Bold font
                'color': '#333333',           # Darker gray text color
                'padding-top': '20px',        # Padding at the top
                'padding-bottom': '0.5px',     # Padding at the bottom
                'padding-left': '45px',     # Padding at the bottom
                'text-align': 'left',         # Align text to the left
                'font-size': '24px'           # Font size adjustment
            }),
        html.Div(id='sample-list'),
    ]),
    
    dcc.Store(id='samples-in-bin'),
    dcc.Store(id='last-clicked', data=None),

    html.Div([
        html.H3("Selected Sample Information"),
        html.Div(id='sample-info'),
    ])
])

# Callback to update the sample list when a bar is clicked
@app.callback(
    [Output('sample-list', 'children'),
     Output('samples-in-bin', 'data'),
     Output('last-clicked', 'data')],
    [Input('rna-contamination-histogram', 'clickData'),
     Input('qa-score-histogram', 'clickData')],
    [State('last-clicked', 'data')]
)
def display_samples_in_bin(rna_click, qa_click, last_clicked):
    # Determine which histogram was clicked
    if rna_click and (last_clicked != 'rna'):
        click_data = rna_click
        column = 'Parameter Value[rRNA Contamination]'
        last_clicked = 'rna'
    elif qa_click and (last_clicked != 'qa'):
        click_data = qa_click
        column = 'Parameter Value[QA Score]'
        last_clicked = 'qa'
    else:
        # If no new click or same histogram clicked again, do nothing
        return "Click on a bar to see the sample names in that bin.", None, last_clicked

    x_mid = click_data['points'][0]['x']
    print(f"Click data: {click_data}")
    print(f"Click data: {x_mid}")
    # Assuming bin width is 1, calculate the start and end of the bin
    bin_width = 1
    x_bin_low = x_mid - (bin_width / 2)  # Start of the bin
    print(f"x_bin_low: {x_bin_low}")
    x_bin_high = x_mid + (bin_width / 2)  # End of the bin

    # Filter the data for samples within that bin range
    column = 'Parameter Value[rRNA Contamination]' if rna_click else 'Parameter Value[QA Score]'
    
    samples_in_bin = data[(data[column] >= x_bin_low) & (data[column] < x_bin_high)]
    samples_in_bin_data = samples_in_bin.to_dict('records')
    

    # Display sample names as clickable buttons
    return html.Ul([
    html.Li(html.Button(sample['Sample Name'], 
                        id={'type': 'sample-button', 'index': sample['Sample Name']}, 
                        style={'background-color': '#86c7eb',  # Green background
                               'color': 'white',               # White text
                               'padding': '10px 20px',          # Padding
                               'border': 'none',                # No border
                               'border-radius': '5px',          # Rounded corners
                               'cursor': 'pointer',             # Pointer cursor on hover
                               'margin': '5px'}))               # Space between buttons
    for sample in samples_in_bin_data
    ], style={'list-style-type': 'none'}), samples_in_bin_data, last_clicked



@app.callback(
    Output('sample-info', 'children'),
    [Input({'type': 'sample-button', 'index': ALL}, 'n_clicks')],
    [State('samples-in-bin', 'data')]
)
def display_sample_info(n_clicks_list, samples_in_bin_data):
    if not any(n_clicks_list):
        return "Click on a sample to see detailed information."
    
    # Find which button was clicked
    clicked_index = [i for i, clicks in enumerate(n_clicks_list) if clicks]
    
    if clicked_index and samples_in_bin_data:
        clicked_sample = samples_in_bin_data[clicked_index[0]]
        return html.Div([
            html.P(f"Sample Name: {clicked_sample['Sample Name']}"),
            html.P(f"QA Instrument: {clicked_sample['Parameter Value[QA Instrument]']}"),
            html.P(f"Parameter Value[QA Assay]: {clicked_sample['Protocol REF']}"),
            html.P(f"Unit: {clicked_sample['Unit']}"),
            html.P(f"Term Source REF: {clicked_sample['Term Source REF']}"),
            html.P(f"Term Accession Number: {clicked_sample['Term Accession Number']}"),
            html.P(f"Extract Name: {clicked_sample['Extract Name']}"),
            html.P(f"Protocol REF: {clicked_sample['Protocol REF']}"),
            html.P(f"Spike-in Quality Control: {clicked_sample['Parameter Value[Spike-in Quality Control]']}"),
            html.P(f"Term Source REF: {clicked_sample['Term Source REF']}"),
        
            html.P(f"Spike-in Mix Number: {clicked_sample['Parameter Value[Spike-in Mix Number]']}"),
            html.P(f"library selection: {clicked_sample['Parameter Value[library selection]']}"),
            html.P(f"library layout: {clicked_sample['Parameter Value[library layout]']}"),
            html.P(f"stranded: {clicked_sample['Parameter Value[stranded]']}"),
            html.P(f"rRNA Contamination: {clicked_sample['Parameter Value[rRNA Contamination]']}"),
            # Add other fields as needed
        ])
    
    return "No sample selected."
    
# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)