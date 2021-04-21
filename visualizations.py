import matplotlib
import matplotlib.pyplot as plt
import numpy
import numpy as np
from bs4 import BeautifulSoup
import requests
import re
import os
import csv
import sqlite3
import json

def CovidCasesBarGraph(state, cur, conn):
    """Takes in the database cursor, connection, and the state name as a string. For the inputted state, creates a bar graph displaying 
    the COVID case count for each county that has a case count above the state case count average"""
    
    cur.execute(f'SELECT {state}CountyNames.countyName, {state}CovidInfo.covidNumberCases FROM {state}CountyNames JOIN {state}CovidInfo ON {state}CountyNames.countyID = {state}CovidInfo.countyID')
    state_counties = cur.fetchall()
    state_countynames = []
    state_covidCases= []
    total = 0
    for i in state_counties:
        total += i[1]
    average = total/len(state_counties)
    for i in state_counties:
        if i[1] >= average:
            state_countynames.append(i[0])
            state_covidCases.append(i[1])
    x_pos = [x for x in state_countynames]
    y_pos = [x for x in state_covidCases]
    plt.xticks(rotation = 90)
    plt.bar(x_pos, y_pos, color='blue', edgecolor = "black")
    fixedName = state.replace("_", " ")
    plt.xlabel(f'{fixedName} County')
    plt.ylabel('Number of COVID Cases')
    plt.title(f'Number of COVID Cases for {fixedName} Counties Above State Average')
    plt.show()

def DoubleHistogram(states, cur, conn):
    """Takes in the database cursor, connection, and a list of state names as a strings. Creates a double histogram 
    for two states, comparing their range of Positivity Rates across their respective counties"""

    state1Name = states[0]
    state2Name = states[1]

    state1 = open(f'{state1Name}_covidCalculatedData.csv', 'r')
    state1_lines = state1.readlines()
    state1.close()
    state1_positvity = []
    for row in state1_lines[1:]:
        data = row.split(',')
        rate = data[1]
        state1_positvity.append(float(rate))
    
    state2 = open(f'{state2Name}_covidCalculatedData.csv', 'r')
    state2_lines = state2.readlines()
    state2.close()
    state2_positvity = []
    for row in state2_lines[1:]:
        data = row.split(',')
        rate = data[1]
        state2_positvity.append(float(rate))


    state1fixedName = state1Name.replace("_", " ")
    state2fixedName = state2Name.replace("_", " ")
    plt.hist(state1_positvity, bins = 15, color='blue', alpha = 0.5, label=state1fixedName)
    plt.hist(state2_positvity, bins = 15, color='red', alpha = 0.5, label=state2fixedName)
    plt.legend(loc='upper right')
    plt.xlabel('Positivity Rate')
    plt.ylabel('Number of Counties')
    plt.title('Distribution of Positivity Rates')


    plt.show() 

def PovertyVSDeathScatter(states, cur, conn):
    """Takes in the database cursor, connection, and a list of state names as a strings. Creates a double scatterplot 
    comparing the Poverty Rates and COVID Death Rates for each county within the two passed states"""

    state1Name = states[0]
    state2Name = states[1]

    state1 = open(f'{state1Name}_covidCalculatedData.csv', 'r')
    state1_lines = state1.readlines()
    state1.close()
    state1_death = []
    for row in state1_lines[1:]:
        data = row.split(',')
        rate = data[2]
        state1_death.append(float(rate))
    
    cur.execute(f'SELECT povertyRate FROM {state1Name}Demographics')
    state1_poverty = cur.fetchall()
    
    state2 = open(f'{state2Name}_covidCalculatedData.csv', 'r')
    state2_lines = state2.readlines()
    state2.close()
    state2_death = []
    for row in state2_lines[1:]:
        data = row.split(',')
        rate = data[2]
        state2_death.append(float(rate))
    
    cur.execute(f'SELECT povertyRate FROM {state2Name}Demographics')
    state2_poverty = cur.fetchall()

    fig = plt.figure()
    ax1 = fig.add_subplot(111)

    state1fixedName = state1Name.replace("_", " ")
    state2fixedName = state2Name.replace("_", " ")

    ax1.scatter(state1_poverty, state1_death, s=10, c='b', marker="s", label=state1fixedName)
    ax1.scatter(state2_poverty,state2_death, s=10, c='r', marker="o", label=state2fixedName)
    plt.xlabel('Poverty Rate')
    plt.ylabel('COVID Death Rate')
    plt.legend(loc='upper right')
    plt.title(f'Poverty Rate vs. COVID Death Rate per County in {state1fixedName} and {state2fixedName}')

    s1poverty_array = list(map(lambda x: x[0], state1_poverty))
    s1death_array = np.array(state1_death)
    trend = np.polyfit(s1poverty_array,s1death_array, 1)
    p = np.poly1d(trend)
    plt.plot(s1poverty_array,p(s1poverty_array),"b--")

    s2poverty_array = list(map(lambda x: x[0], state2_poverty))
    s2death_array = np.array(state2_death)
    trend = np.polyfit(s2poverty_array,s2death_array, 1)
    p = np.poly1d(trend)
    plt.plot(s2poverty_array,p(s2poverty_array),"r--")


    plt.show()

