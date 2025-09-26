from django.contrib import admin
import math
import logging
from .models import PTOBalance, AccrualRates
from department.models import UserProfile

logger = logging.getLogger(__name__)

@admin.register(PTOBalance)
class PTOBalanceAdmin(admin.ModelAdmin):
    list_display = ("user", "pto_balance", "accrual_rate", "display_tenure")
    search_fields = ("user__username",)

    def display_tenure(self, obj):
        """Display the user's tenure safely."""
        try:
            return obj.user.profile.tenure
        except UserProfile.DoesNotExist:
            return "N/A"

    display_tenure.short_description = "Tenure"
    display_tenure.admin_order_field = "user__profile__tenure"

    def calculate_and_set_accrual(self, obj):
        """
        Calculates and sets the accrual rate and year of experience for a given object
        based on the user's profile. Handles missing data and edge cases gracefully.
        """

        # Initialize defaults
        obj.accrual_rate = None
        obj.year_of_experience = 0

        user = getattr(obj, 'user', None)
        if not user:
            logger.warning(f"No user associated with object {obj}. Cannot calculate accrual rate.")
            return

        # Get user profile safely
        profile = getattr(user, 'profile', None)
        if not profile:
            logger.warning(f"UserProfile missing for user {user.username}. Using default values.")
            return

        # Fetch employee type and pay frequency
        employeetype = getattr(profile, 'employee_type', None)
        payfrequency = getattr(profile, 'payfreq', None)

        if not employeetype or not payfrequency:
            logger.warning(f"Employee type or pay frequency missing for user {user.username}.")
            return

        # Get tenure, default to 0.0
        tenure_value = getattr(profile, 'tenure', 0.0)

        # Calculate threshold x
        x = min(max(math.ceil(tenure_value), 1), 11)
        obj.year_of_experience = tenure_value

        logger.info(
            f"Calculated tenure threshold (x)={x} for user {user.username} "
            f"(actual tenure={tenure_value}). EmployeeType={employeetype}, PayFrequency={payfrequency}"
        )

        # Fetch the corresponding accrual rate
        accrualrate = AccrualRates.objects.filter(
            employee_type=employeetype,
            pay_frequency=payfrequency,
            year_of_experience=x
        ).first()

        if accrualrate:
            obj.accrual_rate = accrualrate
        else:
            # Use default AccrualRate to prevent IntegrityError
            default_accrual = AccrualRates.objects.filter(employee_type__isnull=True).first()
            if default_accrual:
                obj.accrual_rate = default_accrual
                logger.warning(
                    f"No AccrualRate found for EmployeeType={getattr(employeetype, 'name', employeetype)}, "
                    f"PayFrequency={getattr(payfrequency, 'frequency', payfrequency)}, YOE={x}. "
                    f"Assigned default accrual rate."
                )
            else:
                logger.error(
                    f"No matching or default AccrualRate found for user {user.username}. "
                    f"Cannot assign accrual_rate. Ensure a default AccrualRate exists."
                )

    def save_model(self, request, obj, form, change):
        # Calculate accrual before saving
        self.calculate_and_set_accrual(obj)
        # Prevent saving if no accrual_rate is assigned
        if not obj.accrual_rate:
            raise ValueError(
                f"Cannot save PTOBalance for {obj.user.username}: No matching or default AccrualRate found."
            )
        super().save_model(request, obj, form, change)
