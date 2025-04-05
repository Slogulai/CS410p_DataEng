import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re

# pandas display options
# pd.set_option('display.max_colwidth', None)  # Prevent truncation of column content
pd.set_option('display.max_columns', None)  # Show all columns
#pd.set_option('display.width', None)        # Adjust the display width to fit the terminal


from urllib.request import urlopen
from bs4 import BeautifulSoup

#url = "http://www.hubertiming.com/results/2017GPTR10K"
url = "http://www.hubertiming.com/results/2023WyEasterLong"
html = urlopen(url)

soup = BeautifulSoup(html, 'html.parser')
type(soup)

#Retrieving and printing the title
title = soup.title
#print(title)
#Retrieving and printing the text
text = soup.get_text()
#print(soup.text)

#Find all anchor elements
anchors = soup.find_all('a')
#print(anchors)
#^^^Can also search for other taga within the html
allinks = soup.find_all('a')
#for link in allinks:
#    print(link.get('href'))

#Find all table elements
rows = soup.find_all('tr')
#print(rows[:10])

for row in rows:
    row_td = row.find_all('td')
#print(row_td)
#type(row_td)

#BeautifulSoup.element.ResultSet

#str_cells = str(row_td)
#cleantext = BeautifulSoup(str_cells, "html.parser").get_text()
#print(cleantext)

list_rows = []
for row in rows:
    cells = row.find_all('td')
    str_cells = str(cells)
    clean = re.compile('<.*?>')
    clean2 = (re.sub(clean, '',str_cells))
    list_rows.append(clean2)
#print(clean2)
#type(clean2)

df = pd.DataFrame(list_rows)
#print(df.head(10))

col_labels = soup.find_all('th')
all_header = []
col_str = str(col_labels)
cleantext2 = BeautifulSoup(col_str, 'html.parser').get_text()
all_header.append(cleantext2)
#print(all_header)


df1 = df[0].str.split(',', expand=True)
df1[0] = df1[0].str.strip('[')
#print(df1.head(10))

df2 = pd.DataFrame(all_header)
#print(df2.head())

df3 = df2[0].str.split(',', expand=True)
#print(df3.head())

frames = [df3, df1]
df4 = pd.concat(frames)
#print(df4.head(10))

df5 = df4.rename(columns=df4.iloc[0])
#print(df5.head())

#df5.info()
#df5.shape

df6 = df5.dropna(axis=0, how='any')
#df6.info()
df6.shape

df7 = df6.drop(df6.index[0])
#print(df7.head())

df7.rename(columns={'[Place': 'Place',}, inplace=True)
df7.rename(columns={' Team]': 'Team',}, inplace=True)
#print(df7.head())

if 'Team' in df7.columns:
    df7['Team'] = df7['Team'].str.strip(']')
#print(df7.head())

time_list = df7[' Time'].tolist()
time_mins = []
for i in time_list:
    sections = i.split(':')
    if len(sections) == 3:  
        h, m, s = sections
        math = (int(h) * 60) + int(m) + (int(s) / 60)
    elif len(sections) == 2:  
        m, s = sections
        math = int(m) + (int(s) / 60)
    else:  
        math = 0  
        print(f"Unexpected time format: {i}")
    time_mins.append(math)

df7['Runner_mins'] = time_mins
#print(df7.head())
df7.describe(include=[np.number])

from pylab import rcParams
rcParams['figure.figsize'] = 15, 5


df7.boxplot(column='Runner_mins')
plt.grid(True, axis='y')
plt.ylabel('Chip Time')
plt.xticks([1], ['Runners'])
x = df7['Runner_mins']

ax = sns.displot(x=x, kde=True, color='m', bins=25, edgecolor="black")

plt.figure(figsize=(15, 5))

f_fuko = df7.loc[df7[' Gender']==' F']['Runner_mins']
m_fuko = df7.loc[df7[' Gender']==' M']['Runner_mins']

sns.histplot(f_fuko, kde=True, edgecolor='black', color='skyblue', alpha=0.6, label='Female (hist)')
sns.kdeplot(f_fuko, color='blue', linewidth=2, label='Female (kde)')

ax2 = plt.twinx()
sns.kdeplot(m_fuko, color='orange', linewidth=2, label='Male', ax=ax2)

handles, labels = plt.gca().get_legend_handles_labels()
handles2, labels2 = ax2.get_legend_handles_labels()
plt.legend(handles + handles2, labels + labels2, loc='best')

ax2.set_ylabel('')

plt.xlabel('Runner Minutes')
plt.title('Distribution of Runner Times by Gender')
#plt.show()

g_stats = df7.groupby(" Gender", as_index=True).describe()
print(g_stats)

df7.boxplot(column='Runner_mins', by=' Gender')
plt.ylabel('Chip Time')
plt.suptitle("")
plt.show()