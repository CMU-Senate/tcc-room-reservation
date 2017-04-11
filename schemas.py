from models import Reservation

from marshmallow_sqlalchemy import ModelSchema

class ReservationSchema(ModelSchema):
    class Meta:
        model = Reservation

reservation_schema = ReservationSchema()
reservations_schema = ReservationSchema(many=True)
