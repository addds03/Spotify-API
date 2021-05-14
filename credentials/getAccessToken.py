
import requests as req
import datetime
import base64 as bs64

"""
Class feches token from Spotify API
"""
class GetAccessToken:
    
    token_url = 'https://accounts.spotify.com/api/token'
    client_id = None
    client_secret = None    
    
    access_token = None
    acess_token_expires = datetime.datetime.now()
    access_token_did_expire = True

    def __init__(self, client_id, client_secret, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret

    def get_client_credentials(self):
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

    def get_token_headers(self):
        client_cred64 = self.get_client_credentials()
        return {
            'Authorization': f'Basic {client_cred64}'
            }
        
    def get_token_data(self):
        return {
            'grant_type':'client_credentials'
            }

    def get_token(self, r):
        data = r.json()

        now = datetime.datetime.now()
        acess_token = data['access_token']
        # time is in seconds
        exp = now + datetime.timedelta(data['expires_in'])

        self.acess_token_expires = exp
        self.access_token_did_expire = exp < now

        return acess_token
           
    def perform_authorization(self):

        token_url = self.token_url
        token_data = self.get_token_data()
        token_headers = self.get_token_headers()    
        response = req.post(token_url, data=token_data,headers=token_headers)

        if response.status_code not in (200, 201, 202, 204):
            return False
        self.access_token = self.get_token(response)
        return True