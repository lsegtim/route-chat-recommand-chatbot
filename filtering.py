import math
from datetime import time

import pandas as pd
from bson import ObjectId
from dateutil.parser import parser


def haversine_distance(lat1, lon1, lat2, lon2):
    r = 6371000  # Radius of the Earth in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # kilometers
    return (r * c) / 1000


def is_within_radius(row, current_latitude, current_longitude, radius):
    distance = haversine_distance(current_latitude, current_longitude, row['latitude'], row['longitude'])
    return distance <= radius


# Function to convert time string to datetime.time object
def convert_time_string_to_time(time_string):
    # parse time string to time
    return parser().parse(time_string).time()


# Function to check if a time range overlaps with the operating hours of a row
def is_within_time_range(row, start_time, end_time):
    open_time = convert_time_string_to_time(row['openTime'])
    close_time = convert_time_string_to_time(row['closeTime'])

    # If the place is open 24 hours
    if open_time == time(0, 0) and close_time == time(0, 0):
        return True

    # Check for overlap
    return (start_time <= open_time <= end_time) or (start_time <= close_time <= end_time)


def check_accessibility(row, accessibility_values, column_to_be_checked='accessibility'):
    row_accessibility_values = set(row[column_to_be_checked].split(","))

    return any(value in row_accessibility_values for value in accessibility_values)


def filter_data(shortest_path, locations):
    location_temp = locations.copy()

    ################################################ Radius ################################################
    # filter locations by radius
    locations = locations[locations.apply(
        lambda row: is_within_radius(row, shortest_path.latitude, shortest_path.longitude,
                                     shortest_path.distanceRadiusValue), axis=1)]

    print("Location_by_radius")
    print(locations)
    print("\n\n\n\n")

    ################################################ Time ################################################
    # Convert "7.00AM - 7.00PM" to datetime.time objects
    start_time = convert_time_string_to_time(shortest_path.updatedData["Time Restrictions"].split("-")[0])
    end_time = convert_time_string_to_time(shortest_path.updatedData["Time Restrictions"].split("-")[1])

    print(start_time)
    print(end_time)

    # Filter locations by time
    locations = locations[locations.apply(lambda row: is_within_time_range(row, start_time, end_time), axis=1)]

    print(locations)
    print("\n\n\n\n")

    ################################################ Accessibility ################################################
    # if filter is "Not selected" then don't filter
    if shortest_path.updatedData["Accessibility"] != "Not selected":
        # Split the given accessibility variable by comma and strip whitespace
        accessibility_values = [value.strip() for value in shortest_path.updatedData["Accessibility"].split(",")]

        locations = locations[locations.apply(lambda row: check_accessibility(row, accessibility_values), axis=1)]

        print(locations)

    ################################################ Historical Contexts ################################################
    # if filter is "Not selected" then don't filter
    if shortest_path.updatedData["Historical Contexts"] != "Not selected":
        # Split the given historical context variable by comma and strip whitespace
        historical_context_values = [value.strip() for value in
                                     shortest_path.updatedData["Historical Contexts"].split(",")]

        locations = locations[locations.apply(
            lambda row: check_accessibility(row, historical_context_values, column_to_be_checked='historical_context'),
            axis=1)]

        print(locations)

    ################################################ Hands-On Activities ################################################
    # if filter is "Not selected" then don't filter
    if shortest_path.updatedData["Hands-On Activities"] != "Not selected":
        # Split the given hands on activities variable by comma and strip whitespace
        hands_on_activities_values = [value.strip() for value in
                                      shortest_path.updatedData["Hands-On Activities"].split(",")]

        locations = locations[locations.apply(
            lambda row: check_accessibility(row, hands_on_activities_values,
                                            column_to_be_checked='hands_on_activities'),
            axis=1)]

        print(locations)

    print("location_count 1", len(locations))

    # convert shortes_path.destination_id to <class 'bson.objectid.ObjectId'>
    destination_id = ObjectId(shortest_path.destination_id)

    # if destination_id is not in the filtered data
    if destination_id not in locations['_id'].values:
        # find the destination location and add it to the filtered data
        destination_location = location_temp[location_temp['_id'] == destination_id]
        locations = pd.concat([locations, destination_location])

    print("location_count", len(locations))

    return locations
