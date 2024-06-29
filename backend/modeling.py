import pandas as pd
import numpy as np
import re
from sklearn.manifold import TSNE

#np.seterr(divide='ignore', invalid='ignore')

global skincare_df
skincare_df = pd.read_csv('./data/skincare_cleaned.csv')
prod_types = skincare_df.Label.unique().tolist()
skin_types = skincare_df.columns[6:].tolist()

# dimension reduction using t-SNE
def tsne_map(op1, op2):
    df = skincare_df[(skincare_df['Label'] == op1) & (skincare_df[op2] == 1)]
    df = df.reset_index(drop = True)
    #print(df)
    ingredient_dict = {}
    corpus = []
    index = 0
    for i in range(len(df)):
        #print(op1 + " " + op2)
        #print("index " + str(i) + " " + op1 + " " + op2 + df.loc[i, "name"])
        tokens = df.loc[i, "ingredients"]
        tokens = tokens.lower().split(", ")
        tokens = re.sub(r"[\(\[].*?[\)\]]", "", str(tokens))
        corpus.append(tokens)
        for ingredient in tokens:
            if ingredient not in ingredient_dict:
                ingredient_dict[ingredient] =  index
                index += 1
    
    m = len(df)
    n = len(ingredient_dict)
    a = np.zeros(shape = (m, n))

    def encoder(tokens):
        column = np.zeros(n)
        for t in tokens:
            i = ingredient_dict[t]
            column[i] = 1
        return column
    
    j = 0
    for tokens in corpus:
        a[j, :] = encoder(tokens)
        j += 1
    #print(str(a.shape[0]) + " x " + str(a.shape[1]))
    

    model = TSNE(n_components = 2, learning_rate = 200)
    try: 
        tsne_features = model.fit_transform(a)
    except ValueError:
        model = TSNE(n_components = 2, perplexity = len(df) - 2, learning_rate = 200)
        tsne_features = model.fit_transform(a)
        
    df.insert(10, "x", pd.Series(tsne_features[:, 0]))
    df.insert(11, "y", pd.Series(tsne_features[:, 1]))

    return df

df_tsne = pd.DataFrame()
for p in prod_types:
    for s in skin_types:
        temp = tsne_map(p, s)
        temp["Label"] = p + "_" + s
        df_tsne= pd.concat([df_tsne, temp])
    #print(df_tsne)

df_tsne.to_csv('data/skincare_tsne.csv', encoding = 'utf-8-sig', index = False)