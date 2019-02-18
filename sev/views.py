import asyncio

from pyramid.view import view_config


@view_config(route_name='say_hello', renderer='string')
async def say_hello(request):
    wait_time = float(request.params.get('sleep', 0.1))
    await asyncio.sleep(wait_time)
    return "Welcome to Pyramid with Asyncio."
