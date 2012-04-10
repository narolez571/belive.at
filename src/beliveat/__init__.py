# -*- coding: utf-8 -*-

"""Provides the ``main()`` WSGI application entry point."""

import logging
logger = logging.getLogger(__name__)

import sys

from pyramid.authentication import SessionAuthenticationPolicy
from pyramid.config import Configurator
from pyramid.exceptions import NotFound
from pyramid.request import Request
from pyramid.security import NO_PERMISSION_REQUIRED as PUBLIC
from pyramid.view import AppendSlashNotFoundViewFactory

from pyramid_beaker import session_factory_from_settings
from pyramid_simpleauth.hooks import get_roles
from pyramid_simpleauth.tree import UserRoot

from .hooks import get_redis_client
from .model import Base
from .tree import Root
from .view import not_found_view

def main(global_config, **settings):
    """Call with settings to create and return a WSGI application."""
    
    # Initialise a configurator.
    config = Configurator(settings=settings, root_factory=Root)
    
    # Include packages.
    config.include('pyramid_beaker')
    config.include('pyramid_tm')
    config.include('pyramid_weblayer')
    config.include('pyramid_simpleauth')
    config.commit()
    config.include('pyramid_twitterauth')
    config.include('pyramid_basemodel')
    
    # Expose routes.
    config.add_route('index', '') # <!-- splash page
    config.add_route('dashboard', 'dashboard')
    config.add_route('assignments', 'assignments/*traverse')
    config.add_route('users', 'users/*traverse', factory=UserRoot,
                     use_global_views=True)
    
    config.add_static_view('socket.io/lib', 'intr:static')
    config.add_route('socket_io', 'socket.io/*remaining')

    # Extend the request.
    config.set_request_property(get_redis_client, 'redis', reify=True)
    
    # Configure a custom 404 that first tries to append a slash to the URL.
    not_found = AppendSlashNotFoundViewFactory(not_found_view)
    config.add_view(not_found, context=NotFound, permission=PUBLIC)
    
    # Run a venusian scan to pick up the declerative configuration.
    config.scan('beliveat')
    
    # Return a configured WSGI application.
    return config.make_wsgi_app()

