import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import json
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, output_file, show
from bokeh.transform import factor_cmap

with open("US_category_id.json") as f:                      # open the json file, load into dict
    json_map = json.load(f)

translation = {}                                            # create map for categoryId and category and number of vids
for i in json_map.get("items"):
    translation[int(i["id"])] = {'category': i["snippet"].get("title"), 'count': 0}


def convertID(x):                                           # create lambda function to apply map
    return translation[x].get('category')


df = pd.read_csv("US_youtube_trending_data.csv")            # open the US YT Trending data
df.info()

del df['comments_disabled']                                 # remove extraneous information
del df['ratings_disabled']
del df['video_id']

df['publishedAt'] = pd.to_datetime(df['publishedAt'])       # convert to datetime type
df['trending_date'] = pd.to_datetime(df['trending_date'])
df.info()

df['category'] = df['categoryId'].apply(lambda x: convertID(x))

fig_dims = (16, 9)                                          # create bigger graph
fig, ax = plt.subplots(figsize=fig_dims)

#sns.scatterplot(x='trending_date', y='view_count', data=df, palette='pastel', hue='category', ax=ax).set_title('views over time')
#plt.show()

#sns.scatterplot(x='likes', y='dislikes', data=df, palette='flare', hue='view_count', ax=ax).set_title('likes/dislikes ratio')
#plt.show()

sns.regplot(x='likes', y='dislikes', data=df, ax=ax).set_title('likes/dislikes linear fit')
plt.show()

count = pd.DataFrame(translation, index=['category', 'count'])
count = count.T                                             # Swap cols and rows
count = count.drop(34)                                      # Delete duplicate category (2nd comedy)
print(count.columns)

for i in df['category']:                                    # Count num of videos per category
    for j in count.index:
        if count['category'][j] == i:
            count['count'][j] += 1

for i in count.index:                                       # Remove categories with 0 trending videos
    if count['count'][i] == 0:
        count = count.drop(i)

count = count.sort_values(ascending=False, by=['count'])    # Sort by number
print(count.index)

# Use bokeh to create bar graph of most popular trending categories

output_file("categories.html")
source = ColumnDataSource(data=dict(categories=count['category'], total=count['count']))

# define custom color palette
colors = ('#53b3cb', '#7db7a4', '#a6bb7d', '#f9c22e', '#f7a834', '#f58e3a',
          '#f15946', '#ed4a49', '#e93a4b', '#e01a4f', '#ab163f', '#76122e', '#410e1e', '#270c16', '#0c090d')

p = figure(x_range=count['category'], plot_width=1600, plot_height=900, title="Youtube Trending Categories")
p.vbar(x='categories', top='total', width=1, source=source, legend_field='categories', line_color='white',
       fill_color=factor_cmap('categories', palette=colors, factors=count['category']))

p.xgrid.grid_line_color = None
p.legend.orientation = 'vertical'
p.legend.location = 'top_right'
p.y_range.start = 0
show(p)