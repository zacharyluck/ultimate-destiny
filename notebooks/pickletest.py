# this file is just so I can explore what is inside of
# manifest.pickle, as well as the code that will be used to
# load the pickled dict later.

import pandas as pd


# load dict from pickle thru pandas into dataframe
f = pd.read_pickle('manifest.pickle')
df = pd.DataFrame.from_dict(f)

print(df.shape)
print(df.head())
print(df.tail())
