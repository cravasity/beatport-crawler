from bs4 import BeautifulSoup
from url_normalize import url_normalize
import requests
import urllib.parse
import json
import pandas as pd
import time

URL = "https://www.beatport.com/search?q="
URL_TEMPLETE = "https://www.beatport.com/track/%s/%d"

def crawl(song_name):
  headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
  }
  res = requests.get(URL + urllib.parse.quote_plus(song_name), headers=headers)

  if res.status_code != 200:
    errormessage = "[-] error : statue code %d" % res.status_code
    return error(errormessage)

  soup = BeautifulSoup(res.text, "html.parser")
  data_json = json.loads(soup.find("script", id="__NEXT_DATA__").text)

  try:
    data = data_json["props"]["pageProps"]["dehydratedState"]["queries"][0]["state"]["data"]["tracks"]["data"][0]
  except IndexError:
    errormessage = "IndexError"
    return error(errormessage)
  
  genre = data["genre"][0]["genre_name"]
  key = data["key_name"]
  track_name = data["track_name"]
  artist = data["artists"][0]["artist_name"]
  b_url = (URL_TEMPLETE % (data["track_name"], data["track_id"]))

  try:
    bpm = data["bpm"]
  except:
    bpm = "bpm unavailable"

  try:
    length = data["length"]
    total_seconds = length // 1000

    minutes = total_seconds // 60
    seconds = total_seconds % 60

    if seconds < 10:
      length_string = f"{minutes}:0{seconds}"
    else:
      length_string = f"{minutes}:{seconds}"
  except:
    length_string = "length unavailable"

  return genre, bpm, key, track_name, artist, length_string, url_normalize(b_url) 

def error(errormessage):
  return errormessage, errormessage, errormessage, errormessage, errormessage, errormessage, errormessage

def main():
  df = pd.read_csv('./djmix-structure-tracks.csv')
  df = df[df['ok'] != 'x']
  i = 1

  new_rows = []

  for index, row in df.iterrows():
    genre, bpm, key, track_name, artist, length_string, b_url = crawl(str(row["title"]))
    new_row = row.copy()
    new_row["beatport_genre"] = genre
    new_row["bpm"] = bpm
    new_row["key"] = key
    new_row["track_name"] = track_name
    new_row["artist"] = artist
    new_row["length"] = length_string
    new_row["beatport_url"] = b_url
    new_rows.append(new_row)
    print(i, "th iteration complete")
    i = i + 1
    time.sleep(0.1)

  new_df = pd.DataFrame(new_rows)

  new_df.to_csv('new.csv', index=False)

def test():
  #df = pd.read_csv('./djmix-structure-tracks.csv')
  df = pd.read_csv('./new.csv')
  print(df)

if __name__ == "__main__":
  main()