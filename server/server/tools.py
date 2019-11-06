from .model import Airpolution
from flask import url_for
from datetime import datetime as dt

def model_to_json(database_content: Airpolution) -> dict:
    return {
        "id": database_content.id,
        "coordinates": [database_content.latitude, database_content.longitude],
        "data": database_content.data,
        "city": database_content.city,
        "street": database_content.street,
    }

def log_data_to_file(line):
    current_date = dt.now().date()
    with open("server\\server\\data_foder\\%s.csv" % current_date, "at") as target:
        target.write(line)
