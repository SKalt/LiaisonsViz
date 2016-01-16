# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 14:49:57 2015
Liaisons Scraper
@author: steven

This program extracts relationships beteween characters from the wikisource 
version of Les Liaisons Dangereuses
"""

#%% import block
import pandas as pd
from lxml import html
import urllib3 as ul3
from io import BytesIO
import re
#%% Get the initial page
indexUrl = "https://fr.wikisource.org/wiki/Les_Liaisons_dangereuses"
# the url of the index page
addressesXPath = '//*[@id="mw-content-text"]/div/ul/li/text()'
hrefsXPath = '//*[@id="mw-content-text"]/div/ul/li/a/@href'
# XPath addresses of the strings describing the senders and the recipients of
# each letter and the url of the wikisource version of each letter, 
#respectively 

# extracting the required data from the page
http = ul3.PoolManager()
page = http.request('GET', indexUrl)
data = page.data 
pageStructure = html.parse(BytesIO(data))
addresses = pageStructure.xpath(addressesXPath)
lettersUrls = pageStructure.xpath(hrefsXPath)
#%% parse out who's writing whom

# split addresses  by ' au ' and ' à '
fromTo1 = [re.split(" à| au ", x) for x in addresses]

# make all strings upper case 
fromTo2 = []
for i in enumerate(fromTo1):
    fromTo2.append([j.upper() for j in i[1]])

# remove all particules from the beginnings of addresses
fromTo3 = fromTo2
for i in enumerate(fromTo2):
    firstWord = i[1][0].split()[0]
    if len(firstWord) == 2: # if there is a particule as the first word
        fromTo3[i[0]][0] = ' '.join(i[1][0].split()[1::])

# remove padding spaces from all entries
fromTo4 = fromTo3
for i in enumerate(fromTo3):
    fromTo4[i[0]] = [j.strip() for j in i[1]]
        
# check all letters have one sender and one recipient
for i in enumerate(fromTo4):
    if len(i[1]) != 2:
        print(i)
# the first is a response.  Thus, we will need to reverse the letter at 
# index 11 to create that at 12.  
fromTo4[12] = fromTo4[11][::-1] 
# re-check
for i in enumerate(fromTo4):
    if len(i[1]) != 2:
        print(i)

#%%
# how many characters are there in the book?
listOChars = []
for i in fromTo4:
    for j in i:
        listOChars.append(j)
len(set(listOChars)) # looks like there are around 30.  Comparing this with 
# SparkNotes' list of characters, ther are 12 more than usual.I'm going to 
# manually disambiguate them:
manualDisambig = {
'MADAME DE TOURVEL':'MADAME TOURVEL',
'LA PRÉSIDENTE DE TOURVEL':'MADAME TOURVEL',
'PRÉSIDENTE TOURVEL':'MADAME TOURVEL',
'MADAME LA PRÉSIDENTE TOURVEL':'MADAME TOURVEL',
'MADAME LA PRÉSIDENTE DE TOURVEL':'MADAME TOURVEL',
'PRÉSIDENTE DE TOURVEL':'MADAME TOURVEL',
'LA PRÉSIDENTE TOURVEL': 'MADAME TOURVEL',

'LA MARQUISE DE ROSEMONDE':'MADAME DE ROSEMONDE',

'LA MARQUISE DE MERTEUIL': 'MARQUISE DE MERTEUIL',
'MADAME LA MARQUISE DE MERTEUIL':'MARQUISE DE MERTEUIL',
"MADAME DE MERTEUIL" : 'MARQUISE DE MERTEUIL',

'BILLET DE SOPHIE (SIC) VOLANGES':'CÉCILE VOLANGES',
'MONSIEUR LE CHEVALIER DANCENY':'CHEVALIER DANCENY',
'AZOLAN SON CHASSEUR': 'AZOLAN',
}

for i in enumerate(listOChars):
    if i[1] in manualDisambig:
        listOChars[i[0]] = manualDisambig[i[1]]
len(set(listOChars)) # better-- down to 17
# now apply the disambiguation to the addresses
fromTo5 = fromTo4 
for i in enumerate(fromTo5): 
    for j in enumerate(i[1]):
        if j[1] in manualDisambig:
            fromTo5[i[0]][j[0]] = manualDisambig[fromTo5[i[0]][j[0]]]

#%% create an ordered edgelist
edgelist = 0
edgelist = pd.DataFrame(fromTo5)
edgelist.columns = ["Source", "Target"]
edgelist["LetterNumber"] = range(1,len(fromTo5) + 1)
edgelist.to_csv('LiaisonsDangereusesEdgelist.tsv', sep= '\t', index = False)
#%% retrieve the dates from each of the letters 
#dateXPath = '//*[@id="mw-content-text"]/div/p'
#allText = []
#for url in lettersUrls: 
#    realUrl = 'fr.wikisource.org' + url
#    r = http.request('GET', realUrl)
#    data = r.data
#    structure = html.parse(BytesIO(data))
#    paragraphs = structure.xpath(dateXPath)
#    allText.append([url, paragraphs])
#    
##%%    
#for i in allText:
#    last = i[1][len(i[1])-1].text
#    print(last)

     