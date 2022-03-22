import os
import abc
import random
import sys
import math
import traceback

import googlemaps
import logging as log

from abc import abstractmethod
from typing import Iterable
from datetime import datetime
from googlemaps.maps import StaticMapMarker
from googlemaps.exceptions import Timeout, TransportError, ApiError
from geographiclib.geodesic import Geodesic
from app.produce.domain import Driver, Delivery
from app.config import Config
from app.common.constants import\
    GEO_DEFAULT_METERS_PER_PING,\
    GEO_DEFAULT_POINTS_DIR, \
    GEO_DEFAULT_MAPS_DIR,\
    GEO_DEFAULT_DATA_DIR, \
    GEO_MAX_MARKERS


class TravelPlan:
    def __init__(self, distance: int, points: list[dict]):
        self.distance = distance
        self.points = points


class IGeo(abc.ABC):
    @abstractmethod
    def get_points(self, driver: Driver, delivery: Delivery) -> TravelPlan:
        pass

    @abstractmethod
    def make_maps(self):
        pass


class RandomGeo(IGeo):
    def get_points(self, driver: Driver, delivery: Delivery) -> TravelPlan:
        num_points = random.randrange(50, 500)
        lat = 38.971652947264985
        lng = -77.05757761585986
        points = []
        for i in range(0, num_points):
            points.append({'lat': lat, 'lng': lng})
        return TravelPlan(distance=(num_points * GEO_DEFAULT_METERS_PER_PING),
                          points=points)

    def make_maps(self):
        raise Exception('Maps not available with random geo generator')


class GoogleMapsGeo(IGeo):
    def __init__(self,
                 meters_per_ping=GEO_DEFAULT_METERS_PER_PING,
                 no_api_key=False, data_dir=GEO_DEFAULT_DATA_DIR):
        config = Config()
        self.api_key = config.api_key
        self.meters_per_ping = meters_per_ping
        self._points_dir = os.path.join(data_dir, GEO_DEFAULT_POINTS_DIR)
        self._maps_dir = os.path.join(data_dir, GEO_DEFAULT_MAPS_DIR)

        self._create_data_directories_if_needed(self._points_dir, self._maps_dir)

        if no_api_key:
            log.warning('Will not be able to make API calls.')
            log.warning('All points files will need to be present for each delivery.')
            return

        if not config.api_key:
            log.warning('GOOGLE_API_KEY environment variable not set. Cannot make API calls.')
            sys.exit(0)
        try:
            self.gmaps = googlemaps.Client(key=self.api_key)
            log.info('Google maps client created.')
        except Exception as e:
            log.error(e)
            traceback.print_exc()
            sys.exit(0)

    @staticmethod
    def _create_data_directories_if_needed(points_dir, maps_dir):
        if not os.path.exists(points_dir):
            log.info(f"{points_dir} does not exist. It will be created.")
            os.makedirs(points_dir)
        if not os.path.exists(maps_dir):
            log.info(f"{maps_dir} does not exist. It will be created.")
            os.makedirs(maps_dir)
        log.debug(f"Points files stored in {points_dir}")
        log.debug(f"Static Maps store in {maps_dir}")

    def get_points(self, driver: Driver, delivery: Delivery) -> TravelPlan:
        """
        Get a travel plan for a driver and delivery. The plan will include
        the distance of the travel (in meters) and the points that will be
        traveled.

        :param driver: the driver
        :param delivery: the delivery
        :return: the travel plan
        """
        points_file = f"{self._points_dir}/{driver.id}-{delivery.id}-points.txt"
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
        try:
            directions = self.gmaps.directions(str(driver.current_location),
                                               str(delivery.address),
                                               mode='driving', departure_time=datetime.now())
        except Exception as ex:
            log.error(f"Could not retrieve directions for {delivery}")
            traceback.print_exc()
            return
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

    def make_maps(self):
        """
        Make a static map using the Google Maps API. The method will get
        all the points file in a directory and create corresponding maps
        for each delivery.

        To minimize the number of markers on the map, the points will
        be selected up to a max, at even intervals
        """
        files = [f for f in os.listdir(self._points_dir)]
        if len(files) == 0:
            log.info(f"There are no points files in {self._points_dir}. No maps will be created.")
            return

        def _get_map_args_from_points_file(_points_file):
            plan = self._get_plan_from_file(f"{self._points_dir}/{_points_file}")
            points = list(map(lambda p: (p['lat'], p['lng']), plan.points))

            # filter points evenly to be less than GEO_MAX_MARKERS
            if len(points) > GEO_MAX_MARKERS:
                index_steps = int(math.ceil(len(points) / GEO_MAX_MARKERS))
                points = points[::index_steps]
            mid = int(len(points) / 2)
            return {
                'markers': StaticMapMarker(locations=points, size='tiny', color='red'),
                'center_marker': points[mid],
                'zoom_level': self._get_zoom_level(plan.distance)}

        for points_file in files:
            fields = points_file.split("-")
            driver_id = fields[0]
            delivery_id = fields[1]
            map_file = f"{self._maps_dir}/{driver_id}-{delivery_id}-map.png"
            if os.path.exists(map_file):
                log.info(f"{map_file} already exists. Will not create a new one.")
                continue

            markers, center_marker, zoom_level = _get_map_args_from_points_file(points_file).values()

            try:
                with open(map_file, 'wb') as f:
                    chunks: Iterable = self.gmaps.static_map(
                        size=(1000, 1000),
                        zoom=zoom_level,
                        center=center_marker,
                        markers=[markers],
                        format='png')
                    if chunks:
                        for chunk in chunks:
                            f.write(chunk)
                    log.info(f"{map_file} created.")
            except (Timeout, TransportError, ApiError) as ex:
                log.error(f"Could not create {map_file}: {ex}")

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
