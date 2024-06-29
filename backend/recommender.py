import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# precondition: df["name"] contains item_name, num < len(df["name"])
# takes a string item_name and integer num and returns the top num closest products to item_name
def recommender(item_name, skin_type, num):
    df = pd.read_csv('data/skincare_tsne.csv')
    df = df[df["Label"].str.contains(skin_type)].reset_index(drop = True)
    df["dist"] = 0.0
    searched_item = df[df["name"].str.contains(item_name, regex=False)]

    p1 = np.array([searched_item["x"].values, searched_item["y"].values]).reshape(1, -1)
    if p1.size == 0:
        return None

    for i in range(len(df)):
        if (item_name not in df.loc[i, "name"] and item_name != df.loc[i, "name"]):
            p2 = np.array([df.loc[i, "x"], df.loc[i, "y"]]).reshape(1, -1)
            df.loc[i, "dist"] = 1 - cosine_similarity(p1, p2)
        else:
            df.loc[i, "dist"] = None

    df = df.sort_values("dist", key = abs, ascending = True)
    df = df.drop(df.index[df['dist'] < 0])
    #print(df[['name', 'brand', 'dist']].head(10))
    return df[['name', 'brand', 'dist']].head(num)

#print(recommender("numbuzin No.5+ Vitamin Concentrated Serum", "Combination&Normal", 10))