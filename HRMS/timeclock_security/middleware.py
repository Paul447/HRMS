from django.http import JsonResponse
from allowipaddress.models import AllowIpAddress
import logging
import ipaddress

logger = logging.getLogger(__name__)

TRUSTED_PROXIES = {"127.0.0.1"}  # IPs of trusted proxies like nginx

class IPAddressRestrictionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.allowed_ips = self._get_allowed_ips()

    def _get_allowed_ips(self):
        allowed_ips = set(AllowIpAddress.objects.filter(is_active=True).values_list("ip_address", flat=True))
        return allowed_ips

    def __call__(self, request):
        self.allowed_ips = self._get_allowed_ips()

        if request.path.startswith("/api/clock/clock-in-out/"):
            client_ip = self._get_client_ip(request)
            logger.info(f"Client IP: {client_ip}")
            if client_ip not in self.allowed_ips:
                logger.warning(f"Forbidden access attempt from IP: {client_ip}")
                return JsonResponse(
                    {"error": "Access denied", "message": "You have to be in office for Clock actions."}, status=403
                )

        return self.get_response(request)

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
        remote_addr = request.META.get("REMOTE_ADDR")

        logger.info(f"X-Forwarded-For: {x_forwarded_for}")
        logger.info(f"REMOTE_ADDR: {remote_addr}")

        try:
            # Split the list and get the last *non-trusted* IP
            ip_list = [ip.strip() for ip in x_forwarded_for.split(",") if ip]
            ip_list.append(remote_addr)

            for ip in reversed(ip_list):
                if ip not in TRUSTED_PROXIES:
                    logger.info(f"Resolved client IP: {ip}")
                    return ip

        except Exception as e:
            logger.error(f"Failed to parse IPs: {e}")

        return remote_addr