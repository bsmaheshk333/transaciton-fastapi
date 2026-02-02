from rest_framework.throttling import AnonRateThrottle


class LoginThrottler(AnonRateThrottle):
    # ensure to configure the rate limiter class and rate for anonymous and user in settings
    scope = "login"
