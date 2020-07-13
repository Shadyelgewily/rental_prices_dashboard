#Todo: extras (berging, schuur etc.) multisellect
#Todo: https://blog.jverkamp.com/2015/04/03/performance-problems-with-flask-and-docker/
#Todo: Restrict locations based on city (only allow cities that have been trained)
#Todo: sanity checks model (met tuin prijs is goedkoper dan zonder tuin etc.; zelfde geldt voor garage)
#Todo: studios met tuin komen niet vaak voor, dus dan kan het voorkomen dat de voorspelling een lagere huurprijs oplevert dan zonder tuin
#Todo: bouwjaar is erg gevoelig, kan bijvoorbeeld komen door weinig observaties of dat die observaties toevallig monumenten zijn (kan misschien beter opgedeeld worden in 5 periodes)
#Todo: feature achterom
#Todo: als je iets kopieert in de omschrijving eerst weer alle waarden resetten
#Todo: monument ja/nee
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from extract_features import features_from_description
from extract_features import features_from_zipcode
from rental_price_models import rental_price_rf

import pandas as pd
import pickle

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

zipcode_features_df =  pd.read_pickle("Data/CBS/zipcode_features.pkl")
rf_model_rental_prices = pickle.load( open( "Models/rf_rental_prices.pkl", "rb" ) )

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# load pickle of random forest model


list_of_woningtypes = ['Appartement', 'Benedenwoning', 'benedenwoning + bovenwoning',
                       'Boerderij', 'Bovenwoning', 'Dubbele bovenwoning', 'Eengezinswoning',
                       'Eenvoudige woning', 'Geschakelde woning', 'Grachtenpand',
                       'Herenhuis', 'Hoekwoning', 'Kamer', 'Landhuis', 'Maisonette',
                       'Penthouse', 'Serviceflat', 'Studio', 'Tussenwoning',
                       'Twee onder kap', 'Villa', 'Vrijstaande woning', 'Woning',
                       'Woon-/winkelpand', 'Woonboerderij', 'Woonboot']
app.layout = html.Div([
    html.H6("Huurprijsindicatie"),
    html.Div(["Postcode: ", dcc.Input(id='zipcode_number', placeholder='1234', style={'width': 60} ),
                           dcc.Input(id='zipcode_letters', placeholder='AB', style={'width': 40 } ),
             html.Span( id='municipality', children=' Nederland')]
             ),
    html.Div([dcc.Textarea(id='long_description', value='', placeholder='Kopieer hier de woningomschrijving',
                           style={'width': 600, 'height': 300})]),
    html.Br(),
    html.Div(['Woningtype: ',
              dcc.Dropdown( id='woningtype',
                            options=[{'label': woningtype, 'value': woningtype} for woningtype in list_of_woningtypes],
                            value='Apartement',
                            style={'width': 280, 'display': 'inline-block', 'vertical-align': 'middle'}
             )]),
    html.Div(['Woonoppervlakte: ',
              dcc.Input(id='living_space_m2', value='', style={'width': 60 } ),
              ' m2']),
    html.Div(['Bouwjaar: ',
             dcc.Dropdown( id='construction_year',
                           options=[{'label': construction_year, 'value': construction_year} for construction_year in list(range(1900, 2020))],
                           value='1980',
                           style={'width': 100, 'display': 'inline-block', 'vertical-align': 'middle'}
             )]),
    html.Div(['Aantal kamers: ',
              dcc.Input( id ='aantal_kamers', value='', style={'width': 40 }  )
             ]),
    html.Div(['Aantal slaapkamers: ',
              dcc.Input(id='aantal_slaapkamers', value='', style={'width': 40 } )
              ]),
    html.Div(['Berging: ',
            dcc.Dropdown( id='berging',
                       options=[
                           {'label': 'Ja', 'value': 'Ja'},
                           {'label': 'Nee', 'value': 'Nee'}
                       ],
                       value='Nee',
                       style={'width': 100, 'display': 'inline-block', 'vertical-align': 'middle'}
             )]),
    html.Div(['Balkon: ',
              dcc.Dropdown(id='balkon',
                           options=[
                               {'label': 'Ja', 'value': 'Ja'},
                               {'label': 'Nee', 'value': 'Nee'}
                           ],
                           value='Nee',
                           style={'width': 100, 'display': 'inline-block', 'vertical-align': 'middle'}
                           )]),
    html.Div(['Garage: ',
              dcc.Dropdown(id='garage',
                           options=[
                               {'label': 'Ja', 'value': 'Ja'},
                               {'label': 'Nee', 'value': 'Nee'}
                           ],
                           value='Nee',
                           style={'width': 100, 'display': 'inline-block', 'vertical-align': 'middle'}
                           )]),
    html.Div(['Tweede badkamer: ',
              dcc.Dropdown(id='tweede_badkamer',
                        options=[
                            {'label': 'Ja', 'value': 'Ja'},
                            {'label': 'Nee', 'value': 'Nee'}
                        ],
                        value='Nee',
                        style={'width': 100, 'display': 'inline-block', 'vertical-align': 'middle'}
            )]),
    html.Div(['Aantal tuinen: ',
              dcc.Dropdown(
                  id='aantal_tuinen',
                   options=[
                       {'label': '0', 'value': '0'},
                       {'label': '1', 'value': '1'},
                       {'label': '2', 'value': '2'}
                   ],
                   value = '0',
                  style={'width': 100, 'display': 'inline-block', 'vertical-align': 'middle'}
              )]),
    html.Div(['Dakterras: ',
              dcc.Dropdown(id='dakterras',
                           options=[
                               {'label': 'Ja', 'value': 'Ja'},
                               {'label': 'Nee', 'value': 'Nee'}
                           ],
                           value='Nee',
                           style={'width': 100, 'display': 'inline-block', 'vertical-align': 'middle'}
            )]),
    html.Div([html.Button('Huurprijsindicatie',
                          id='predict_rental_price',
                          style={'background-color': '#267356', 'color': '#FFF'})]),
    html.Br(),
    html.Span(id ='rental_price_prediction', children='<Hier komt de huurprijsindicatie>')
])

