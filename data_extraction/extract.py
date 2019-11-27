'''
Author: Niklas Aßelmann
'''

import csv

def getValues(filePath):
    with open(filePath) as csv_file:
        daten = csv.reader(csv_file.readlines())
        next(daten, None)
        elements = []
        for x in daten:
            elements.append(x)
        lat=[]
        lon=[]
        time=[]
        '''
        pm2.5=[]
        pm5=[]
        pm=10[]
        '''
        lat= searchForParameters(elements, ["rmclatitude"])
        lon= searchForParameters(elements, ["rmclongitude"])
        time= searchForParameters(elements, ["TIMESTAMP"])
        '''
        pm2.5= searchForParameters(elements, [""])
        pm5= searchForParameters(elements, [""])
        pm10= searchForParameters(elements, [""])
        '''
        list_length = len(time)
        counter=2
        while list_length > counter:
            if lon[counter]=="":
                print("No Longitude")
                counter=counter+1
            else:
                    if lat[counter]=="":
                        print("No Latitude")
                        counter=counter+1
                    else:
                        if time[counter]=="":
                            print("No Time")
                            counter=counter+1
                        else:
                            Output=[lon[counter],lat[counter],time[counter]]
                            print(Output)
                            counter=counter+1


def searchForParameters(elements, paramArray):
    '''
    Function purpose: return all attributes of a elements in the first row of a file \n
    Input: paramArray, elements \n
    Output: getAllRowElements(x,elements)
    '''
    for x in paramArray:
        for row in elements[0]:
            if x in row:
                return getAllRowElements(x,elements)


def getAllRowElements(rowname,elements):
    '''
    Function purpose: help-function to get all row elements for a specific string \n
    Input: rowname, elements \n
    Output: array values
    '''
    for idx, val in enumerate(elements[0]):
        if  rowname in val:
            indexOf = idx
            values = []
            for x in elements:
                if x[indexOf] != rowname:
                    values.append(x[indexOf])
            return values

getValues("sample_data.dat")