from app.produce.domain import Driver, Delivery, Address


def _get_drivers_list() -> list[Driver]:
    driver1 = Driver('1', current_location=Address('123 Main St', 'Washington', 'DC', '20001'),
                     deliveries=[Delivery(1, '1', Address('123 Broadway', 'Washington', 'DC', '20001'))])
    driver2 = Driver('2', current_location=Address('321 MLK Blvd', 'Washington', 'DC', '20001'),
                     deliveries=[Delivery(2, '2', Address('667 Awesome St', 'Washington', 'DC', '20001')),
                                 Delivery(3, '2', Address('456 Anywhere', 'Washington', 'DC', '20001'))])
    return [driver1, driver2]
