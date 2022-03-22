from typing import Optional
from datetime import datetime


class Address:
    def __init__(self, street: str, city: str, state: str, zip_code: str):
        self.street = street
        self.city = city
        self.state = state
        self.zip = zip_code

    def __str__(self):
        return f"{self.street}, {self.city}, {self.state} {self.zip}"


class Delivery:
    def __init__(self, deliv_id: int, driver_id: str, address: Address):
        self.id = deliv_id
        self.driver_id = driver_id
        self.address = address
        self.complete = False

    def set_complete(self):
        self.complete = True

    def is_complete(self):
        return self.complete

    def __str__(self):
        return f"deliv_id: {self.id}, driver_id: {self.driver_id}, complete: {self.complete}, addr: {self.address}"


class Driver:
    def __init__(self, driver_id: str, current_location: Address, deliveries: list[Delivery]):
        self.id = driver_id
        self.deliveries = deliveries
        self.current_delivery: Optional[Delivery] = None
        self.current_location: Address = current_location

    def has_more_deliveries(self):
        return len(self.deliveries) != 0

    def has_active_delivery(self):
        return self.current_delivery is not None

    def get_next_delivery(self):
        if not self.has_more_deliveries():
            return None
        delivery = self.deliveries.pop(0)
        self.current_delivery = delivery
        return delivery

    def is_current_delivery_complete(self) -> bool:
        return self.current_delivery.is_complete()

    def complete_current_delivery(self):
        self.current_delivery.set_complete()

    def set_current_delivery(self, delivery: Delivery):
        self.current_delivery = delivery

    def set_current_location(self, address: Address):
        self.current_location = address


class DriverLocation:
    def __init__(self, delivery_id, driver_id, lat, lng, timestamp: datetime):
        self.delivery_id = delivery_id
        self.driver_id = driver_id
        self.lat = lat
        self.lng = lng
        self.timestamp = timestamp

    def __str__(self):
        return f"delivery_id: {self.delivery_id}, driver_id: {self.driver_id} lat: {self.lat}, lng: {self.lng}, " \
               f"timestamp: {self.timestamp.isoformat()}"
