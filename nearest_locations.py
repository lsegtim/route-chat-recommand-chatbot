from filtering import haversine_distance


def sort_by_distance_from_current_location(filtered_data, current_location, distance):
    # Calculate distance from current location
    filtered_data['distance'] = filtered_data.apply(
        lambda row: haversine_distance(current_location[0], current_location[1], row['latitude'], row['longitude']),
        axis=1)

    # Sort by distance
    filtered_data = filtered_data.sort_values(by=['distance'])

    # if distance is 0 then return the filtered data
    if distance == 0:
        return filtered_data
    else:
        # return distance >= distance
        return filtered_data[filtered_data['distance'] >= distance]
