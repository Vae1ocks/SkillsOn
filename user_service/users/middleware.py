from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model

from channels.db import database_sync_to_async

# from urllib.parse import parse_qs


@database_sync_to_async
def get_user(token):
    try:
        token_decode = AccessToken(token)
        id = token_decode["user_id"]
        user = get_user_model().objects.get(id=id)
        return user
    except (InvalidToken, TokenError, get_user_model().DoesNotExist):
        return AnonymousUser()


class TokenAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        # query_string = parse_qs(scope['query_string'].decode())
        # token = query_string.get('token')
        path = scope["path"]
        if path[-1] == "/":
            path = path[:-1]  # убираем последний слеш /token/ --> /token
        token = path.rsplit("/", 1)[-1]
        if token:
            scope["user"] = await get_user(token)
        else:
            scope["user"] = AnonymousUser()
        return await self.inner(scope, receive, send)
