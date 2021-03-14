#Todo: voor gemeubileerd zoeken op begin van string, omdat anders 'ongemeubileerd' meekomt

import re

def extract_zipcode_feature_from_long_description(long_description):
    regex_pattern = "[1-9][0-9]{3} ?(?!sa|sd|ss)[a-z]{2} "
    matches = re.findall(regex_pattern, long_description, re.IGNORECASE)

    if(len(matches) > 0):
        zipcode = matches[0].replace(" ", "")
        return (zipcode[0:4], zipcode[4:6].upper())
    else:
        return ("", "")

def extract_woonoppervlakte_from_long_description(long_description):
    regex_pattern = "([0-9]+) (m2|m²|vierkante meter)"
    matches = re.findall(regex_pattern, long_description, re.IGNORECASE)

    if(len(matches) > 0):
        return matches[0][0]

    return ""

def extract_kamers_from_long_description(long_description):
    regex_pattern = "([0-9]+)(kamer|-kamer)"
    matches = re.findall(regex_pattern, long_description.replace("\n", "").replace(" ", ""), re.IGNORECASE)

    if(len(matches) > 0):
        return matches[0][0]

    return ""

def extract_bouwjaar_from_long_description(long_description):
    regex_pattern = "([0-9]+)bouwjaar"
    matches = re.findall(regex_pattern, long_description.replace("\n", "").replace(" ", ""), re.IGNORECASE)

    if(len(matches) > 0):
        return int(matches[0])

    return ""

#Todo: tussen het getal en slaapkamer mag 1 woord staan (ruime)
def extract_slaapkamers_from_long_description(long_description):
    regex_pattern = "([0-9]) (slaapkamer|ruime slaapkamer|kleine slaapkamer|royale slaapkamer)"
    matches = re.findall(regex_pattern, long_description, re.IGNORECASE)

    if(len(matches) > 0):
        return matches[0][0]

    return ""

def extract_berging_feature_from_long_description(long_description):
    search_for_strings = [ 'berging', 'bergruimte']
    regex_pattern = "(" + "|".join(search_for_strings) + ")"

    long_description_contains_feature = bool(re.search(regex_pattern, long_description.lower()))
    return long_description_contains_feature

def extract_balkon_feature_from_long_description(long_description):
    search_for_strings = ['balkon']
    regex_pattern = "(" + "|".join(search_for_strings) + ")"

    long_description_contains_feature = bool(re.search(regex_pattern, long_description.lower()))
    return long_description_contains_feature

def extract_tweede_badkamer_feature_from_long_description(long_description):
    search_for_strings = [ 'badkamers', 'tweede badkamer']
    regex_pattern = "(" + "|".join(search_for_strings) + ")"

    long_description_contains_feature = bool(re.search(regex_pattern, long_description.lower()))
    return long_description_contains_feature

def extract_kelder_feature_from_long_description(long_description):
    search_for_strings = [ 'kelder']
    regex_pattern = "(" + "|".join(search_for_strings) + ")"

    long_description_contains_feature = bool(re.search(regex_pattern, long_description.lower()))
    return long_description_contains_feature

def extract_dakterras_feature_from_long_description(long_description):
    search_for_strings = [ 'dakterras', 'terras' ]
    regex_pattern = "(" + "|".join(search_for_strings) + ")"

    long_description_contains_feature = bool(re.search(regex_pattern, long_description.lower()))
    return long_description_contains_feature

def extract_garage_feature_from_long_description(long_description):
    search_for_strings = [ 'garage', 'parkeerplaats' ]
    regex_pattern = "(" + "|".join(search_for_strings) + ")"

    long_description_contains_feature = bool(re.search(regex_pattern, long_description.lower()))
    return long_description_contains_feature

def extract_aantal_tuinen_feature_from_long_description(long_description):
    #voortuin EN achtertuin or tweede tuin or twee tuinen
    regex_pattern_two_gardens = "(?=.*voortuin)(?=.*achtertuin)|(tweede tuin|tuinen)"
    regex_pattern_one_garden = "tuin"
    long_description_contains_two_gardens = bool(re.search(regex_pattern_two_gardens, long_description.lower()))
    long_description_contains_atleast_one_garden = bool(re.search(regex_pattern_one_garden, long_description.lower()))

    if long_description_contains_two_gardens:
        return '2'
    elif long_description_contains_atleast_one_garden:
        return '1'
    else:
        return '0'

def predict_rental_price(feature_list):
    return feature_list['type'] + " " + feature_list['plaats'] + " " + str(int(feature_list[ 'slaapkamers']) * int(feature_list[ 'kamers' ]))