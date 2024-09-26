from django.db import models
from django.contrib.auth import get_user_model


class UserPayout(models.Model):
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="payouts"
    )
    value = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payout {self.id} with status {self.status}"
