import requests as r

CLIENT_ID = "3j7rkgete6i4erp2fhaulae3nt"
CLIENT_SECRET = "197260bg7nl54nbiekalna1iq6e4sf44ihcqrqh8t00q8d2uhs1p"
COGNITO_TOKEN_ENDPOINT = "https://minecraft-user-pool.auth.us-west-2.amazoncognito.com/oauth2/token"


def f():

    body = {"grant_type": "client_credentials", "scope": ["openid"]}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = r.post(url=COGNITO_TOKEN_ENDPOINT, data=body, auth=(CLIENT_ID, CLIENT_SECRET), headers=headers)

    return response.json()["access_token"]


print(f())
