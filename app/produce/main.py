import json
import logging as log
import sys

from functools import reduce
from app.produce.geo import RandomGeo
from app.produce.geo import GoogleMapsGeo
from app.produce.parser import DriverLocationParser
from app.produce.producer import DriverLocationProducer


def main(_args):
    args = DriverLocationParser(_args).get_args()
    if args.verbose:
        args.log = 'VERBOSE'
    log.basicConfig(level=args.log)

    if args.no_gapi:
        geo = RandomGeo()
    else:
        geo = GoogleMapsGeo(data_dir=args.data_dir, no_api_key=args.no_api_key)

    if args.make_maps:
        if args.no_gapi:
            log.error('Maps cannot be made without Google Maps!')
            sys.exit(1)
        geo.make_maps()
        return

    producer = DriverLocationProducer(geo,
                                      buffer_size=args.buffer_size,
                                      max_threads=args.max_threads,
                                      delay=args.delay)
    producer.start()
    producer.join()

    locations = {}
    for location in producer.get_driver_locations():
        driver_id = location.driver_id
        if driver_id not in locations:
            locations[driver_id] = 0
        locations[driver_id] += 1

    log.info(json.dumps(locations, indent=4))
    total = reduce(lambda tot, val: tot + val, locations.values(), 0)
    log.info(f"Total Points: {total}")
