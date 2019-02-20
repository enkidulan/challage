import logging.config

from pyramid.config import Configurator
from pyramid.session import SignedCookieSessionFactory
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import Allow, Authenticated


class Root(object):
    __acl__ = [(Allow, Authenticated, 'view')]

    def __init__(self, request):
        pass


def groupfinder(user, request):
    return [
        Authenticated,
        f'user:{user}',
    ]


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application."""

    session_factory = SignedCookieSessionFactory(
        'itsaseekreet', max_age=31536000, timeout=31536000)  # TODO:

    # support logging in python3
    logging.config.fileConfig(
        settings['logging.config'],
        disable_existing_loggers=False
    )

    config = Configurator(
        settings=settings,
        session_factory=session_factory,
        root_factory=Root)

    # Addons
    config.include('pyramid_chameleon')

    # Security policies
    authn_policy = AuthTktAuthenticationPolicy(
        'qwerty', callback=groupfinder,  # TODO:
        hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)

    # Routing
    config.add_route('home', '/')
    config.add_route('second', '/second')
    config.add_route('login', '/login')
    config.add_route('auth', '/auth')
    config.add_route('logout', '/logout')
    config.add_static_view('deform_static', 'deform:static/')
    config.scan()

    return config.make_wsgi_app()
