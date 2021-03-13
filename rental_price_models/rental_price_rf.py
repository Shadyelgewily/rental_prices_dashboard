from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, KBinsDiscretizer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.model_selection import cross_val_score
from sklearn.inspection import permutation_importance
import matplotlib.pyplot as plt

import dash_table
from training_and_test_data import jaap_data
import pandas as pd
import pickle

RF_INDEPENDENT_VARS_NUMERIC = ["woonoppervlakte", "treinstation", "middelbare_school",
                      "supermarkt", "basisschool", "median_income", "slaapkamers", "kamers"]
RF_INDEPENDENT_VARS_STRING = [ "type", "tuin", "balkon", "garage", "plaats"]
RF_DEPENDENT_VAR = ["price"]

def select_complete_obs_jaap_data():
    jaap_df = jaap_data.tmp_read_jaap_data()
    relevant_features = (RF_DEPENDENT_VAR + RF_INDEPENDENT_VARS_NUMERIC + RF_INDEPENDENT_VARS_STRING )
    jaap_df = jaap_df[[c for c in jaap_df.columns if c in relevant_features ]]
    jaap_df.dropna(axis=0, inplace=True)
    jaap_df['tuin'].replace(['VoorAchter', 'VoorAchterZijkant', 'AchterZijkant', 'Achter', 'Zijkant', 'Voor'], ['Ja', 'Ja', 'Ja', 'Ja', 'Ja', 'Ja'], inplace=True)

    #Filter categorical variables tuin
    return(jaap_df)

def encode_rf_string_to_dummy(jaap_df):

    return( pd.get_dummies(jaap_df, drop_first = True) )

def fit_rf_rental_prices():
    jaap_df = select_complete_obs_jaap_data()
    X = jaap_df.drop(RF_DEPENDENT_VAR, axis=1, inplace=False)
    y = jaap_df[RF_DEPENDENT_VAR].values.ravel()

    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state = 555)

    preprocessor = ColumnTransformer([('cat', OneHotEncoder(dtype='int', handle_unknown='ignore'), RF_INDEPENDENT_VARS_STRING ),
                                      ('discr', KBinsDiscretizer(encode='onehot', strategy='uniform'), [ 'median_income', 'middelbare_school', 'supermarkt'])
                                      ], remainder='passthrough')

    rf_regression = RandomForestRegressor(random_state=555, oob_score = True, n_estimators = 200)

    grid_search_CV_param_grid = {   'preprocessor__discr__n_bins': [10, 20],
                                    'rf_regression__max_features': ['sqrt'],
                                    'rf_regression__n_estimators': [200]
                                 }

    rf_pipeline = Pipeline(steps=[
                                    ('preprocessor', preprocessor),
                                    ('rf_regression', rf_regression)
                                ])
    #Quite some variation in the CV scores, so this can indicate that more data leads to more stable results (or n_trees => 500)
    #cv_scores =  cross_val_score(rf_pipeline, X_train, y_train, cv = 5, n_jobs = -1)

    grid_search_CV_random_forest = GridSearchCV(estimator = rf_pipeline, param_grid = grid_search_CV_param_grid, cv = 3, n_jobs = 3, verbose = 2)

    grid_search_CV_random_forest.fit(X_train, y_train )
    grid_search_CV_random_forest.score(X_test, y_test)

    #pd.concat([pd.DataFrame(grid_search_CV_random_forest.cv_results_["params"]),
    #           pd.DataFrame(grid_search_CV_random_forest.cv_results_["mean_test_score"], columns=["Accuracy"])], axis=1)


    best_estimator = grid_search_CV_random_forest.best_estimator_
    best_estimator.column_names_training_data_ = X_train.columns

    pickle.dump(best_estimator, open( "Models/rf_rental_prices.pkl", "wb" ) )

    return True

def predict_rental_price(model_obj, features_list):
    feature_df = pd.DataFrame([features_list], columns = model_obj.column_names_training_data_)
    #model_obj.predict(feature_df)

    dt_data = feature_df.to_dict('rows')
    dt_columns = [{"name": i, "id": i,} for i in (feature_df.columns)]
    #return dash_table.DataTable(data=dt_data, columns=dt_columns)

    return "De huurprijsindicatie is: " + str(int(model_obj.predict(feature_df))) + " euro"

def plot_permutation_importance(rf_model, test_X, test_y):
    result = permutation_importance(rf_model, test_X, test_y, n_repeats=10,
                                random_state=4245454, n_jobs=2)
    sorted_idx = result.importances_mean.argsort()

    fig, ax = plt.subplots()
    ax.boxplot(result.importances[sorted_idx].T,
               vert=False, labels=test_X.columns[sorted_idx])
    ax.set_title("Permutation Importances (test set)")
    fig.tight_layout()
    plt.show()