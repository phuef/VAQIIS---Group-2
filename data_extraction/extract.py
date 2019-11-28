import csv
import numpy as np

def getValues(filePath):
    with open(filePath) as csv_file:
        daten = csv.reader(csv_file.readlines())
        next(daten, "NAN")
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
        bin1= searchForParameters(elements, ["LiveBin_1dM"])
        bin2= searchForParameters(elements, ["LiveBin_2dM"])
        bin3= searchForParameters(elements, ["LiveBin_3dM"])
        bin4= searchForParameters(elements, ["LiveBin_4dM"])
        bin5= searchForParameters(elements, ["LiveBin_5dM"])
        bin6= searchForParameters(elements, ["LiveBin_6dM"])
        bin7= searchForParameters(elements, ["LiveBin_7dM"])
        bin8= searchForParameters(elements, ["LiveBin_8dM"])
        bin9= searchForParameters(elements, ["LiveBin_9dM"])
        bin10= searchForParameters(elements, ["LiveBin_10dM"])
        bin11= searchForParameters(elements, ["LiveBin_11dM"])
        bin12= searchForParameters(elements, ["LiveBin_12dM"])
        bin13= searchForParameters(elements, ["LiveBin_13dM"])
        bin14= searchForParameters(elements, ["LiveBin_14dM"])
        bin15= searchForParameters(elements, ["LiveBin_15dM"])
        bin16= searchForParameters(elements, ["LiveBin_16dM"])
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
                            if bin1[counter]!=None or bin2[counter]!=None or bin3[counter]!=None or bin4[counter]!=None or bin5[counter]!=None or bin6[counter]!=None or bin7[counter]!=None or bin8[counter]!=None or bin9[counter]!=None or bin10[counter]!=None or bin11[counter]!=None or bin12[counter]!=None or bin13[counter]!=None or bin14[counter]!=None or bin15[counter]!=None or bin16[counter]!=None:
                                    if bin1[counter]=="NAN"  or bin2[counter]=="NAN" or bin3[counter]=="NAN" or bin4[counter]=="NAN" or bin5[counter]=="NAN" or bin6[counter]=="NAN" or bin7[counter]=="NAN" or bin8[counter]=="NAN" or bin9[counter]=="NAN" or bin10[counter]=="NAN" or bin11[counter]=="NAN" or bin12[counter]=="NAN" or bin13[counter]=="NAN" or bin14[counter]=="NAN" or bin15[counter]=="NAN" or bin16[counter]=="NAN":
                                        print("Not all Bins have Values")
                                        counter=counter+1
                                    else:
                                        PM10 = float(bin1[counter])+float(bin2[counter])+float(bin3[counter])+float(bin4[counter])+float(bin5[counter])+float(bin6[counter])+float(bin7[counter])+float(bin8[counter])+float(bin9[counter])+float(bin10[counter])+float(bin11[counter])+float(bin12[counter])+float(bin13[counter])+float(bin14[counter])+float(bin15[counter])+float(bin16[counter])
                                        Output=[lon[counter],lat[counter],time[counter],PM10]
                                        C = np.array(Output)
                                        print(C)
                                        counter=counter+1
                            else:
                                print("Not all Bins have Values")
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