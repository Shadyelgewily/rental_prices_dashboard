#Todo: extras (berging, schuur etc.) multisellect
#Todo: https://blog.jverkamp.com/2015/04/03/performance-problems-with-flask-and-docker/
#Todo: Restrict locations based on city (only allow cities that have been trained)
#Todo: sanity checks model (met tuin prijs is goedkoper dan zonder tuin etc.; zelfde geldt voor garage)
#Todo: studios met tuin komen niet vaak voor, dus dan kan het voorkomen dat de voorspelling een lagere huurprijs oplevert dan zonder tuin
#Todo: bouwjaar is erg gevoelig, kan bijvoorbeeld komen door weinig observaties of dat die observaties toevallig monumenten zijn (kan misschien beter opgedeeld worden in 5 periodes)
#Todo: feature achterom
#Todo: als je iets kopieert in de omschrijving eerst weer alle waarden resetten
#Todo: monument ja/nee
#Todo: Geen tuin is soms hoger dan wel een tuin
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from sklearn.model_selection import ShuffleSplit

from extract_features import features_from_description
from extract_features import features_from_zipcode
from rental_price_models import rental_price_rf

import pandas as pd
import pickle

external_stylesheets = [dbc.themes.LUX]

#Todo: impute missing values with median income
zipcode_features_df =  pd.read_pickle("Data/CBS/zipcode_features.pkl")
rf_model_rental_prices = pickle.load( open( "Models/rf_rental_prices.pkl", "rb" ) )

list_of_woningtypes = ['Appartement', 'Benedenwoning', 'benedenwoning + bovenwoning',
                       'Boerderij', 'Bovenwoning', 'Dubbele bovenwoning', 'Eengezinswoning',
                       'Eenvoudige woning', 'Geschakelde woning', 'Grachtenpand',
                       'Herenhuis', 'Hoekwoning', 'Kamer', 'Landhuis', 'Maisonette',
                       'Penthouse', 'Serviceflat', 'Studio', 'Tussenwoning',
                       'Twee onder kap', 'Villa', 'Vrijstaande woning',
                       'Woon-/winkelpand', 'Woonboerderij', 'Woonboot']

#Todo: ook gemiddelde prijs berekenen per gemeente
#Todo: Met 80, 90, 95% zekerheid confidence intervals gebaseerd op quantiles van average error
#Todo: multiple callbacks
#Todo: checken of perceeloppervlakte niet de m2 verpest

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Page 1", href="#")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("More pages", header=True),
                dbc.DropdownMenuItem("Page 2", href="#"),
                dbc.DropdownMenuItem("Page 3", href="#"),
            ],
            nav=True,
            in_navbar=True,
            label="More",
        ),
    ],
    brand="Point Forecast Consultancy",
    brand_href="http://www.pointforecastconsultancy.nl",
    color="info",
    dark=True,
)

omschrijving_card = dbc.Card([
    dbc.FormGroup(
                [
                    dbc.Label("Omschrijving van de woning", style={'font-weight': 'bold'}),
                    dcc.Textarea(id='long_description', value='',
                                 placeholder='Kopieer de omschrijving van de woning (van bijvoorbeeld Pararius). '
                                             'De meeste eigenschappen van de woning worden automatisch afgelezen uit de tekst en aan de rechterkant voor je ingevuld.',
                                 style={'width': 600, 'height': 300}),
                ]
            ),
    dbc.FormGroup(
        [dbc.Row(
            [dbc.Col(html.Div(dbc.Button("Bereken", color="primary", id="predict_rental_price", className="mr-1"),
                              style={'textAlign': 'center'}))]
        ),
        dbc.Row([html.Br(), html.Br()]),
        dbc.Row(
            dbc.Col(
                html.Div([html.H4(id='rental_price_prediction', className='text-info')], style={'textAlign': 'center'})
            )
        )]
    )],
    body=True
)

