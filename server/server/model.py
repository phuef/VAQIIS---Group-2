from server import db


class Airpolution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    longitude = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    data = db.Column(db.Float, nullable=False)
    city = db.Column(db.String(30), nullable=False)
    street = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return "<Airpolution city: {city}, street: {street}, data: {data}>".format(
            city=self.city, street=self.street, data=self.data
        )

