from bs4 import BeautifulSoup
import requests
import re
import os
import csv
import sqlite3
import json
import sys
import atexit
from os import path
from json import dumps, loads

def read_counter():
    """Finds the number of times the code has been executing by reading the counter.json file"""

    return loads(open("counter.json", "r").read()) + 1 if path.exists("counter.json") else 0

def write_counter():
    """Updates the number of times the code has been executing by writing into the counter.json file"""

    with open("counter.json", "w") as f:
        f.write(dumps(counter))

#Reads and updates execution counter. Needed outside of main()
counter = read_counter()
atexit.register(write_counter)

def get_stateDict(state):
    """Takes in a state name as a string and returns a dictionary of COVID info on that state from a unique API URL link."""

    stateIntitals = {
        'Alabama': 'AL',
        'Alaska': 'AK',
        'American_Samoa': 'AS',
        'Arizona': 'AZ',
        'Arkansas': 'AR',
        'California': 'CA',
        'Colorado': 'CO',
        'Connecticut': 'CT',
        'Delaware': 'DE',
        'District_of_Columbia': 'DC',
        'Florida': 'FL',
        'Georgia': 'GA',
        'Guam': 'GU',
        'Hawaii': 'HI',
        'Idaho': 'ID',
        'Illinois': 'IL',
        'Indiana': 'IN',
        'Iowa': 'IA',
        'Kansas': 'KS',
        'Kentucky': 'KY',
        'Louisiana': 'LA',
        'Maine': 'ME',
        'Maryland': 'MD',
        'Massachusetts': 'MA',
        'Michigan': 'MI',
        'Minnesota': 'MN',
        'Mississippi': 'MS',
        'Missouri': 'MO',
        'Montana': 'MT',
        'Nebraska': 'NE',
        'Nevada': 'NV',
        'New_Hampshire': 'NH',
        'New_Jersey': 'NJ',
        'New_Mexico': 'NM',
        'New_York': 'NY',
        'North_Carolina': 'NC',
        'North_Dakota': 'ND',
        'Northern_Mariana_Islands':'MP',
        'Ohio': 'OH',
        'Oklahoma': 'OK',
        'Oregon': 'OR',
        'Pennsylvania': 'PA',
        'Puerto_Rico': 'PR',
        'Rhode_Island': 'RI',
        'South_Carolina': 'SC',
        'South_Dakota': 'SD',
        'Tennessee': 'TN',
        'Texas': 'TX',
        'Utah': 'UT',
        'Vermont': 'VT',
        'Virgin_Islands': 'VI',
        'Virginia': 'VA',
        'Washington': 'WA',
        'West_Virginia': 'WV',
        'Wisconsin': 'WI',
        'Wyoming': 'WY'}

    stateInitial = stateIntitals.get(state)
    state_api = f'https://api.covidactnow.org/v2/county/{stateInitial}.json?apiKey=76735e187ac1425dab4bba7aaaa46d09'
    state_response = requests.get(state_api)
    stateDict= state_response.json()
    return stateDict

def get_websiteLinks(state):

    """Takes in a state name as a string. Returns a list of county URL links as strings in alphabetical order for a certain state."""

    modifiedState = state.replace("_", "-")
    finalState = modifiedState.title()
    base_url = f'https://us-places.com/' + finalState + '/' + finalState + '.htm'
    r = requests.get(base_url)
    soup = BeautifulSoup(r.text, 'html.parser')

    dropDownTag = soup.find("select")
    optionTags = dropDownTag.find_all("option")[1:]

    dict = {}
    for optionTag in optionTags:
        websiteEnding = optionTag.get("value")
        fullName = optionTag.text 
        fullNameList = fullName.split("-")
        if len(fullNameList) ==2:
            countyName = fullNameList[1].strip()
        else:
            countyName = fullNameList[0].strip()
        dict[countyName] = websiteEnding
   
    sortedCounties = sorted(dict.items(), key = lambda x: x[0])

    websiteLinks = []
    for countyTuple in sortedCounties:
        full_url = "https://us-places.com" + countyTuple[1]
        websiteLinks.append(full_url)

    return websiteLinks

def get_countyNames(state):
    """Takes in a state name as a string. Returns a list of county names as strings in alphabetical order for a certain state."""

    modifiedState = state.replace("_", "-")
    finalState = modifiedState.title()
    base_url = f'https://us-places.com/' + finalState + '/' + finalState + '.htm'
    r = requests.get(base_url)
    soup = BeautifulSoup(r.text, 'html.parser')

    dropDownTag = soup.find("select")
    optionTags = dropDownTag.find_all("option")[1:]
    countyNames = []
    for optionTag in optionTags:
        fullName = optionTag.text 
        fullNameList = fullName.split("-")
        if len(fullNameList) ==2:
            countyNames.append(fullNameList[1].strip())
        else:
            countyNames.append(fullNameList[0].strip())

    return sorted(countyNames)

