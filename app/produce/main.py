import json
import logging as log

from functools import reduce
from app.produce.geo import Geo
from app.produce.parser import DriverLocationParser
from app.produce.producer import DriverLocationProducer


def main(_args):
    args = DriverLocationParser(_args).get_args()
    if args.verbose:
        args.log = 'VERBOSE'
    log.basicConfig(level=args.log)

    if args.make_maps:
        Geo(data_dir=args.data_dir, no_api_key=args.no_api_key)\
            .make_maps()
        return

    producer = DriverLocationProducer(buffer_size=args.buffer_size,
                                      max_threads=args.max_threads,
                                      data_dir=args.data_dir,
                                      delay=args.delay,
                                      no_api_key=args.no_api_key)
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
