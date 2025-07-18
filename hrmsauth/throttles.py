from rest_framework.throttling import SimpleRateThrottle

class LoginRateThrottle(SimpleRateThrottle):
    scope = "login"

    def get_cache_key(self, request, view):
        # Use username if present, otherwise fallback to IP address
        username = request.data.get("username")
        if username:
            ident = username.lower()
        else:
            ident = self.get_ident(request)  # client IP address
        return self.cache_format % {
            "scope": self.scope,
            "ident": ident,
        }
