import aiohttp
import colander
import deform
import json
import secrets
from pyramid.view import view_config
from oauthlib.oauth2 import WebApplicationClient
from pyramid.httpexceptions import HTTPFound
from pyramid.security import (
    remember,
    forget,
)

client_id = 'xx'
client_secret = 'xx'
redirect_uri = 'http://localhost:6543/auth'
authorize_uri = 'https://id.twitch.tv/oauth2/authorize'
token_uri = 'https://id.twitch.tv/oauth2/token'


class StreamerSchema(colander.MappingSchema):
    favorite_twitch_streamer_name = colander.SchemaNode(colander.String())


@view_config(route_name='home', renderer='templates/home.pt', permission='view')
async def home(request):
    favorite_twitch_streamer_name = request.session.get('favorite_twitch_streamer_name', '')
    form = deform.Form(StreamerSchema(), buttons=('submit',))
    if 'submit' in request.params:
        controls = request.POST.items()
        try:
            appstruct = form.validate(controls)
        except deform.ValidationFailure as errors:
            # Form is NOT valid
            return {'form': errors.render()}
        request.session['favorite_twitch_streamer_name'] = appstruct['favorite_twitch_streamer_name']
        with open('/tmp/data.json') as f:
            f.write(json.dumps({
                'auth_token': request.session.get('access_token'),
                'usr_id': appstruct['favorite_twitch_streamer_name']}))
        return HTTPFound('/')
    return {'form': form.render({'favorite_twitch_streamer_name': favorite_twitch_streamer_name})}


@view_config(route_name='second', renderer='templates/second.pt', permission='view')
async def second(request):
    favorite_twitch_streamer_name = request.session.get('favorite_twitch_streamer_name', '')
    return {'favorite_twitch_streamer_name': favorite_twitch_streamer_name}


@view_config(route_name='login')
async def login(request):
    # TODO: add check of user is logged in already
    csrf_token = secrets.token_hex(16)
    request.session['csrf_token'] = csrf_token
    client = WebApplicationClient(client_id)
    request_uri = client.prepare_request_uri(
        uri=authorize_uri,
        redirect_uri=redirect_uri,
        scope=['user:read:email', 'channel_subscriptions'],
        state=csrf_token,
    )
    return HTTPFound(location=request_uri)


@view_config(route_name='auth')
async def auth(request):
    csrf_token = request.session['csrf_token']
    client = WebApplicationClient(client_id)
    uri = request.url.replace('http://', 'https://')  # TODO:
    code = client.parse_request_uri_response(uri, state=csrf_token)['code']
    request_uri = client.prepare_request_uri(
        uri=token_uri,
        client_secret=client_secret,
        code=code,
        grant_type='authorization_code',
        redirect_uri=redirect_uri)

    async with aiohttp.ClientSession() as session:
        async with session.post(request_uri) as resp:
            assert resp.status == 200
            access_token = (await resp.json())['access_token']

    request.session['access_token'] = access_token

    async with aiohttp.ClientSession() as session:
        users_uri = 'https://api.twitch.tv/helix/users'
        headers = {'Authorization': f'Bearer {access_token}'}
        async with session.get(users_uri, headers=headers) as resp:
            assert resp.status == 200
            user_login = (await resp.json())['data'][0]['email']

    request.session['user_login'] = user_login
    headers = remember(request, user_login)
    return HTTPFound(location=request.route_url("home"), headers=headers)


@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    url = request.route_url('home')
    return HTTPFound(location=url, headers=headers)
