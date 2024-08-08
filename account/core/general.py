from ipware import get_client_ip
from rest_framework.settings import api_settings


def get_ip_from_request(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    remote_addr = request.META.get("REMOTE_ADDR")
    num_proxies = api_settings.NUM_PROXIES

    if num_proxies is not None:
        if num_proxies == 0 or xff is None:
            return remote_addr
        addrs = xff.split(",")
        client_addr = addrs[-min(num_proxies, len(addrs))]
        return client_addr.strip()
    return "".join(xff.split()) if xff else remote_addr


def get_ip_from_request_with_ipware(request):
    client_ip, is_routable = get_client_ip(request)
    return client_ip, is_routable
