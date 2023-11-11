import numpy as np
import pandas as pd
from bson import ObjectId

from filtering import haversine_distance


def create_adjacency_matrix(df):
    num_nodes = len(df)
    adj_matrix = np.zeros((num_nodes, num_nodes))

    for i in range(num_nodes):
        for j in range(num_nodes):
            if i != j:  # No need to calculate distance from a node to itself
                adj_matrix[i][j] = haversine_distance(df.iloc[i]['latitude'], df.iloc[i]['longitude'],
                                                      df.iloc[j]['latitude'], df.iloc[j]['longitude'])
            else:
                adj_matrix[i][j] = 0  # Set distance from a node to itself as zero

    return adj_matrix


def tsp(adj_matrix, start, end):
    n = len(adj_matrix)
    dp = [[float('inf')] * n for _ in range(1 << n)]
    dp[1 << start][start] = 0
    pred = [[-1] * n for _ in range(1 << n)]

    for mask in range(1, 1 << n):
        for u in range(n):
            if not (mask & (1 << u)):
                continue

            for v in range(n):
                if mask & (1 << v) and adj_matrix[v][u] != -1:
                    if dp[mask][u] > dp[mask ^ (1 << u)][v] + adj_matrix[v][u]:
                        dp[mask][u] = dp[mask ^ (1 << u)][v] + adj_matrix[v][u]
                        pred[mask][u] = v

    mask = (1 << n) - 1
    u = end
    path = []

    while u != -1:
        path.append(u)
        v = pred[mask][u]
        mask = mask ^ (1 << u)
        u = v

    path.reverse()
    return dp[(1 << n) - 1][end], path


def duplicate_nodes(adj_matrix, copies):
    n = len(adj_matrix)
    new_n = n * copies
    new_matrix = [[0] * new_n for _ in range(new_n)]

    for i in range(new_n):
        for j in range(new_n):
            new_matrix[i][j] = adj_matrix[i % n][j % n]

    # # print mappping
    # for i in range(new_n):
    #     print(i, ":", i % n, end="\t")
    return new_matrix


def optimize_path(shortest_path, start_node_index, end_node_index, df):
    print("\nOptimizing path...")
    print(shortest_path)
    print(start_node_index, end_node_index)

    # Step 1: Remove duplicated indices
    i = 0
    while i < len(shortest_path) - 1:
        if shortest_path[i] == shortest_path[i + 1]:
            shortest_path.pop(i)
        else:
            i += 1

    # Step 2: Remove cycles
    node_indices = {}  # Dictionary to keep track of the index at which each node is first encountered
    for i, node in enumerate(shortest_path):
        if node in node_indices:
            # Cycle detected from node_indices[node] to i
            # Remove the cycle by keeping the part of the path before the cycle
            shortest_path = shortest_path[:node_indices[node] + 1] + shortest_path[i + 1:]
            node_indices = {node: index for index, node in enumerate(shortest_path)}  # Update node_indices
        else:
            node_indices[node] = i  # No cycle detected, update node_indices

    # Ensure the optimized path starts and ends with the correct nodes
    if shortest_path[0] != start_node_index:
        shortest_path.insert(0, start_node_index)
    if shortest_path[-1] != end_node_index:
        shortest_path.append(end_node_index)

    return shortest_path


def find_shortest_path_tsp(adj_matrix, start_node_id, end_node_id, df):
    start_node_index = df[df['_id'] == start_node_id].index[0]
    print("\n\n\n\n\n\n")
    print(end_node_id)
    print(df['_id'])
    print(df['_id'] == end_node_id)
    print(df[df['_id'] == end_node_id].index[0])
    print(df[df['_id'] == end_node_id].index[0])
    print(df[df['_id'] == end_node_id].index[0])
    print(df[df['_id'] == end_node_id].index[0])
    print(df[df['_id'] == end_node_id].index[0])
    end_node_index = df[df['_id'] == end_node_id].index[0]
    print(start_node_index, end_node_index)

    # Duplicate each node 2 times
    copies = 2
    new_adj_matrix = duplicate_nodes(adj_matrix, copies)

    new_start = start_node_index
    new_end = end_node_index + len(adj_matrix)

    print(new_start, new_end)

    # Solve TSP on the new graph
    shortest_path_length, shortest_path = tsp(new_adj_matrix, new_start, new_end)

    print(shortest_path_length, shortest_path)

    # Adjust the node indices in the path to reflect the original node indices
    n = len(adj_matrix)
    shortest_path = [node % n for node in shortest_path]

    shortest_path = optimize_path(shortest_path, start_node_index, end_node_index, df)

    print(df)
    # by dataframe index sort the df
    df = df.reindex(shortest_path)
    df = df.reset_index()
    print(df)

    return shortest_path_length, shortest_path, df


def find_shortest_path(shortest_path, filtered_data):
    start_lat = shortest_path.latitude
    start_lon = shortest_path.longitude
    destination_location = ObjectId(shortest_path.destination_id)

    # add start location to the dataframe
    filtered_data = pd.concat([filtered_data, pd.DataFrame([["start", "Current Location", start_lat, start_lon]],
                                                           columns=['_id', 'name', 'latitude', 'longitude'])],
                              ignore_index=True)

    # save csv
    filtered_data.to_csv('filtered_data_2.csv', index=False)

    start_node_id = "start"

    adj_matrix = create_adjacency_matrix(filtered_data)
    shortest_path_length, shortest_path, filtered_data = find_shortest_path_tsp(adj_matrix, start_node_id,
                                                                                destination_location, filtered_data)
    print(f'Shortest path: {shortest_path}')
    print(f'Shortest path length: {shortest_path_length}')

    # show all columns in the dataframe
    pd.set_option('display.max_columns', None)

    return filtered_data