eigenschappen_card = dbc.Card([
    dbc.FormGroup([
        dbc.Label("Postcode: ", style={'font-weight': 'bold'}),
        dcc.Input(id='zipcode_number', placeholder='1234', style={'width': 60} ),
        dcc.Input(id='zipcode_letters', placeholder='AB', style={'width': 40 } ),
        html.Span( id='municipality', children=' Nederland')
    ]),
    dbc.FormGroup([
            dbc.Label("Type woning", style={'font-weight': 'bold'}),
            dcc.Dropdown(id='woningtype',
                          options=[{'label': woningtype, 'value': woningtype} for woningtype in list_of_woningtypes],
                          placeholder='Selecteer...')
        ]),
    dbc.FormGroup([
        dbc.Label("Bouwjaar: ", style={'font-weight': 'bold'}),
        dcc.Dropdown(id='construction_year',
                     options=[{'label': construction_year, 'value': construction_year} for construction_year in
                              list(range(1860, 2020))],
                     placeholder='Selecteer...',
                     style={'width': 150, 'display': 'inline-block', 'vertical-align': 'middle'})
    ]),
    dbc.FormGroup([
        dbc.Label("Woonoppervlakte: ", style={'font-weight': 'bold'}),
        dcc.Input(id='living_space_m2', value='', style={'width': 40}),' m2'
    ]),
    dbc.FormGroup([
        dbc.Label("Aantal kamers: ", style={'font-weight': 'bold'}),
        dcc.Input(id ='aantal_kamers', value='', style={'width': 40 })
     ]),
    dbc.FormGroup([
        dbc.Label("Waarvan slaapkamers: ", style={'font-weight': 'bold'}),
        dcc.Input(id='aantal_slaapkamers', value='', style={'width': 40})
    ]),
    dbc.FormGroup([dbc.Label("Berging of schuur: ", style={'font-weight': 'bold'}),
        dcc.Dropdown(id='berging',
                   options=[
                       {'label': 'Nee', 'value': 'Nee'},
                       {'label': 'Ja', 'value': 'Ja'}
                   ],
                   placeholder='Selecteer...',
                   style={'width': 150, 'display': 'inline-block', 'verticalAlign': 'middle'})
    ]),
    dbc.FormGroup([dbc.Label("Balkon: ", style={'font-weight': 'bold'}),
       dcc.Dropdown(id='balkon',
                    options=[
                        {'label': 'Nee', 'value': 'Nee'},
                        {'label': 'Ja', 'value': 'Ja'}
                    ],
                    placeholder='Selecteer...',
                    style={'width': 150, 'display': 'inline-block', 'verticalAlign': 'middle'})
       ]),
    dbc.FormGroup([dbc.Label("Garage of parkeerplaats: ", style={'font-weight': 'bold'}),
                   dcc.Dropdown(id='garage',
                                options=[
                                    {'label': 'Nee', 'value': 'Nee'},
                                    {'label': 'Ja', 'value': 'Ja'}
                                ],
                                placeholder='Selecteer...',
                                style={'width': 150, 'display': 'inline-block', 'verticalAlign': 'middle'})
                   ]),
    dbc.FormGroup([dbc.Label("Tweede toilet of badkamer: ", style={'font-weight': 'bold'}),
                   dcc.Dropdown(id='tweede_badkamer',
                                options=[
                                    {'label': 'Nee', 'value': 'Nee'},
                                    {'label': 'Ja', 'value': 'Ja'}
                                ],
                                placeholder='Selecteer...',
                                style={'width': 150, 'display': 'inline-block', 'verticalAlign': 'middle'})
                   ]),
    dbc.FormGroup([dbc.Label("Aantal tuinen: ", style={'font-weight': 'bold'}),
              dcc.Dropdown(
                  id='aantal_tuinen',
                  options=[
                      {'label': '0', 'value': '0'},
                      {'label': '1', 'value': '1'},
                      {'label': '2', 'value': '2'}
                  ],
                  value='0',
                  placeholder='Selecteer...',
                  style={'width': 150, 'display': 'inline-block', 'vertical-align': 'middle'}
              )]),
    dbc.FormGroup([dbc.Label("(Dak)terras: ", style={'font-weight': 'bold'}),
                   dcc.Dropdown(id='dakterras',
                                options=[
                                    {'label': 'Nee', 'value': 'Nee'},
                                    {'label': 'Ja', 'value': 'Ja'}
                                ],
                                placeholder='Selecteer...',
                                style={'width': 150, 'display': 'inline-block', 'verticalAlign': 'middle'})
                   ]),
],

    body=True
)

