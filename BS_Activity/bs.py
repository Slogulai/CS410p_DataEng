import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re

# Set pandas display options to avoid truncation
#pd.set_option('display.max_colwidth', None)  # Prevent truncation of column content
#pd.set_option('display.max_columns', None)  # Show all columns
#pd.set_option('display.width', None)        # Adjust the display width to fit the terminal


from urllib.request import urlopen
from bs4 import BeautifulSoup

url = "http://www.hubertiming.com/results/2017GPTR10K"
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
print(df7.head())