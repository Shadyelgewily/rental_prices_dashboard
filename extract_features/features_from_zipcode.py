import pandas as pd
import math

#To do: add loging and timing using decorators

def merge_raw_data_and_save_zipcode_and_municipality():
    zipcodes_with_merge_IDs = pd.read_csv("Data/Raw/CBS/pc6hnr20190801_gwb.csv", sep=";")
    zipcodes_with_merge_IDs.drop('Huisnummer', axis=1, inplace=True)
    zipcodes_with_merge_IDs.drop_duplicates(inplace=True)
    zipcodes_with_merge_IDs['Zipcode_numeric' ] = zipcodes_with_merge_IDs['PC6'].str.slice(0,4).astype(int)

    municipalities = pd.read_csv("Data/Raw/CBS/gem2019.csv", sep=";")
    zipcode_income_info = pd.read_csv( "Data/CBS/median_spendable_income.csv")

    #Merge with municipality info
    zipcode_features = pd.merge(left=zipcodes_with_merge_IDs, right=municipalities, left_on='Gemeente2019',
                                           right_on='Gemcode2019')
    zipcode_features.rename(columns={"PC6": "Zipcode", "Gemeentenaam2019": "Municipality"}, inplace=True)

    #Merge with income info
    zipcode_features = pd.merge(left = zipcode_features, right = zipcode_income_info, left_on = "Zipcode_numeric", right_on = "zipcode_numeric")

    zipcode_features = zipcode_features[['Zipcode', 'Municipality', 'median_income']]
    zipcode_features.set_index("Zipcode", inplace=True)

    zipcode_features.to_pickle('Data/CBS/zipcode_features.pkl')

    return True


def zipcode_to_municipality(zipcode, zipcode_features_df):
    try:
        municipality = zipcode_features_df.loc[zipcode, 'Municipality']
    except KeyError:
        municipality = 'Nederland'
    finally:
        return municipality

#Allternatives: https://opendata.cbs.nl/statline/#/CBS/nl/dataset/83765NED/table?fromstatweb
def zipcode_to_income(zipcode, zipcode_features_df):
    income = zipcode_features_df.loc[zipcode, 'median_income']

    if math.isnan(income):
        income = zipcode_features_df['median_income'].mean()

    return round(income)

def read_and_save_trainstations_NL():
    pass

#Belangrijk dat de features getrained worden op consistente afstanden, dus ipv de gescrapede features van Jaap ook deze berekenen
#in elk geval voor de multiplicatiefactor en validatie
def distance_zipcode_to_closest_station():
    #Foreach station in city...
    #https://www.afstandberekenen.nl/widget?from=3844kj&to=station%hilversum&calculate=1
    #https://api.postcode.nl/documentation/nl/v1/Address/viewByLatLon
    pass

def distance_to_closest_school():
    #https://www.afstandberekenen.nl/widget?from=3844kj&to=station%hilversum&calculate=1
    pass