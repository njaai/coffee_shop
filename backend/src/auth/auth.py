import json
from os import abort
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen


# AUTH0_DOMAIN = 'udacity-fsnd.auth0.com'
# ALGORITHMS = ['RS256']
# API_AUDIENCE = 'dev'

AUTH0_DOMAIN = 'dev--62fql0u.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'coffee'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header

'''
@TODO implement get_token_auth_header() method
    it should attempt to get the header from the request
        it should raise an AuthError if no header is present
    it should attempt to split bearer and the token
        it should raise an AuthError if the header is malformed
    return the token part of the header
'''
token111 = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Im95YUJ0c3dta0hQLWw3NHBkbm43cyJ9.eyJpc3MiOiJodHRwczovL2Rldi0tNjJmcWwwdS51cy5hdXRoMC5jb20vIiwic3ViIjoiZ29vZ2xlLW9hdXRoMnwxMTAzMjY3MDY1NDIzNTI0NDE4MjkiLCJhdWQiOiJjb2ZmZWUiLCJpYXQiOjE2NjMzNDQ4MTMsImV4cCI6MTY2MzM1MjAxMywiYXpwIjoiTXl2b0drZlJzNGtpd2VRMHh6b1J4WnVNd214NVgwMnciLCJzY29wZSI6Im9mZmxpbmVfYWNjZXNzIiwicGVybWlzc2lvbnMiOltdfQ.XBCXsdjtQZqzNKA6mPPI81rQWoYqQunDAFGls7jkxBUNfKtDgK3YDckhJDJ8T0ndmBuITH_-kivzlY7uvxuPVep4gcEopekuZ9986Av8CgC1xs0kCWqEPuepu7M2TN1cul8ZM3wsEu0Lw3pa-v-GFgByHciGzL9JV7ozvaKLO1ohs6cw3r1aV1438MuahKUK1LN1XUvfbnSrIvx3qNgL6pu7_CxtGtmTWfuRt76f-defbKqLjf4CLhDncJE594OQFawIMf_pMP95a25135yBxn_R5MSGdJasP9sx_ylDwxuNistz0xda1xfqWg5RegHfn8r2ROyl-oUlAuThyeJ1Xw"
def get_token_auth_header():
    if 'Authorization' not in request.headers:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed'
        }, 401)
    aut_header = request.headers['Authorization']
    header_parts = aut_header.split(' ')

    if len(header_parts) !=2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed'
        }, 401)
    elif header_parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed'
        }, 401)
    return header_parts[1]
    
    # raise Exception('Not Implemented')
'''
'''

# def requires_auth(f):
#     @wraps(f)
#     def wrapper(*args, **kwargs):
#         jwt = get_token_auth_header()
    
#         return f(jwt, *args, **kwargs)
#     return wrapper
    
'''
@TODO implement check_permissions(permission, payload) method
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload

    it should raise an AuthError if permissions are not included in the payload
        !!NOTE check your RBAC settings in Auth0
    it should raise an AuthError if the requested permission string is not in the payload permissions array
    return true otherwise
'''
def check_permissions(permission, payload):
     if 'permissions' not in payload:
                        raise AuthError({
                            'code': 'invalid_claims',
                            'description': 'Permissions not included in JWT.'
                        }, 400)

     if permission not in payload['permissions']:
        raise AuthError({
            'code': 'unauthorized',
            'description': 'Permission not found.'
        }, 403)
     return True
    # raise Exception('Not Implemented')

'''
@TODO implement verify_decode_jwt(token) method
    @INPUTS
        token: a json web token (string)

    it should be an Auth0 token with key id (kid)
    it should verify the token using Auth0 /.well-known/jwks.json
    it should decode the payload from the token
    it should validate the claims
    return the decoded payload

    !!NOTE urlopen has a common certificate error described here: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
'''
def verify_decode_jwt(token):
     # GET THE PUBLIC KEY FROM AUTH0
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())

    # GET THE DATA IN THE HEADER
    unverified_header = jwt.get_unverified_header(token)


    # CHOOSE OUR KEY
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    
    # Finally, verify!!!
    if rsa_key:
        try:
            # USE THE KEY TO VALIDATE THE JWT
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload
        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
            }, 400)
    # raise Exception('Not Implemented')

'''
@TODO implement @requires_auth(permission) decorator method
    @INPUTS
        permission: string permission (i.e. 'post:drink')

    it should use the get_token_auth_header method to get the token
    it should use the verify_decode_jwt method to decode the jwt
    it should use the check_permissions method validate claims and check the requested permission
    return the decorator which passes the decoded payload to the decorated method
'''
def requires_auth(permission=''):
     def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            jwt = get_token_auth_header()
            payload = verify_decode_jwt(jwt) 
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
     return requires_auth_decorator