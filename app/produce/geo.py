import os
import sys
import googlemaps
import logging as log

from datetime import datetime
from googlemaps.maps import StaticMapMarker
from geographiclib.geodesic import Geodesic
from app.produce.domain import Driver, Delivery
from app.config import Config

config = Config()
DEFAULT_METERS_PER_PING = 10
DEFAULT_POINTS_DIR = "tmp/points"
DEFAULT_MAP_DIR = "tmp/maps"
MAX_MARKERS = 40


class TravelPlan:
    def __init__(self, distance: int, points: list[dict]):
        self.distance = distance
        self.points = points


class Geo:
    def __init__(self, meters_per_ping=DEFAULT_METERS_PER_PING):
        self.meters_per_ping = meters_per_ping

    def get_points(self, driver: Driver, delivery: Delivery) -> TravelPlan:
        """
        Get a travel plan for a driver and delivery. The plan will include
        the distance of the travel (in meters) and the points that will be
        traveled.

        :param driver: the driver
        :param delivery: the delivery
        :return: the travel plan
        """
        points_file = f"{DEFAULT_POINTS_DIR}/{driver.id}-{delivery.id}-points.txt"
        try:
            return self._get_plan_from_file(points_file)
        except FileNotFoundError:
            log.info(f"No file {points_file}. Will make an API call to get points.")
            plan = self._get_plan_from_api(driver=driver, delivery=delivery)
            self._write_plan_to_file(points_file, plan)
            return plan

    @staticmethod
    def _write_plan_to_file(points_file, plan: TravelPlan):
        """
        Write a travel plan to file. The file will contain the distance at
        the top of the file, and the coordinate points below.

        :param points_file: the points file
        :param plan: the travel plan
        """
        with open(points_file, 'a') as f:
            f.write(f"Distance:{plan.distance}{os.linesep}")
            for point in plan.points:
                f.write(f"{point['lat']},{point['lng']}{os.linesep}")

    @staticmethod
    def _get_plan_from_file(points_file) -> TravelPlan:
        """
        Get a travel plan from a points file.

        :param points_file: the points file
        :return: the travel plan
        """
        points = []
        with open(points_file) as f:
            distance = int(f.readline().strip().split(':')[1])
            for line in f:
                if line:
                    fields = line.split(',')
                    points.append({'lat': fields[0], 'lng': fields[1].strip()})
        return TravelPlan(distance=distance, points=points)

    def _get_plan_from_api(self, driver: Driver, delivery: Delivery) -> TravelPlan:
        """
        Get a travel plan for a delivery from the Google Maps API. An API
        key must be provided with the GOOGLE_API_KEY environment variable.

        :param driver: the driver
        :param delivery: the delivery
        :return: the travel plan
        """
        if not self.gmaps:
            # Create client only once
            if not config.api_key:
                log.error('GOOGLE_API_KEY environment variable not set.')
                sys.exit(1)
            self.gmaps = googlemaps.Client(key=config.api_key)

        directions = self.gmaps.directions(str(driver.current_location),
                                           str(delivery.address),
                                           mode='driving', departure_time=datetime.now())
        steps = directions[0]['legs'][0]['steps']
        distance = directions[0]['legs'][0]['distance']['value']
        points = []
        for step in steps:
            step_distance = step['distance']['value']
            points += self._process_step(step, 1, distance_til_end=step_distance)
        return TravelPlan(distance=distance, points=points)

    def _process_step(self, step, ticks, distance_til_end) -> list[dict]:
        """"
        Get points for a Step from Google Maps Directions API.
        For a Step, points will be generated from the starting
        location to the ending location. Points will be created
        at a set interval (meters_per_ping).

        See: https://gis.stackexchange.com/a/349485
        """
        geod = Geodesic.WGS84
        start = step['start_location']
        end = step['end_location']

        points = []
        while distance_til_end > self.meters_per_ping:
            inv = geod.Inverse(start['lat'], start['lng'], end['lat'], end['lng'])
            azi1 = inv['azi1']

            direct = geod.Direct(start['lat'], start['lng'], azi1, self.meters_per_ping * ticks)
            point = {'lat': direct['lat2'], 'lng': direct['lon2']}
            points.append(point)

            ticks += 1
            distance_til_end -= self.meters_per_ping
        return points

    def make_map(self):
        """
        Make a static map using the Google Maps API. The method will get
        all the points file in a directory and create corresponding maps
        for each delivery.
        """
        files = [f for f in os.listdir(DEFAULT_POINTS_DIR)]
        for file in files:
            fields = file.split('-')
            driver = fields[0]
            delivery = fields[1]
            out_file = f"{DEFAULT_MAP_DIR}/{driver}-{delivery}-map.png"

            plan = self._get_plan_from_file(f"{DEFAULT_POINTS_DIR}/{file}")
            points = list(map(lambda p: (p['lat'], p['lng']), plan.points))

            if len(points) > MAX_MARKERS:
                index_steps = int(len(points) / MAX_MARKERS)
                points = points[::index_steps]
            mid = int(len(points) / 2)

            gmaps = googlemaps.Client(key=config.api_key)
            markers = StaticMapMarker(locations=points, size='tiny', color='red')

            with open(out_file, 'wb') as f:
                zoom_level = self._get_zoom_level(plan.distance)
                for chunk in gmaps.static_map(size=(1000, 1000),
                                              zoom=zoom_level,
                                              center=points[mid],
                                              markers=[markers],
                                              format='png'):
                    f.write(chunk)

    @staticmethod
    def _get_zoom_level(distance):
        """
        Get the zoom level for the Google Static Maps API. The longer
        the distance, the less focused the zoom level will be.

        :param distance: the distance traveled
        :return: the zoom level
        """
        meters_per_mile = 1609
        miles = distance / meters_per_mile
        if miles < 1:
            return 17
        elif miles < 1.5:
            return 16
        elif miles < 2:
            return 15
        elif miles < 5:
            return 14
        elif miles < 10:
            return 13
        elif miles < 20:
            return 12
        elif miles < 25:
            return 11
        return 10
