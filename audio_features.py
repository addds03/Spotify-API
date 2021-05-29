
import datetime as dt
import json
import csv
import requests as req
import pandas as pd
from credentials.getAccessToken import GetAccessToken

def write_audio_features(id, token, writer):
    """
    writes audio features to the file
    """
    try:
        end_point = 'https://api.spotify.com/v1/audio-features/'+id
        header = get_header(token)
        response = req.get(end_point, headers=header)
        data = response.json()
    
        writer.writerow([id, data['danceability'],data['energy'],data['key'],data['loudness'],
                                 data['mode'],data['speechiness'],data['acousticness'],
                                 data['instrumentalness'],data['liveness'],
                                 data['valence'],data['tempo']])
    except (KeyError, TypeError):
        writer.writerow([id, '','','','','','','','','','',''])
    
def get_header(token):
    """
    Creates request header
    """

    return {
        'Accept':'application/json',
        'Content-Type' : 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
def get_trackID(track, token):
    """
    Creates a request url for getting track Id, returns Id if present else continue
    """
    end_point = 'https://api.spotify.com/v1/search'
    header = get_header(token)
    param = {
                ('q', track),
                ('type', 'track'),
            }
    track_id = None

    response = req.get(end_point, headers=header, params=param)
    data = response.json()
        
    try:
        track_id = data['tracks']['items'][0]['id']
    except:
        pass    
    
    return track_id    

def istokenexpired(data):
    """
    Check if access token is expired
    """

    now = dt.datetime.now()
    expires_at = dt.datetime.fromisoformat(data['token_expires_at'])
    return now > expires_at

# Issue of 1st time token not yet resolved
def get_token(auth_code):
    """
    Performs authorization and requests for access token or refresh token based on token expiry
    """

    data = None 

    if auth_code != None:
        token_class = GetAccessToken(auth_code, client_id, client_secret, 'authorization_code')
        # auth code invalid or we already have access code
        if not token_class.token_request():
            try:
                data = load_file('codebase/credentials/token.json')
                 # access token expired get refresh token
                if istokenexpired(data):
                    auth_code = data['refresh_token']
                    token_class = GetAccessToken(auth_code, client_id, client_secret, 'refresh_token')
                    if not token_class.token_request():
                        raise Exception('Use getAuthCode.ipynb to change the authorization code in config file')
            except FileNotFoundError:
                print('token file not found')
    
    return data['access_token']

def load_file(path):
    f = open(path)
    return json.load(f)

def get_credentials():
    """
    Reads credentials from file
    """

    try:
        cred = load_file('codebase/credentials/config.json')
        auth_code = cred['auth_code']
        client_id = cred['client_id']
        client_secret = cred['client_secret']
    except FileNotFoundError:
        print('Manually Create a config file')

    return auth_code, client_id, client_secret

if __name__ == '__main__':
    
    access_token = None
    auth_code = None
    client_id = None
    client_secret = None
    
    # reads credentials
    auth_code, client_id, client_secret = get_credentials()
    
    # requests for access token
    access_token = get_token(auth_code)

    # get track IDs
    df_streams = pd.read_csv('MyData/mystreams.csv')
    distinct_tracks = df_streams.drop_duplicates(subset='track_name')
    distinct_tracks['track_id'] = distinct_tracks['track_name'].apply(get_trackID, token=access_token)         
    distinct_tracks.drop(columns=['end_time','artist_name','milliseconds','played,minutes','played','date','time','day','month'], axis=1, inplace=True)
    distinct_tracks.to_csv('MyData/trackIds.csv', index= False)
   
    # request for audio features
    audio_features = open('MyData/audio_features.csv', 'w', newline= '', encoding='UTF-16')
    dataWriter = csv.writer(audio_features)
    dataWriter.writerow(['id','danceability','energy','key','loud','mode','speech','acoustics',
                        'instrumentals','liveness','valence','tempo'])

    distinct_tracks['track_id'].apply(write_audio_features, token=access_token, writer=dataWriter)
    audio_features.close()

