
import datetime as dt
import json
import requests as req
import pandas as pd
from credentials.getAccessToken import GetAccessToken


def get_header(token):
    return {
        'Accept':'application/json',
        'Content-Type' : 'application/json',
        'Authorization': f'Bearer {token}'
    }

def get_parameter(track):
    return {
        ('q', track),
        ('type', 'track'),
    }

def get_trackIDs(track, token):
    
    end_point = 'https://api.spotify.com/v1/search'
    header = get_header(token)
    param = get_parameter(track)
    track_id = None

    response = req.get(end_point, headers=header, params=param)
    data = response.json()
    
    try:
        track_id = data['tracks']['items'][0]['artists'][0]['id']
    except:
        print(data)

    return track_id
    
def istokenexpired(data):
    now = dt.datetime.now()
    expires_at = dt.datetime.fromisoformat(data['token_expires_at'])
    return now > expires_at

def load_file(path):
    f = open(path)
    return json.load(f)

if __name__ == '__main__':
    
    access_token = None
    data = None
    auth_code = None
    client_id = None
    client_secret = None
    
    try:
        cred = load_file('codebase/credentials/config.json')
        auth_code = cred['auth_code']
        client_id = cred['client_id']
        client_secret = cred['client_secret']
    except FileNotFoundError:
        print('Manually Create a config file')

    # Issue of 1st time token not yet resolved
    if auth_code != None:
        token_class = GetAccessToken(auth_code, client_id, client_secret, 'authorization_code')
        # auth code invalid or we already have access code
        if not token_class.get_tokens():
            try:
                data = load_file('codebase/credentials/token.json')
                 # access token expired get refresh token
                if istokenexpired(data):
                    auth_code = data['refresh_token']
                    token_class = GetAccessToken(auth_code, client_id, client_secret, 'refresh_token')
                    token_class.get_tokens()
            except FileNotFoundError:
                print('Manually Fetch authorization code from and start over')
        
    access_token = data['access_token']

     # get track IDs
    df_streams = pd.read_csv('MyData/mystreams.csv')
    
    track_names = df_streams['track_name']
    
    track_ids = []
    count = 0
    for index, track in enumerate(track_names):
        if index == 332:
            track_ids.append(get_trackIDs(track, access_token))
        #print(count)
        #count = count + 1
        
        #if count == 6:
        #    break

    #print(len(track_ids))    
    #df_streams['track_id'] = df_streams['track_name'].apply(get_trackIDs, token=access_token)
    

    # today = dt.datetime.now()
    # yesterday = today - dt.timedelta(days=1)
    # yesterday_timestamp = int(yesterday.timestamp())

    # endpoint = 'https://api.spotify.com/v1/me/player/recently-played'
    
    # query = f'?limit=50&after={yesterday_timestamp}'

    # r = req.get(f'{endpoint}{query}', headers=headers)
    
    # #r = req.get(f'{endpoint}', headers=headers)    

    # data = r.json()
    
    # song_names = []
    # #release_years = []
    # artist_names = []
    # played_at_list = []
    # timestamps = []

    # for song in data['items']:
    #      song_names.append(song['track']['name'])
    #      #release_years.append(song['track']['release_date'])
    #      artist_names.append(song['track']['album']['artists'][0]['name'])
    #      played_at_list.append(song['played_at'])
    #      timestamps.append(song['played_at'][0:10])
    
    # song_dict = {
    #     'song_names' : song_names,
    #     #'release_years' : release_years,
    #     'artist_names' : artist_names,
    #     'played_at_list' : played_at_list,
    #     'timestamps' : timestamps
    # }

    # df_songs = pd.DataFrame(data= song_dict, columns=['song_names','artist_names','played_at_list','timestamps'])

    # df_songs.set_index('played_at_list', inplace=True, drop=True)
    # print(df_songs.sort_index(ascending=False))
    