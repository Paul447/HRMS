from django.http import HttpResponseForbidden, JsonResponse
from allowipaddress.models import AllowIpAddress
import logging

logger = logging.getLogger(__name__)

class IPAddressRestrictionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.allowed_ips = self._get_allowed_ips()
        logger.info(f"Allowed IPs loaded: {self.allowed_ips}")

    def _get_allowed_ips(self):
        allowed_ips = set(AllowIpAddress.objects.filter(is_active=True).values_list('ip_address', flat=True))
        logger.info(f"Loaded allowed IPs from DB: {allowed_ips}")
        return allowed_ips

    def __call__(self, request):
        logger.info("Middleware running")
        self.allowed_ips = self._get_allowed_ips()  # Refresh IPs (remove if caching is preferred)
        logger.info(f"Request path: {request.path}")
        logger.info(f"Allowed IPs: {self.allowed_ips}")
        if request.path.startswith('/api/clock/clock-in-out/'):
            client_ip = self._get_client_ip(request)
            logger.info(f"Client IP: {client_ip}")
            if client_ip not in self.allowed_ips:
                logger.warning(f"Forbidden access attempt from IP: {client_ip}")
                return JsonResponse({"error": "Access denied", "message": "You have to be in office for Clock actions."}, status=403)
        response = self.get_response(request)
        return response

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        logger.info(f"Client IP retrieved: {ip}")
        return ip