def get_populations(state):

    """Takes in a state name as a string. Returns a dictionary with the keys being county names 
        and the values being the population for each county in the state."""
    
    populations = {}
    websiteLinks = get_websiteLinks(state)
    counties = get_countyNames(state)
    county_index = 0

    for websiteLink in websiteLinks:
        r = requests.get(websiteLink)
        soup = BeautifulSoup(r.text, 'html.parser')

        try:
            fullContentText = soup.find("div", id="content").text
            fullContentWOCommas = fullContentText.replace(",", "")
            population = re.findall(r'Population: (\d+)A', fullContentWOCommas)[0]
            populations[counties[county_index]] = int(population)
            county_index += 1
        except:
            fixedStateName = state.replace("_", " ")
            print(f'Unfortunately, {fixedStateName} is missing information on certain counties and therefore we are unable to continue the program. Re-run the program and choose a different state.')
            sys.exit()
    
    return populations


def get_povertyRates(state):

    """Takes in a state name as a string. Returns a dictionary with the keys being county names
        and the values being the poverty rate for each county in the state."""

    povertyRates = {}
    websiteLinks = get_websiteLinks(state)
    counties = get_countyNames(state)
    county_index = 0

    for websiteLink in websiteLinks:
        r = requests.get(websiteLink)
        soup = BeautifulSoup(r.text, 'html.parser')

        fullContentText = soup.find("div", id="content").text
        povertyRate = re.findall(r'poverty: (\d+.\d+)%', fullContentText)[0]
        povertyRates[counties[county_index]] = round(float(povertyRate)/100,3)
        county_index += 1
    
    return povertyRates

def get_covidNumberCases(state_dic):

    """Utilizes the entire state_dic from the API to grab the number of positive COVID cases per county. 
            Returns a dict with keys as county names and values as COVID case numbers."""

    covidNumberCases = {}

    for dic in state_dic:
        county = dic['county']
        covidNumber = dic["actuals"]["cases"]
        covidNumberCases[county] = [covidNumber]
    
    return covidNumberCases

def get_covidDeaths(state_dic):
    """Utilizes the entire state dic from the API to grab the number of COVID deaths per county. 
            Returns a dictionary with keys as county names and values as COVID death counts."""

    covidDeaths = {}

    for dic in state_dic:
        county = dic['county']
        covidDeathCount = dic["actuals"]["deaths"]
        covidDeaths[county] = [covidDeathCount]
    
    return covidDeaths


def setUpDatabase(db_name):

    """Takes the name of a database, a string, as an input. Returns the cursor and connection to the database."""

    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def set_up_tables(state1, state2, cur, conn):

    """Takes in the database cursor, connection, and two state names as strings. 
           Sets up three tables for each of the two states passed. The tables include a county name table, 
           a demographic table, and a COVID information table."""

    cur.execute(f'CREATE TABLE IF NOT EXISTS {state1}CountyNames (countyID INTEGER PRIMARY KEY, countyName TEXT)')
    cur.execute(f'CREATE TABLE IF NOT EXISTS {state1}Demographics (countyID INTEGER PRIMARY KEY, population INTEGER, povertyRate FLOAT)')
    cur.execute(f'CREATE TABLE IF NOT EXISTS {state1}CovidInfo (countyID INTEGER PRIMARY KEY, covidNumberCases INTEGER, covidDeaths INTEGER)')

    cur.execute(f'CREATE TABLE IF NOT EXISTS {state2}CountyNames (countyID INTEGER PRIMARY KEY, countyName TEXT)')
    cur.execute(f'CREATE TABLE IF NOT EXISTS {state2}Demographics (countyID INTEGER PRIMARY KEY, population INTEGER, povertyRate FLOAT)')
    cur.execute(f'CREATE TABLE IF NOT EXISTS {state2}CovidInfo (countyID INTEGER PRIMARY KEY, covidNumberCases INTEGER, covidDeaths INTEGER)')
    conn.commit()

def fill_countyNamesTable(state, cur, conn):

    """Takes in the database cursor, connection, and the state name as a string. 
        Does not return anything. Fills in the passed state’s county name table with all the counties within 
        that state (countyName) along with a countyID INTEGER PRIMARY KEY."""

    state_counties = get_countyNames(state)
    cur.execute(f'SELECT countyID FROM {state}CountyNames')
    starting_point = len(cur.fetchall())
    state_id = 1
    for county in state_counties:
        cur.execute(f'INSERT OR IGNORE INTO {state}CountyNames (countyID, countyName) VALUES (?, ?)', (state_id, county))
        state_id += 1
        cur.execute(f'SELECT countyID FROM {state}CountyNames')
        new_point = len(cur.fetchall())
        if new_point - starting_point >= 25:
            break
    
    conn.commit()

