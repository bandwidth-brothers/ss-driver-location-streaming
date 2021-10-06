import json


class DriverLocationJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        return obj.__dict__
