from models import Reservation
from setup import ma

from marshmallow import fields

class ReservationSchema(ma.ModelSchema):
    user = fields.Method('get_user')

    def get_user(self, reservation, **kwargs):
        user = self.context['user']
        if user.admin or reservation.user == user:
            return reservation.user.id
        else:
            return None

    class Meta:
        model = Reservation

reservation_schema = ReservationSchema()
reservations_schema = ReservationSchema(many=True)