def fill_DemographicTable(state, cur, conn):
  
    """Takes in the database cursor, connection, and the state name as a string. 
        Does not return anything. Fills in the passed state’s county demographic 
        table with countyID, population, and poverty rate."""

    populations = get_populations(state)
    povertyRates = get_povertyRates(state)
    state_counties = get_countyNames(state)

    cur.execute(f'SELECT countyID FROM {state}CountyNames')
    county_names_filled = len(cur.fetchall())
    if len(state_counties) == county_names_filled:

        cur.execute(f'SELECT countyID FROM {state}Demographics')
        starting_point = len(cur.fetchall())

        for county in state_counties:
            population = populations[county]
            povertyRate = povertyRates[county]
            cur.execute(f'SELECT countyID FROM {state}CountyNames WHERE countyName = ?', (county,))
            county_id = int(cur.fetchone()[0])
            cur.execute(f'INSERT OR IGNORE INTO {state}Demographics (countyID, population, povertyRate) VALUES (?, ?, ?)', (county_id, population, povertyRate))
            cur.execute(f'SELECT countyID FROM {state}Demographics')
            new_point = len(cur.fetchall())
            if new_point - starting_point >= 25:
                break

    conn.commit()

def fill_CovidInfoTable(state, cur, conn):

    """Takes in the database cursor, connection, and the state name as a string. 
           Does not return anything. Fills in the passed state’s county COVID info table with 
           countyID, covidNumberCases, and covidDeaths."""

    stateDict = get_stateDict(state)
    covidNumberCases = get_covidNumberCases(stateDict)
    covidDeaths = get_covidDeaths(stateDict)
    state_counties = get_countyNames(state)

    cur.execute(f'SELECT countyID FROM {state}Demographics')
    count_demographics_filled = len(cur.fetchall())
    if count_demographics_filled == len(state_counties):

        cur.execute(f'SELECT countyID FROM {state}CovidInfo')
        starting_point = len(cur.fetchall())

        for county in state_counties:
            covidNumberCasesInsert = covidNumberCases[county + ' County'][0]
            covidDeathsInsert = covidDeaths[county + ' County'][0]
            cur.execute(f'SELECT countyID FROM {state}CountyNames WHERE countyName = ?', (county,))
            county_id = int(cur.fetchone()[0])
            cur.execute(f'INSERT OR IGNORE INTO {state}CovidInfo (countyID, covidNumberCases, covidDeaths) VALUES (?, ?, ?)', (county_id, covidNumberCasesInsert, covidDeathsInsert))
            cur.execute(f'SELECT countyID FROM {state}CovidInfo')
            new_point = len(cur.fetchall())
            if new_point - starting_point >= 25:
                break

    conn.commit()

def get_percentCovidCases(state, cur, conn):

    """Takes in the database cursor, connection, and the state name as a string. 
        Returns a dictionary with keys as county names and the values as percentages 
        of the number of positive COVID cases vs the population (as a floating decimal) for each county in the state."""

    cur.execute(f'SELECT {state}CountyNames.countyName, {state}Demographics.population, {state}CovidInfo.covidNumberCases FROM {state}Demographics JOIN {state}CovidInfo ON {state}Demographics.countyID = {state}CovidInfo.countyID JOIN {state}CountyNames ON {state}CountyNames.countyID = {state}Demographics.countyID')
    results = cur.fetchall()
    
    percentages = {}
    for result in results:
        percentages[result[0]] = result[2]/result[1]
    
    return percentages

def get_percentCovidDeaths(state, cur, conn):

    """Takes in the database cursor, connection, and the state name as a string. 
           Returns a dictionary with keys as county names and the values as percentages 
           of the number of COVID deaths vs the number of positive cases (as a floating decimal) for each county in the state."""

    cur.execute(f'SELECT {state}CountyNames.countyName, {state}Demographics.population, {state}CovidInfo.covidDeaths FROM {state}Demographics JOIN {state}CovidInfo ON {state}Demographics.countyID = {state}CovidInfo.countyID JOIN {state}CountyNames ON {state}CountyNames.countyID = {state}Demographics.countyID')
    results = cur.fetchall()

    percentages = {}
    for result in results:
        percentages[result[0]] = result[2]/result[1]

    return percentages

def write_calculated_data_to_file(filename, state, cur, conn):

    """Takes in the database cursor and connection. Accepts the filename and state name as strings. 
        Opens the file and writes the county, positivity rate, and death rate for each county in the state"""

    path = os.path.dirname(os.path.abspath(__file__)) + os.sep
    write_file = open(path + filename, "w")
    write = csv.writer(write_file, delimiter=",")
    write.writerow(('County',"Positivity Rate","Death Rate"))


    positive_output = get_percentCovidCases(state,cur, conn)
    death_output = get_percentCovidDeaths(state,cur, conn)

    
    for county in positive_output.keys():
        write.writerow((county,positive_output[county], death_output[county]))
    
    write_file.close()

