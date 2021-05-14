
from credentials.getAccessToken import GetAccessToken


if __name__ == '__main__':
    client_id = 'f6809b3b21a44a2b9279c36507f78c15'
    client_secret = '19b35fc517c744afa580df79b89136e2'

    token = GetAccessToken(client_id, client_secret)
    auth = token.perform_authorization()

    print(token.access_token)