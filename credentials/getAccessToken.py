
import requests as req
import datetime as dt
import base64 as bs64
import json

"""
Class fetches token from Spotify API
"""
class GetAccessToken:
    
    token_url = 'https://accounts.spotify.com/api/token'
    client_id = None
    client_secret = None    
    auth_code = None
    grant_type = None
    
    
    acess_token_expires = dt.datetime.now()

    def __init__(self, auth_code, client_id, client_secret, *args, **kwargs):
        #super().__init__(*args, **kwargs)
        self.auth_code = auth_code
        self.client_id = client_id
        self.client_secret = client_secret
        self.grant_type = args[0]

    def get_client_credential(self):
        """
        Returns a base64 encoded string
        """
        client_id = self.client_id
        client_secret = self.client_secret

        if client_id == None or client_secret == None:
            raise Exception('You must set Client id & Client secret')
        client_credentials = f'{client_id}:{client_secret}'
        client_cred64 = bs64.b64encode(client_credentials.encode())
        return client_cred64.decode()

    def generate_header(self):
        """
        Generates request header
        """
        client_cred64 = self.get_client_credential()
        return {
            'Authorization': f'Basic {client_cred64}'
            }
        
    def generate_body_para(self):
        """
        Generates body request parameters
        """
        grant_type = self.grant_type
        code = self.auth_code
        if grant_type == 'authorization_code':
            return {
            'grant_type': grant_type,
            'code': code,
            'redirect_uri':'https://addds03.github.io/Addy-Portfolio/' 
            }
        elif grant_type == 'refresh_token':
            return {
            'grant_type': grant_type,
            'refresh_token' : code
            }        
    
    def write_token(self, r):
        """
        Writes the access and refresh tokens to a file
        """
        data = r.json()
        now = dt.datetime.now()
        sec = data['expires_in']
        acess_token_expires = now + dt.timedelta(seconds = sec)
        
        refresh_token = None
        acess_token = data['access_token']
        
        if self.grant_type != 'refresh_token':
            refresh_token = data['refresh_token']

        token = {
            'access_token' : acess_token,
            'token_received_at' : now,
            'token_expires_in' : sec,
            'token_expires_at' : acess_token_expires,
            'refresh_token' : refresh_token
            }
  
        def myconverter(o):
            if isinstance(o, dt.datetime):
                return o.__str__()

        with open('codebase/credentials/token.json', 'w') as outfile:
            json.dump(token, outfile, default=myconverter, indent=4)        
           
    def token_request(self):

        token_url = self.token_url
        body_para = self.generate_body_para()
        headers = self.generate_header()
        response = req.post(token_url, data=body_para, headers=headers)
   
        if response.status_code not in (200, 201, 202, 204):
            return False
        
        # writes access token and refresh tokens to a file
        self.write_token(response)
        return True