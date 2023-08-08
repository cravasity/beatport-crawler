from bs4 import BeautifulSoup
import requests
import urllib.parse
import json
import pandas as pd
import time

URL = "https://www.beatport.com/search?q="

def crawl(song_name):
  headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
  }
  res = requests.get(URL + urllib.parse.quote_plus(song_name), headers=headers)

  if res.status_code != 200:
    genre = bpm = key = track_name = artist = length_string = "[-] error : statue code %d" % res.status_code
    return genre, bpm, key, track_name, artist, length_string

  soup = BeautifulSoup(res.text, "html.parser")
  data_json = json.loads(soup.find("script", id="__NEXT_DATA__").text)
  try:
    data = data_json["props"]["pageProps"]["dehydratedState"]["queries"][0]["state"]["data"]["tracks"]["data"][0]
  except IndexError:
    return "null", "null", "null", "null", "null", "null"

  try:
    genre = data["genre"][0]["genre_name"]
  except:
    genre = "genre unavailable"

  try:
    bpm = data["bpm"]
  except:
    bpm = "bpm unavailable"

  try:
    key = data["key_name"]
  except:
    key = "key unavailable"

  try:
    track_name = data["track_name"]
  except:
    track_name = "track name unavailable"

  try:
    artist = data["artists"][0]["artist_name"]
  except:
    artist = "artist unavailable"

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

  return genre, bpm, key, track_name, artist, length_string

def main():
  df = pd.read_csv('./djmix-structure-tracks.csv')
  df = df[df['ok'] != 'x']
  i = 1

  new_rows = []

  for index, row in df.iterrows():
    genre, bpm, key, track_name, artist, length_string = crawl(str(row["title"]))
    new_row = row.copy()
    new_row["beatport_genre"] = genre
    new_row["bpm"] = bpm
    new_row["key"] = key
    new_row["track_name"] = track_name
    new_row["artist"] = artist
    new_row["length"] = length_string
    new_rows.append(new_row)
    print(i)
    i = i + 1
    time.sleep(1)

  new_df = pd.DataFrame(new_rows)

  new_df.to_csv('new.csv', index=False)

def test():
  #df = pd.read_csv('./djmix-structure-tracks.csv')
  df = pd.read_csv('./new.csv')
  #df = df[df['ok'] != 'x']

  print(df)
if __name__ == "__main__":
  main()
  #test()