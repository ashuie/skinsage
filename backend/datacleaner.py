import pandas as pd
import re

raw_data = pd.read_csv("./data/skincare.csv")
#raw_data.info()

df = raw_data.dropna()
df.drop(labels = "URL", axis = 1, inplace = True)
#df.info()

name_pattern = [r'\b\w+ml\b\ ?', r'\b\w+mL\b', r'\b\w+mL\b\ ?', r'\b\w*_+\w*\b', \
                r'\[.*?\]', r'(?i:special)\ ?', r'(?i:double)\ ?', \
                r'(?i:pack)\ ?', r'(?i:set)\ ?', r'(?i:refill)\ ?', r'\(.*?\)', r'\ \+\ ?' \
                r'(?i:duo)\ ?']

for i in range(len(df)):
    text = df.loc[i, "name"]
    for pattern in name_pattern:
        matches = re.findall(pattern, text)
        for match in matches:
            text = text.replace(match, '')
    df.loc[i, "name"] = text.strip()
df_2 = df.sort_values("price", ascending=True).drop_duplicates("name").sort_index()
df = df.loc[df_2.index, :].reset_index(drop = True)

# drop "USD" from prices
price_pattern = re.compile(r'(\d+.\d{2})')
#print(len(df))
for i in range(len(df)):
    df.loc[i, "price"] = re.findall(price_pattern, df.loc[i, "price"])[0]
    #print(df.loc[i, "price"])
df["price"] = pd.to_numeric(df["price"])

df.fillna({"rating": 0}, inplace = True)

# add columns for skin types
for j in range(len(df)):
    df.loc[j, "skin type"] = str(df.loc[j, "skin type"]).replace(",", "|").strip("\"")

df_3 = df['skin type'].str.get_dummies()
df = df.join(df_3).drop('skin type', axis = 1)

#df.drop(['level_0', 'index'], axis = 1, inplace = True)
#df = df.reset_index()
df.to_csv('data/skincare_cleaned.csv', encoding = 'utf-8-sig', index = False)