@app.callback(
    Output(component_id='berging', component_property='value'),
    [Input(component_id='long_description', component_property='value')]
)
def update_berging_value(long_description):
    bool_result = features_from_description.extract_berging_feature_from_long_description(long_description)
    if(bool_result == True):
        return 'Ja'
    else:
        return 'Nee'

@app.callback(
    Output(component_id='tweede_badkamer', component_property='value'),
    [Input(component_id='long_description', component_property='value')]
)
def update_tweede_badkamer_value(long_description):
    bool_result = features_from_description.extract_tweede_badkamer_feature_from_long_description(long_description)
    if(bool_result == True):
        return 'Ja'
    else:
        return 'Nee'

@app.callback(
    Output(component_id='aantal_tuinen', component_property='value'),
    [Input(component_id='long_description', component_property='value')]
)
def update_aantal_tuinen_value(long_description):
    result = features_from_description.extract_aantal_tuinen_feature_from_long_description(long_description)
    return result

@app.callback(
    Output(component_id='dakterras', component_property='value'),
    [Input(component_id='long_description', component_property='value')]
)
def update_dakterras_value(long_description):
    bool_result = features_from_description.extract_dakterras_feature_from_long_description(long_description)
    if(bool_result == True):
        return 'Ja'
    else:
        return 'Nee'

@app.callback(
    Output(component_id='municipality', component_property='children'),
    [Input(component_id='zipcode_number', component_property='value'), Input(component_id='zipcode_letters', component_property='value')]
)
def update_zipcode_info(zipcode_number, zipcode_letters):
    if( ( zipcode_number is None ) | ( zipcode_letters is None ) ):
        return "Nederland"

    if( (len(zipcode_number) != 4) | ( len(zipcode_letters) != 2) ):
        return "Nederland"

    zipcode = ( str(zipcode_number) + str(zipcode_letters) ).upper()
    municipality = features_from_zipcode.zipcode_to_municipality(zipcode, zipcode_features_df)
    income = features_from_zipcode.zipcode_to_income(zipcode, zipcode_features_df)

    return municipality + " (gem. besteedbare inkomen in postcode is " + str(income) + ")"

@app.callback(Output('rental_price_prediction', 'children'), [Input('predict_rental_price', 'n_clicks')],
              [State('aantal_slaapkamers', 'value'),
               State('aantal_kamers', 'value'),
               State('woningtype', 'value'),
               State('living_space_m2', 'value'),
               State('construction_year', 'value'),
               State('zipcode_number', 'value'),
               State('zipcode_letters', 'value'),
               State('aantal_tuinen', 'value'),
               State('balkon', 'value'),
               State('garage', 'value'),
               State('berging', 'value')
               ])
def on_click_huurprijsindicatie(n_button_clicks, aantal_slaapkamers, aantal_kamers, woningtype, living_space_m2,
                                construction_year, zipcode_number, zipcode_letters, aantal_tuinen,
                                balkon, garage, berging):
    if n_button_clicks is None:
        return '<Hier komt de huurprijsindicatie>'

    zipcode = ( str(zipcode_number) + str(zipcode_letters) ).upper()
    municipality = features_from_zipcode.zipcode_to_municipality(zipcode, zipcode_features_df)
    income = features_from_zipcode.zipcode_to_income(zipcode, zipcode_features_df)

    if(int(aantal_tuinen) > 0 ):
        has_tuin = "Ja"
    else:
        has_tuin = "Nee"

    features_list = { 'slaapkamers': int(aantal_slaapkamers), 'kamers': int(aantal_kamers),
                      'type': woningtype.lower(), 'woonoppervlakte': int(living_space_m2),
                      'bouwjaar': int(construction_year), 'plaats': municipality.lower(),
                      'median_income': int(income), 'tuin': has_tuin,
                      'balkon': balkon, 'garage': garage, 'berging': berging,
                      'treinstation': 500, 'middelbare_school': 500, 'supermarkt': 200, 'basisschool': 500}

    return rental_price_rf.predict_rental_price(rf_model_rental_prices, features_list)

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=True)