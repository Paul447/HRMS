# your_app/filters.py
import django_filters
from django_filters import CharFilter
from django.contrib.auth import get_user_model
from timeclock.models import Clock  # Assuming Clock is in your models.py

# It's good practice to get the User model dynamically
User = get_user_model()


class OnsShiftClockFilter(django_filters.FilterSet):
    # These filter names (on the left of the equals sign) MUST MATCH the query parameter names
    # that your frontend sends.
    # Your frontend sends: 'user__first_name', 'user__last_name', 'user__userprofile__department__name'

    user__first_name = CharFilter(field_name="user__first_name", lookup_expr="icontains")
    user__last_name = CharFilter(field_name="user__last_name", lookup_expr="icontains")
    user__userprofile__department__name = CharFilter(field_name="user__userprofile__department__name", lookup_expr="icontains")

    class Meta:
        model = Clock
        # These fields in Meta.fields must also match the filter names defined above.
        # They represent the valid query parameters this FilterSet will recognize.
        fields = ["user__first_name", "user__last_name", "user__userprofile__department__name"]
