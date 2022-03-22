import json

from datetime import datetime
from app.produce.domain import DriverLocation

class DriverLocationJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return obj.__dict__


class DriverLocationJsonDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=DriverLocationJsonDecoder.object_hook, *args, **kwargs)

    @classmethod
    def object_hook(cls, dct):
        driver_id = cls._get(dct, 'driver_id')
        delivery_id = cls._get(dct, 'delivery_id')
        lat = cls._get(dct, 'lat')
        lng = cls._get(dct, 'lng')
        timestamp = cls._get(dct, 'timestamp')
        return DriverLocation(driver_id=driver_id, delivery_id=delivery_id, lat=lat, lng=lng, timestamp=timestamp)

    @classmethod
    def _get(cls, dct, name):
        try:
            return dct[name]
        except KeyError:
            return None


