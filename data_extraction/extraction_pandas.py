# timestamp, lat, long, pm10

import pandas as pd
import pandasql as ps
import os
import csv

def dataExtractionCSV(filename):
    data= pd.read_csv(filename)
    print(data)
    str=""
    for i in range(1,17):
        str+= f"LiveBin_{i}dM"
        if i<16:
            str+="+ "
    sql=f"""SELECT timestamp, lat, lon, {str} AS pm10 FROM data"""
    a=ps.sqldf(sql, locals())
    a.to_csv(f'exracted_Data_{filename}')


def dataExtractionDAT(filename):

    data= pd.read_csv(filename)
    print(data)
    str=""
    for i in range(1,17):
        str+= f"LiveBin_{i}dM"
        if i<16:
            str+=", "
    sql=f"""SELECT TIMESTAMP, 
    substr(rmclatitude, 1, 2) || '.' || cast(cast(substr(rmclatitude, 3, 2) || substr(rmclatitude, 6)as integer)/60 as text) as lat, 
    substr(rmclongitude, 2, 2) || '.' || cast(cast(substr(rmclongitude, 4, 2) || substr(rmclongitude, 7)as integer)/60 as text) as lon, 
    {str}  FROM data"""
    a=ps.sqldf(sql, locals())
    a.to_csv(f'extracted_Data_{filename}')
    deleteUnneccessaryRows(f'extracted_Data_{filename}')

def datToCSV(filename):
    with open(f'{filename}.dat', 'r') as reader:
        #Read and print the entire file line by line
        line = reader.readline()
        print(line, end='')
        f= open(f"{filename}.txt","w+")
        while line != '':  # The EOF char is an empty string
            #print(line, end='')
            f.write(f'{line}\r\n')
            line = reader.readline()
    with open(f'{filename}.txt', 'r') as fin:
        data = fin.read().splitlines(True)
    with open(f'{filename}.txt', 'w') as fout:
        fout.writelines(data[1:])
        df = pd.read_csv(f'{filename}.txt')
        df.to_csv(f'{filename}.csv')
        dataExtractionDAT(f'{filename}.csv')

def datExtraction(filename):
    datToCSV(filename)
    os.remove(f'{filename}.txt')
    os.remove(f'{filename}.csv')

def deleteUnneccessaryRows(filename):
    lines=list()
    with open(filename, 'r') as readFile:
        reader = csv.reader(readFile)
        for row in reader:
            lines.append(row)
            for field in row:
                if field=="TS" or field=="0.0":
                    lines.remove(row)
                    break
    with open(filename, 'w', newline='') as writeFile:
        writer = csv.writer(writeFile)
        writer.writerows(lines)


# dataExtractionCSV('2019-12-19_fasttable.csv')
# datExtraction('TOA5_fasttable2_2019_10_29_0939')
# datExtraction('TOA5_fasttable1_2019_10_29_1029')
# datExtraction('TOA5_fasttable2_2019_10_29_1000')
# datExtraction('TOA5_fasttable2_2019_10_29_1100')
# datExtraction('TOA5_fasttable3_2019_10_29_1200')
# datExtraction('TOA5_fasttable4_2019_10_30_1336')
# datExtraction('TOA5_fasttable4_2019_10_30_1400')
# datExtraction('TOA5_fasttable5_2019_10_31_0958')
# datExtraction('TOA5_fasttable6_2019_11_14_0941')
# datExtraction('TOA5_fasttable9_2019_11_21_0954')
# datExtraction('TOA5_fasttable10_2019_11_21_1200')
