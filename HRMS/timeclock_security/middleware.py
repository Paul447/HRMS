# timeclock_security/middleware.py
from django.http import JsonResponse, HttpResponseForbidden
from allowipaddress.models import AllowIpAddress
import logging

logger = logging.getLogger(__name__)

class IPAddressRestrictionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Cache allowed IPs to avoid hitting the DB on every request
        self.allowed_ips = self._get_allowed_ips()
        logger.info(f"Allowed IPs loaded: {self.allowed_ips}")

    def _get_allowed_ips(self):
        return set(AllowIpAddress.objects.filter(is_active=True).values_list('ip_address'))

    def __call__(self, request):
        # Only apply this restriction to clock-in related views
        # Adjust 'clock_in' and 'clock_out' to your actual URL names/paths
        if request.path.startswith('/api/clock/clock-in-out/') or \
           request.path.startswith('/api/clock/clock-in-out/'):
            client_ip = self._get_client_ip(request)
            if client_ip not in self.allowed_ips:
                logger.warning(f"Forbidden access attempt from IP: {client_ip} for URL: {request.path}")
                # logger.warning(self.allowed_ips)
                return HttpResponseForbidden("Access denied from this IP address.", client_ip )

        response = self.get_response(request)
        return response

    def _get_client_ip(self, request):
        # Handle proxies (e.g., if behind Nginx, Apache, or a load balancer)
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip() # Take the first IP if multiple are listed
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip