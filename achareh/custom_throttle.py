from django.core.cache import caches
from rest_framework.throttling import ScopedRateThrottle


class CustomScopedRateThrottle(ScopedRateThrottle):
    scope_attr = "custom_throttle_scope"
    cache = caches["throttle"]

    def __init__(self, phone=None):
        self.phone = phone

    def allow_request(self, request, view):
        self.scope = self.get_scope(view)

        if not self.scope:
            return True

        self.rate = self.get_rate()
        self.num_requests, self.duration = self.parse_rate(self.rate)

        if self.rate is None:
            return True

        self.key = self.get_cache_key(request)
        if self.key is None:
            return True

        self.history = self.get_history(request)
        self.now = self.timer()

        while self.history and self.history[-1] <= self.now - self.duration:
            self.history.pop()
        if len(self.history) >= self.num_requests:
            return False
        return True

    def add_request(self, request, view):
        self.scope = self.get_scope(view)
        self.rate = self.get_rate()
        self.num_requests, self.duration = self.parse_rate(self.rate)
        self.history = self.get_history(request)
        self.now = self.timer()
        self.history.insert(0, self.now)
        self.cache.set(self.key, self.history, self.duration)
        return True

    def get_history(self, request):
        self.key = self.get_cache_key(request)
        return self.cache.get(self.key, [])

    def get_cache_key(self, request):
        if self.phone:
            ident = self.phone
        else:
            ident = self.get_ident(request)

        return self.cache_format % {"scope": self.scope, "ident": ident}

    def get_scope(self, view):
        return getattr(view, self.scope_attr, None)
