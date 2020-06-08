import base64
import datetime
import io

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table

import plotly.graph_objs as go
import plotly.express as px

import pandas as pd

app = dash.Dash(__name__)
app.title = "Ta-Da, Data!"

app.layout = html.Div([
    html.A(html.Button('Back to LittleHotelier'),
    href='https://www.littlehotelier.com/?utm_source=google&utm_medium=cpc&utm_campaign=LH_G_APAC_New-Zealand_English_Exact_Brand_Core&gclid=CjwKCAjwssD0BRBIEiwA-JP5rCR69PyOXnS2zakyJLXtz2UguHXfVk2MSmsjbq-LjA6Q2q_DDDHuthoCPIUQAvD_BwE&gclsrc=aw.ds', target="_blank"),

    html.A(html.Button('T&Cs'),
    href='https://www.littlehotelier.com/data-security/', target="_blank"),

    html.H1('Ta-Da, Data!'),
    html.P('Discover your data! Upload a CSV file from LittleHotelier and unearth the wealth of knowledge to benefit and enrich your business!'),
    
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select CSV Files')
        ]),
        style={
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'solid',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px',
            'backgroundColor' : '#ed6d47',
            'color' : 'white',
            'margin' : '80px',
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Div(id='output-data-upload'),
])


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'Please upload a CSV file.'
        ])

#processes for the data (from pandas notebook)

    relevantdata = df.drop(columns=['Booking reference', 'Booked', 'Property name', 'Promotion code', 'Guest first name', 'Guest last name', 'Guest email', 'Guest phone number', 'Guest organisation', 'Guest address', 'Guest address2', 'Guest state', 'Guest post code', 'Check in date', 'Check out date', 'Arrival time', 'Guest comments', 'Requested newsletter', 'Status', 'Rate plans', 'Subtotal amount', 'Extra adult amount', 'Extra child amount' ,'Extra infant amount', 'Extras total amount', 'Credit card surcharge processed amount', 'Surcharge Percentage', 'Promotional Discount', 'Payment total', 'Payment Received', 'Number of adults', 'Number of children', 'Guest city', 'Number of infants', 'Number of Rooms', 'Custom Property Specific Data', 'Referral' ,'Payments deposit processed total', 'Payment outstanding', 'Mobile booking?', 'Promotion Description', 'Enter rates including fees', 'Fixed Taxes Total', 'Percentage Taxes Total', 'Rooms']) 

    # Visualisation for Booking Channel PIE
    channel = relevantdata['Channel name'].value_counts(normalize=True) * 100 

    channeldf = pd.DataFrame({'Channel':channel.index, 'Percentage':channel.values})  
        
    channelfig = px.pie(channeldf, values='Percentage', names='Channel', title='Pie Chart of Booking Channels Used By Guests')


    #  Visualisation for  Nationality PIE
    nationality = relevantdata['Guest country'].value_counts(normalize=True) * 100

    natdf = pd.DataFrame({'Nationality':nationality.index, 'Percentage':nationality.values})

    natfig = px.pie(natdf, values='Percentage', names='Nationality', title='Pie Chart Showing Nationalities of Guests by Percentage')

    #natfig = px.bar(natdf, x="Nationality", y="Percentage", orientation="v")

    #  Visualisation for Top Rooms booked BAR
    rooms = relevantdata['Room types'].value_counts(normalize=True) * 100
    toptenrooms = rooms.head(10)
    
    roomsdf = pd.DataFrame({'Room Type':toptenrooms.index, 'Percentage':toptenrooms.values})

    roomsfig = px.bar(roomsdf, x="Room Type", y="Percentage", orientation="v", title='Bar Chart to Show the Top 10 Room Types Booked')



#Return = what it shows

    return html.Div([
        html.H2('Modal Data From Your CSV.'),

        dash_table.DataTable(
            data = relevantdata.mode().to_dict('records'),
            columns = [{'name': i, 'id': i} for i in relevantdata.columns]
        ),

    html.Hr(),  # horizontal line
    html.H3('See below charts and tables made from your data file. Explore trends and patterns or upload a new file.'),
    html.Hr(),

    #Show visualisations
    dcc.Graph(figure=channelfig),

    html.Br(),

    dcc.Graph(figure=natfig),

    html.Br(),

    dcc.Graph(figure=roomsfig),

    html.Br(),
    ])

@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children

if __name__ == '__main__':
    app.run_server(debug=True)
