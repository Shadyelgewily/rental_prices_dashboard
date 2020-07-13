from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
import dash_table
from training_and_test_data import jaap_data
import pandas as pd
import pickle

RF_INDEPENDENT_VARS_NUMERIC = ["bouwjaar", "woonoppervlakte", "treinstation", "middelbare_school",
                      "supermarkt", "basisschool", "median_income", "slaapkamers", "kamers"]
RF_INDEPENDENT_VARS_STRING = [ "type", "tuin", "balkon", "garage", "plaats"]
RF_DEPENDENT_VAR = ["price"]

def select_complete_obs_jaap_data():
    jaap_df = jaap_data.tmp_read_jaap_data()
    relevant_features = (RF_DEPENDENT_VAR + RF_INDEPENDENT_VARS_NUMERIC + RF_INDEPENDENT_VARS_STRING )
    jaap_df = jaap_df[[c for c in jaap_df.columns if c in relevant_features ]]
    jaap_df.dropna(axis=0, inplace=True)
    jaap_df['tuin'].replace(['VoorAchter', 'VoorAchterZijkant', 'AchterZijkant', 'Achter'], ['Ja', 'Ja', 'Ja', 'Ja'], inplace=True)

    #Filter categorical variables tuin
    return(jaap_df)

def encode_rf_string_to_dummy(jaap_df):

    return( pd.get_dummies(jaap_df, drop_first = True) )

def fit_rf_rental_prices():
    jaap_df = select_complete_obs_jaap_data()
    X = jaap_df.drop(RF_DEPENDENT_VAR, axis=1, inplace=False)
    y = jaap_df[RF_DEPENDENT_VAR].values.ravel()

    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state = 555)

    dummy_transformer = ColumnTransformer([('cat', OneHotEncoder(dtype='int'), RF_INDEPENDENT_VARS_STRING ) ], remainder='passthrough')

    rf_object = Pipeline(steps=[('preprocessor', dummy_transformer),
                                ('regression', RandomForestRegressor(random_state=555, n_estimators = 100, oob_score = True))
                                ])
    rf_object.fit(X_train, y_train )
    rf_object.score(X_test, y_test)
    rf_object.column_names_training_data_ = X_train.columns

    pickle.dump(rf_object, open( "Models/rf_rental_prices.pkl", "wb" ) )

    return True

def predict_rental_price(model_obj, features_list):
    feature_df = pd.DataFrame([features_list], columns = model_obj.column_names_training_data_)
    #model_obj.predict(feature_df)

    dt_data = feature_df.to_dict('rows')
    dt_columns = [{"name": i, "id": i,} for i in (feature_df.columns)]
    #return dash_table.DataTable(data=dt_data, columns=dt_columns)

    return "De huurprijsindicatie is: " + str(int(model_obj.predict(feature_df))) + " euro"