def main():

    """Takes nothing as an input and returns nothing. 
        Ask the user for two state names, sets up the database, and calls fill_countyNamesTable(), 
        fill_DemographicTable(), fill_CovidInfoTable(), and write_calculated_data_to_file for each state. 
        Closes the database connection."""

    cur, conn = setUpDatabase('covidRawData.db')

    #If this is the first time the code is executing, then the first if statement will pass
    #We checked this so that the user wouldn't have to imput which two states they wanted to compare everytime they
    #ran their code to put in 25 more items of data
    if counter == 1:
        input1 = input("Type One State in the US That You Would Like To Compare Covid Info To With Another State (We will Ask For Second State Next): ")
        input2 = input("Type In The Second State You Would Like To Compare: ")
        state1 = input1.replace(" ", "_")
        state2 = input2.replace(" ", "_")
        set_up_tables(state1, state2, cur, conn)
    
    else:
        #To acocount for the user not typing in the state names again, we need to extract the state names from looking 
        #at the titles of tables we already have created
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        lst = cur.fetchall()
        state1Full = lst[0][0]
        state1 = state1Full.split("County")[0]
        state2Full = lst[3][0]
        state2 = state2Full.split("County")[0]

    #Gets the current status of each table for State 1 to compare later to know where to fill the next 25 items
    cur.execute(f'SELECT countyID FROM {state1}CovidInfo')
    state1DatabaseCountyCount = len(cur.fetchall())
    state1ActualCountyCount = len(get_countyNames(state1))
    cur.execute(f'SELECT countyID FROM {state1}CountyNames')
    state1NamesCountyCount = len(cur.fetchall())
    cur.execute(f'SELECT countyID FROM {state1}Demographics')
    state1DemographicsCountyCount = len(cur.fetchall())

    #Checks to see if all rows (counties) are filled into the last table for state 1 (CovidInfo). If there 
    #are less counties in the last table then counties in the actual state then the following if statement will pass
    #to continue filling in the tables for that state.
    if state1DatabaseCountyCount < state1ActualCountyCount:
        fill_countyNamesTable(state1, cur, conn)
        if state1NamesCountyCount == state1ActualCountyCount:
            fill_DemographicTable(state1, cur, conn)
        if state1DemographicsCountyCount == state1ActualCountyCount:
            fill_CovidInfoTable(state1, cur, conn)
        cur.execute(f'SELECT countyID FROM {state1}CovidInfo')
        state1InfoCountyCount = len(cur.fetchall())
        #When all three tables are completed for state 1, the csv file will be created and written into.
        if (state1InfoCountyCount == state1ActualCountyCount):
            csvFile = f'{state1}_covidCalculatedData.csv'
            write_calculated_data_to_file(csvFile,state1, cur, conn)
            print("Done writing tables for state 1. Run code again to start filling tables for state 2")
        else:
            print('Run code again to keep filling the Database.')
    

    #Gets the current status of each table for State 2 to compare later to know where to fill the next 25 items
    cur.execute(f'SELECT countyID FROM {state2}CovidInfo')
    state2DatabaseCountyCount = len(cur.fetchall())
    state2ActualCountyCount = len(get_countyNames(state2))
    cur.execute(f'SELECT countyID FROM {state2}CountyNames')
    state2NamesCountyCount = len(cur.fetchall())
    cur.execute(f'SELECT countyID FROM {state2}Demographics')
    state2DemographicsCountyCount = len(cur.fetchall())

   #If the number of rows (counties) is equal to  the number of actual counties in state 1 for the last table, 
   #then the following lines will run to fill in the tables for state 2.
    if(state1DatabaseCountyCount == state1ActualCountyCount):
        fill_countyNamesTable(state2, cur, conn)
        if state2NamesCountyCount == state2ActualCountyCount:
            fill_DemographicTable(state2, cur, conn)
        if state2DemographicsCountyCount == state2ActualCountyCount:
            fill_CovidInfoTable(state2, cur, conn)
        cur.execute(f'SELECT countyID FROM {state2}CovidInfo')
        state2DatabaseCountyCount = len(cur.fetchall())
        state2ActualCountyCount = len(get_countyNames(state2))
        #When all three tables are completed for state 2, the csv file will be created and written into.
        if (state2DatabaseCountyCount == state2ActualCountyCount):
            csvFile = f'{state2}_covidCalculatedData.csv'
            write_calculated_data_to_file(csvFile,state2, cur, conn)
            print('Done filling tables and writing files. Time to run visualization.py')
        else:
            print('Run code again to keep filling the Database.')

    conn.close()


if __name__ == "__main__":
    main()
