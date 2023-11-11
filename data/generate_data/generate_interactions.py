import random

import pandas as pd

users = pd.read_csv("users.csv")
locations = pd.read_csv("locations.csv")

# add id to each dataframes
users['id'] = users.index
locations['id'] = locations.index

# create new dataframe as interaction with columns user_id, location_id, rating
interactions = pd.DataFrame(columns=["user_id", "location_id", "rating"])

# create 300 interactions with random user_id, location_id, rating (1-5)
for i in range(300):
    # get random user_id
    user_id = users['id'].sample().values[0]
    # get random location_id
    location_id = locations['id'].sample().values[0]
    # get random rating
    rating = random.randint(1, 5)

    # add data to interactions with concat
    interactions = pd.concat([interactions, pd.DataFrame([[user_id, location_id, rating]],
                                                         columns=["user_id", "location_id", "rating"])],
                             ignore_index=True)

# save interactions to csv
interactions.to_csv("interactions.csv", index=False)
