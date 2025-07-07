# shiftmanagement/models.py

from django.db import models
from django.contrib.auth.models import User

class Squad(models.Model):
    # Changed max_length to 1 as per choices.
    name = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')], unique=True)

    def __str__(self):
        return f"Squad {self.name}"

class ShiftType(models.Model):
    name = models.CharField(max_length=10, choices=[('DAY', 'Day Shift'), ('NIGHT', 'Night Shift')], unique=True)

    def __str__(self):
        return self.name

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    squad = models.ForeignKey(Squad, on_delete=models.CASCADE) # Employee still belongs to a squad

    def __str__(self):
        # Fallback to username if full name is not set
        return self.user.get_full_name() or self.user.username

# NEW MODEL: SquadShift
# This model represents a shift assigned to an entire squad.
class SquadShift(models.Model):
    squad = models.ForeignKey(Squad, on_delete=models.CASCADE)
    shift_type = models.ForeignKey(ShiftType, on_delete=models.CASCADE)
    shift_start = models.DateTimeField()
    shift_end = models.DateTimeField()

    class Meta:
        # Ensures a squad can only have one shift assigned at a given start time
        unique_together = ('squad', 'shift_start')
        ordering = ['shift_start', 'squad__name']

    def __str__(self):
        return f"Squad {self.squad.name} - {self.shift_type.name} from {self.shift_start.strftime('%Y-%m-%d %H:%M')}"

