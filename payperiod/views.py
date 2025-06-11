from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.utils import timezone
from datetime import datetime
import pytz

from .models import PayPeriod
from .serializer import PayPeriodSerializerForClockPunchReport
from django.conf import settings

# Pay period ViewSet For Clock Punch Report Which Return All Pay Periods upto Today’s Date
class PayPeriodUptoTodayViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = PayPeriodSerializerForClockPunchReport

    def get_queryset(self):
        local_tz = pytz.timezone(settings.TIME_ZONE)
        today_local_date = timezone.localtime(timezone.now(), timezone=local_tz).date()
        end_of_today_local = local_tz.localize(datetime.combine(today_local_date, datetime.max.time()))
        end_of_today_utc = end_of_today_local.astimezone(pytz.utc)

        return PayPeriod.objects.filter(start_date__lte=end_of_today_utc).order_by('-start_date')

