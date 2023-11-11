import pandas as pd

df = pd.read_csv("processed.csv")

# group by user_id and location_id
df = df.groupby(['user_id', 'location_id']).size().reset_index(name='count')

# sort by count
df = df.sort_values(by=['count'], ascending=False)

print(df.head())
