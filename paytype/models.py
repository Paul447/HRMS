from django.db import models

class PayType(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
# Create your models here.
class UserBasedPayType(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE )
    pay_type = models.ForeignKey(PayType, on_delete=models.CASCADE, unique=True)
