from .model import Airpolution


def model_to_json(database_content: Airpolution) -> dict:
    return {
        "id": database_content.id,
        "coordinates": [database_content.latitude, database_content.longitude],
        "data": database_content.data,
        "city": database_content.city,
        "street": database_content.street,
    }

