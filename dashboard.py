# Dashboard
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table

# Plot ly
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from dash.dependencies import Input, Output

# Datatable
import pandas as pd

# Most importan words
import nltk
from collections import Counter


# Dictionary of several databases
database_dict = {
    'MET' : 'csv/Anonym.csv',
    'GLO' : 'csv/Glob.csv',
    'COMP' :'csv/Comp.csv'
}
key_dropdown_lb = 'MET'


database_csv = database_dict[key_dropdown_lb]
df = pd.read_csv(database_csv, usecols = ['Location', 'Created At', 'Text', 'Sentiment', 'Polarity', 'Favs', 'Retweets'])


# Pre processing for Hot Keywoards
top_N = 10
stopwords = nltk.corpus.stopwords.words('english')
RE_stopwords = r'\b(?:{})\b'.format('|'.join(stopwords)) # RegEx for stopwords



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


"""****************
Application Layout
*******************"""
app.layout = html.Div(children=[
    html.Div(
        html.H1 (style={'width': '58%','float': 'left', 'text-align':'right'}, children='Anonym\'s Media Monitoring')
    ),
    html.Div(style={'width': '30%', 'display': 'inline-block', 'padding-left': '5%', 'padding-top': '10px'}, children=[
        dcc.Dropdown(
            id='my-dropdown',
            options=[
                {'label': 'Anonym', 'value': 'MET'},
                {'label': 'Temas Globales', 'value': 'GLO'},
                {'label': 'Competencia', 'value': 'COMP'}
            ],
            value='MET'
            ),
        html.Div(id='output-container')
        ])
    ,
    html.Div(id = 'par', children=[
    	html.Div(
		    dcc.Graph(style={'width': '49%', 'padding': '0 0 0 20', 'float': 'left'}, id='a_graph',)
                ),
    	html.Div(
		    dcc.Graph(
		        id='pie-chart',
		        style={'display': 'inline-block', 'width': '49%'}, 
		    )
		)
    ]
	),
    dash_table.DataTable(
        id='datatable-filtering-fe',
        style_cell={'textAlign': 'left'},
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        },
        style_data_conditional=[{
            'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(248, 248, 248)'
        }],
        page_current= 0,
        page_size= 6,
        columns=[
            {"name": i, "id": i, "deletable": False} for i in df.columns
        ],
        filter_action="native",
        filter_query=''
    ),
    html.Div(id='datatable-filter-container')
])



"""**********************************************
Callbacks for changing dropdown listbox and table
*************************************************"""

""" ----------
    callback : type
    Description of `callback`.
    Changes the Pie Chart, depending on the dropdown list box
"""
@app.callback(
    dash.dependencies.Output('pie-chart', 'figure'),
    [dash.dependencies.Input('my-dropdown', 'value')])
def update_output(value):
    global key_dropdown_lb
    key_dropdown_lb = value
    database_csv = database_dict[key_dropdown_lb]
    df = pd.read_csv(database_csv, usecols = ['Location', 'Created At', 'Text', 'Sentiment', 'Polarity', 'Favs', 'Retweets'])
    
    figure={
        'data': [
            go.Pie(
                labels=['Positives', 'Negatives', 'Neutrals'], 
                values=[
                        len(df[df['Sentiment'] == 'Positive']), 
                        len(df[df['Sentiment'] == 'Negative']), 
                        len(df[df['Sentiment'] == 'Neutral'])
                        ],
                name="View Metrics",
                marker_colors=['rgba(184, 247, 212, 0.6)','rgba(255, 50, 50, 0.6)','rgba(131, 90, 241, 0.6)'],
                textinfo='value',
                hole=.65)
        ]
    }
    return figure


""" ----------
    callback : type
    Description of `callback`.
    Changes the Side Bar, depending on the dropdown list box, and depending on the table filter
"""
@app.callback(
    dash.dependencies.Output('a_graph', 'figure'),
    [dash.dependencies.Input('my-dropdown', 'value'), Input('datatable-filtering-fe', "filter_query")])
def update_output(value, filter_query):
    global key_dropdown_lb
    key_dropdown_lb = value
    database_csv = database_dict[key_dropdown_lb]
    df = pd.read_csv(database_csv, usecols = ['Text', 'Sentiment'])
    
    # Check for query inside the table
    if (filter_query):
        if 'Negative' in filter_query :
            df = df[df['Sentiment'].values  == "Negative"]
        else:
            df = df[df['Sentiment'].values  == "Positive"]

    figure={
        'data': [go.Bar(x=[1, 2, 3, 4, 5, 6,7,8,9,10], 
                        y= list(pd.DataFrame(Counter(
                            (df['Text'].str.lower().replace([r'\|', RE_stopwords], [' ', ''], regex=True).str.cat(sep=' ').split())
                            ).most_common(top_N))[0]),
                        orientation='h')]
    }
    return figure


""" ----------
    callback : type
    Description of `callback`.
    Changes the Table, depending on the dropdown list box
"""
@app.callback(
    dash.dependencies.Output('datatable-filtering-fe', 'data'),
    [dash.dependencies.Input('my-dropdown', 'value')])
def update_chart(value):
    global key_dropdown_lb
    key_dropdown_lb = value
    database_csv = database_dict[key_dropdown_lb]
    df = pd.read_csv(database_csv, usecols = ['Location', 'Created At', 'Text', 'Sentiment', 'Polarity', 'Favs', 'Retweets'])
    data=df.to_dict('records')
    return data


if __name__ == '__main__':
    app.run_server(debug=True)