def PovertyVSPositivityScatter(states, cur, conn):
    """Takes in the database cursor, connection, and a list of state names as a strings. Creates a double scatter plot comparing the 
    Poverty Rates and Positivity Rates for each county within the two passed states"""

    state1Name = states[0]
    state2Name = states[1]

    state1 = open(f'{state1Name}_covidCalculatedData.csv', 'r')
    state1_lines = state1.readlines()
    state1.close()
    state1_positivity = []
    for row in state1_lines[1:]:
        data = row.split(',')
        rate = data[1]
        state1_positivity.append(float(rate))
    
    cur.execute(f'SELECT povertyRate FROM {state1Name}Demographics')
    state1_poverty = cur.fetchall()
    
    state2 = open(f'{state2Name}_covidCalculatedData.csv', 'r')
    state2_lines = state2.readlines()
    state2.close()
    state2_positivity = []
    for row in state2_lines[1:]:
        data = row.split(',')
        rate = data[1]
        state2_positivity.append(float(rate))
    
    cur.execute(f'SELECT povertyRate FROM {state2Name}Demographics')
    state2_poverty = cur.fetchall()

    fig = plt.figure()
    ax1 = fig.add_subplot(111)

    state1fixedName = state1Name.replace("_", " ")
    state2fixedName = state2Name.replace("_", " ")

    ax1.scatter(state1_poverty, state1_positivity, s=10, c='b', marker="s", label=state1fixedName)
    ax1.scatter(state2_poverty,state2_positivity, s=10, c='r', marker="o", label=state2fixedName)
    plt.xlabel('Poverty Rate')
    plt.ylabel('COVID Positivity Rate')
    plt.legend(loc='upper right')
    plt.title(f'Poverty Rate vs. Positivity Rate per County in {state1fixedName} and {state2fixedName}')

    s1poverty_array = list(map(lambda x: x[0], state1_poverty))
    s1positivity_array = np.array(state1_positivity)
    trend = np.polyfit(s1poverty_array,s1positivity_array, 1)
    p = np.poly1d(trend)
    plt.plot(s1poverty_array,p(s1poverty_array),"b--")

    s2poverty_array = list(map(lambda x: x[0], state2_poverty))
    s2positivity_array = np.array(state2_positivity)
    trend = np.polyfit(s2poverty_array,s2positivity_array, 1)
    p = np.poly1d(trend)
    plt.plot(s2poverty_array,p(s2poverty_array),"r--")

    plt.show()



def main():
    """Takes nothing as an input and returns nothing. Ask the user for two state    
    names they inputted into the data collection program, establishes the database connection, 
    and calls CovidCasesBarGraph()for each state, DoubleHistogram(), PovertyVSDeathScatter(), 
    and PovertyVSPositivityScatter(). Closes the database connection."""   

    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/covidRawData.db')
    cur = conn.cursor()

    input1 = input("What Was the First State You Compared Prior: ")
    input2 = input("What Was the Second State you Compared It With: ")
    state1 = input1.replace(" ", "_")
    state2 = input2.replace(" ", "_")
    states = [state1, state2]

    for state in states:
        CovidCasesBarGraph(state, cur, conn)

    DoubleHistogram(states, cur, conn)
    PovertyVSDeathScatter(states, cur, conn)
    PovertyVSPositivityScatter(states, cur, conn)

if __name__ == "__main__":
    main()