app.layout = html.Div([
    html.Div(navbar),
    dbc.Container([
    html.Div(
    [
        dbc.Row(html.Br()),
        dbc.Row(dbc.Col(html.Div(html.H1('Huurprijs Indicator'), style={'textAlign': 'center'}))),
        dbc.Row(dbc.Col(html.Div([html.P("Met deze app kun je op een razendsnelle manier checken wat de geschatte huurprijs is van een woning. "
                                        "De voorgestelde huurprijs is gebaseerd op een AI model die een voorspelling maakt aan de hand van historische prijzen van vergelijkbare woningen."),
                                 html.P(["Kopieer de omschrijving van de woning, check of alle velden aan de rechterkant goed zijn ingevuld en klik op 'Bereken'.",
                                        html.Br(),html.Br(),
                                        dcc.Markdown("*Let op: Aan de voorgestelde huurprijzen kunnen geen rechten worden ontleend.*")])
                                 ]))),
        dbc.Row(
            [
                dbc.Col(omschrijving_card),
                dbc.Col(eigenschappen_card),
            ]
        ),
    ])
])
])
@app.callback(
    Output(component_id='woningtype', component_property='value'),
    [Input(component_id='long_description', component_property='value')]
)
def update_berging_value(long_description):
    return features_from_description.extract_woning_type_from_long_description(long_description, list_of_woningtypes)

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
    Output(component_id='zipcode_number', component_property='value'),
    [Input(component_id='long_description', component_property='value')]
)
def update_zipcode_number_value(long_description):
    return features_from_description.extract_zipcode_feature_from_long_description(long_description)[0]

@app.callback(
    Output(component_id='zipcode_letters', component_property='value'),
    [Input(component_id='long_description', component_property='value')]
)
def update_zipcode_number_value(long_description):
    return features_from_description.extract_zipcode_feature_from_long_description(long_description)[1]

@app.callback(
    Output(component_id='living_space_m2', component_property='value'),
    [Input(component_id='long_description', component_property='value')]
)
def update_woonoppervlakte_value(long_description):
    return features_from_description.extract_woonoppervlakte_from_long_description(long_description)

@app.callback(
    Output(component_id='aantal_slaapkamers', component_property='value'),
    [Input(component_id='long_description', component_property='value')]
)
def update_slaapkamers_value(long_description):
    return features_from_description.extract_slaapkamers_from_long_description(long_description)

@app.callback(
    Output(component_id='aantal_kamers', component_property='value'),
    [Input(component_id='long_description', component_property='value')]
)
def update_kamers_value(long_description):
    return features_from_description.extract_kamers_from_long_description(long_description)

@app.callback(
    Output(component_id='construction_year', component_property='value'),
    [Input(component_id='long_description', component_property='value')]
)
def update_bouwjaar_value(long_description):
    return features_from_description.extract_bouwjaar_from_long_description(long_description)

@app.callback(
    Output(component_id='balkon', component_property='value'),
    [Input(component_id='long_description', component_property='value')]
)
def update_balkon_value(long_description):
    bool_result = features_from_description.extract_balkon_feature_from_long_description(long_description)
    if (bool_result == True):
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
    Output(component_id='garage', component_property='value'),
    [Input(component_id='long_description', component_property='value')]
)
def update_garage_value(long_description):
    bool_result = features_from_description.extract_garage_feature_from_long_description(long_description)
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

    return municipality

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
        return ''

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
                      'treinstation': 6000, 'middelbare_school': 700, 'supermarkt': 130, 'basisschool': 800}

    return rental_price_rf.predict_rental_price(rf_model_rental_prices, features_list)

if __name__ == '__main__':
    app.title = 'Huurprijs Indicator'
    app.run_server(host='0.0.0.0', debug=True)