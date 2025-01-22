import httpx


class CustomBearerAuth(httpx.Auth):
    def __init__(self, token):
        self.token = token

    def auth_flow(self, request):
        # Send the request, with a custom `Authentication` header.
        request.headers['Authorization'] = "Bearer " + self.token
        yield request
