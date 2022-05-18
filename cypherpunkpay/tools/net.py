from urllib.parse import urlparse


def is_local_network(url: str) -> bool:
    host = urlparse(url).hostname
    if host == 'localhost':
        return True
    from ipaddress import ip_address
    try:
        ip = ip_address(host)
        return ip.is_link_local or ip.is_private
    except ValueError:
        # Neither IPv4 nor IPv6. Probably domain or onion.
        pass
    return False


def get_host_or_ip(url: str) -> str:
    return urlparse(url).hostname  # works fine for URL-s with IP addresses instead of hostnames as well
