
import os

import pandas as pd


def extract_data(data, filename) -> pd.DataFrame:
    data_path = os.path.join("dataframe.p")
    t1 = pd.read_csv(data)
    bins = ["LiveBin_{}dM".format(x) for x in range(1, 17)]
    tpm10 = t1[[x for x in bins]].dropna().sum(axis=1)
    tOut = pd.DataFrame(
        {
            "TIMESTAMP": t1["TIMESTAMP"],
            "lat": t1["lat"],
            "lon": t1["lon"],
            "pm10": tpm10,
        }
    ).dropna()

    try:
        tOld = pd.read_pickle(data_path)
        tNew = (
            tOut.append(tOld, ignore_index=True)
                .drop_duplicates()
                .sort_values("TIMESTAMP")
        )



        tNew.to_csv(data_path)
    except:
        tOut.sort_values("TIMESTAMP").to_pickle(data_path)
        tNew = tOut
    # treduced=pd.DataFrame(columns=['TIMESTAMP','lat','lon','pm10'])
    lat=0
    lon=0

    pm10=0
    print(tNew)
    # print(treduced)
    # timestamp=tNew[0].TIMESTAMP
    list=[]
    timestamp=None
    for i,row in tNew.iterrows():
        print(i)
        if i%10==5:
            lat=row.lat
            lon=row.lon
            timestamp=row.TIMESTAMP
            pm10+=row.pm10
        if i%10==0:
            pm10+=row.pm10
            pm10=pm10/10
            list.append([timestamp, lat, lon, pm10])
            # d=pd.DataFrame({'TIMESTAMP': [timestamp],'lat':[lat], 'lon':[lon], 'pm10':[pm10]} )
            # print(d)
            # treduced.append(d)
            pm10=0
        else:
            pm10+=row.pm10

    treduced=pd.DataFrame(list, columns=['TIMESTAMP','lat','lon','pm10']).drop(0)
    print(treduced)
    # c=tOut.groupby(tOut.index/10)
    # print(c.head(100))
    treduced.to_csv(f'reducedData_{filename}.csv')


# b=pd.read_csv('extracted_Data_TOA5_fasttable1_2019_10_29_1029.csv')
with open('extracted_Data_TOA5_fasttable3_2019_10_29_1200.csv') as b:
    extract_data(b, '_TOA5_fasttable3_2019_10_29_1200')