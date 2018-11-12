#! /usr/bin/python3
import requests, sys
from bs4 import BeautifulSoup
import re, string, csv
table = string.maketrans("","")

id = "1SUyNzBHIsXSuASnpHZlxUedJWuvdU8XRRN8D-09G4wAkeO_a4sM1NKwfzqx_THU"
secret = "0F9WCLEmUrnUuMVcLL4-vsq4fsr-paqhZNh3vDPiPEYjTJAsx9_ed6v_EevoHWH8uzPauoOFC2g5WX63dtUuKg"
token = "0_K6SUclwrf344XpYJdXSGEddeaV0eCcMsK8SgFeIKNQeAkoLiTOyfOZbLzeDagw"
base_url = "http://api.genius.com"

def request_song_info(song_title, artist_name):
    """Input  = artist name and song
       Output = the json response from Genius API
    """
    base_url = 'https://api.genius.com'
    headers = {'Authorization': 'Bearer ' + token}
    search_url = base_url + '/search'
    data = {'q': song_title + ' ' + artist_name}
    response = requests.get(search_url, data=data, headers=headers)
    json = response.json()
    remote_song_info = None
    return response

def parse_lyrics(url):
    """Input  = artist/song URL
       Output = scrape the lyrics
    """
    page = requests.get(url)
    html = BeautifulSoup(page.text, 'html.parser')
    lyrics = html.find('div', class_='lyrics').get_text()
    return lyrics

def clean(lyrics, numbers=False, lower=False):
    """Input  = lyrics
       Output = cleaned version of the lyrics in tokenized form
       We can tokenize, count the number of words, look
       at the word frequency, unique words, etc
    """
    if not lyrics:
        return []
    print("-removing verse/chorus identifiers,"),
    output = re.sub("[\[].*?[\]]", "", lyrics)
    print("punctuation,"),
    output = re.sub(r'[^\w\s]', '',   output)
    if numbers:
        output = re.sub(r'[^a-zA-Z]',' ', output)
        print("and anything non-alpha."),
    if lower:
        output = output.lower()
        print("Lower casing too.")

    # Do a small analysis
    tokens = [s.strip() for s in output.split() if s] 
    unique_words = {}
    for w in tokens:
        if w in unique_words:
            unique_words[w] += 1
        else:
            unique_words[w] = 1

    print("-word count: %d" % len(tokens) )
    print("-unique word count: %d" % len(unique_words) )
    print("-most frequent words:"),
    # Print the top 5 most frequently used songs
    top5=1
    for w in sorted(unique_words, key=unique_words.get, reverse=True):
        print("%s (%d), " % (w,unique_words[w]) ),
        if top5 >= 5:
            break
        top5 += 1
    print("\n")
    return tokens
        
def get_lyrics(song,name):
    """ Driver function
    """
    print("\nSearching for %s by %s" % (song,name) )
    response = request_song_info(song,name)
    json = response.json()
    remote_song_info = None

    for hit in json['response']['hits']:
        if name.lower() in hit['result']['primary_artist']['name'].lower():
            remote_song_info = hit
            break

    song_url,lyrics,cleaned=None,None,None
    if remote_song_info:
        song_url = remote_song_info['result']['url']
    else:
        print("Could not find it")
         
    if song_url:
        lyrics = parse_lyrics(song_url)
        cleaned = clean(lyrics,True, True)
    else:
        print("Returning empty string b/c %s was not found" % song)
    return cleaned

################################################################################
# Bring in the CSV file, which contains all the songs/artists
#
# Bring in our list of songs to look up
songs, artists, yrs, top100 = {}, {}, {}, {}
years = []
with open('billboard_ye_topartists.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    count = 0
    for row in csv_reader:
        yrs[count]     = row[0]
        top100[count]   = row[1]
        songs[count]   = row[2]
        artists[count] = row[3]
        years.append(int(row[0]))
        count += 1

years.sort()
print("Will look for %d songs spanning the years %d-%d" % (len(songs),years[0],years[-1]))

##################################################
def clean_up_artist(artist):
    """If artist has a feature, remove it
       Remove any trailing white space
    """
    if artist.find("Featuring") == -1:
        return artist.rstrip() 
    else:
        return artist[:artist.find('Featuring')].rstrip()

#get_lyrics("Caroline","Amin")
    
f = open('song_lyrics.csv','w')
did_not_find = []
count = 1
for row, song in songs.items():
    song = song
    artist = clean_up_artist( artists[row] )
    if "beyonc" in artist.lower():
        artist = "beyonc"
        
    lyrics = get_lyrics(song, artist)  # This function does not work with trailing white-space
    yr = yrs[row]
    number = top100[row]
    line =  yr + "," + number + "," + "\"" + song + "\"," + "\"" + artist + "\"," + "\""
    if lyrics:
        for w in lyrics:
            line += w + " "    
        line += "\""   
    else:
        line += "\""
        did_not_find.append(song)
    line += "\n"    
    f.write(line)
    print("%d / %d" % (count, len(songs)))
    count += 1

# If there were parsing issues, report it
if did_not_find:   
    print("\nCould not find the following (%d):" % len(did_not_find))
    print(did_not_find)
    
f.close()
