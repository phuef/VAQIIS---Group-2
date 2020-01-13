# timestamp, lat, long, pm10

import pandas as pd
import pandasql as ps

def dataExtraction(filename):
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

dataExtraction('2019-12-19_fasttable.csv')