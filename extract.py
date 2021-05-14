
import datetime
import json
import requests as req
import pandas as pd
from credentials.getAccessToken import GetAccessToken


def get_headers(token):
    return {
        'Accept':'application/json',
        'Content-Type' : 'application/json',
        'Authorization': f'Bearer {token}'
    }

if __name__ == '__main__':
    client_id = 'f6809b3b21a44a2b9279c36507f78c15'
    client_secret = '19b35fc517c744afa580df79b89136e2'
    access_token = None

    token = GetAccessToken(client_id, client_secret)
    auth = token.perform_authorization()
    
    if auth:
        access_token = token.access_token
    
    headers = get_headers('BQAaboMR7SOBtHZl27BP0Pf93FFQnRLjznnWcDtNxD4dqhVLA_6kFancOIpS1i4G4ijg7_9woy6q_OdKac3tgixbyjWFIrgefTdfV-wWWh9GXboA1llrWKK6S3EDxAcMnmYAneGl96A785e0uyp9Mf2hq775KVxKsA76TGgs')

    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1)
    yesterday_timestamp = int(yesterday.timestamp())

    endpoint = 'https://api.spotify.com/v1/me/player/recently-played'
    query = f'?limit=50&after={yesterday_timestamp}'

    r = req.get(f'{endpoint}{query}', headers=headers)
    data = r.json()

    song_names = []
    #release_years = []
    artist_names = []
    played_at_list = []
    timestamps = []

    for song in data['items']:
         song_names.append(song['track']['name'])
         #release_years.append(song['track']['release_date'])
         artist_names.append(song['track']['album']['artists'][0]['name'])
         played_at_list.append(song['played_at'])
         timestamps.append(song['played_at'][0:10])
    
    song_dict = {
        'song_names' : song_names,
        #'release_years' : release_years,
        'artist_names' : artist_names,
        'played_at_list' : played_at_list,
        'timestamps' : timestamps
    }

    df_songs = pd.DataFrame(data= song_dict, columns=['song_names','artist_names','played_at_list','timestamps'])

    df_songs.set_index('played_at_list', inplace=True, drop=True)
    print(df_songs.sort_index(ascending=False))