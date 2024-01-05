from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

from EnergyPoint import EnergyPoint

def write_points(config, energy_points):
    points = []

    ep: EnergyPoint
    for ep in energy_points:
        points.append(Point(config['measurement']).field('kWh', ep.energy).field('Watt', ep.power).time(ep.timestamp, write_precision=WritePrecision.S))

    client = InfluxDBClient(url=config['url'], token=config['token'], org=config['org'])
    write_api = client.write_api(write_options=SYNCHRONOUS)
    write_api.write(bucket=config['bucket'], record=points)