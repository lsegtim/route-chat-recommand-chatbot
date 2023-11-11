import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv("interactions.csv")

# plot rating distribution
df['rating'].value_counts().plot(kind='bar')
plt.show()

# plot rating distribution with count
df['rating'].value_counts().plot(kind='bar')
for index, value in enumerate(df['rating'].value_counts()):
    plt.text(index, value, str(value))
plt.show()
