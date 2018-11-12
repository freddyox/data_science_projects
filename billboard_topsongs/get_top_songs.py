#! /usr/bin/python3

######################################################################
# Goal of this script:
#
# Scrape Billboard's year-end top-100 list for artist and song title
#
# We have 2006 to 2017 available in this particular format, e.g.
# https://www.billboard.com/charts/year-end/2017/hot-100-songs

import requests
from bs4 import BeautifulSoup

years = range(2006, 2018, 1)

def get_site_text(year):
    """Utility function to get the url text given a year
    # Args:   year
    # Output: the full html text (this might be expensive)
    """
    url = 'https://www.billboard.com/charts/year-end/' + year + '/hot-100-songs'
    print(url)
    r = requests.get(url)
    return r.text

def get_artists(parse_class):
    """Grab the correct HTML info, parse it and build a data container
    # Args:   class argument, what to sniff out in the html file
    # Output: list (artist,song)
    """
     # note temp[0].contents returns [u'\nShape Of You\n']
    text = parse_class.text.strip()
    # We strip white spaces, line split, and ignore empty lines hence "if s"
    info = [s.strip() for s in text.splitlines() if s] 
    if len(info) is not 2:
        print('There might be something wrong here...', info)
    return info
    
    
# Driver code
everything = {}
for yr in years:
    soup = BeautifulSoup( get_site_text(str(yr)), "html.parser")
    find_class = soup.find_all("div", class_="ye-chart-item__text")

    # Get the necessary information from the page
    all_artists = {}
    index = 1
    for t in find_class:
        all_artists[index] = get_artists(t)
        index += 1
    everything[yr] = all_artists    

# spit everything out to a text file
f = open('billboard_ye_topartists.csv', 'a')

for yr in sorted(everything.iterkeys()):
    info = everything[yr]
    for rank, artist in info.items():
        line = str(yr) + "," + str(rank) + ","
        for a in range(len(artist)):
            # We want to protect against too many columns
            if not artist[a]:
                continue
            # Let's make it a csv, ignore comma for last entry
            if a<len(artist)-1:
                line += "\"" + artist[a] + "\","
            else:
                line += "\"" + artist[a] + "\"\n"
        # Let's print the string
        f.write(line)
        #print(line)

f.close
