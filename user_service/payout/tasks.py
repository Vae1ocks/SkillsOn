from celery import shared_task
from yookassa import Payout
from .models import UserPayout


@shared_task
def check_payout_status(payout_id, user_payout, user, value):
    payout = Payout.find_one(payout_id)

    if payout.status == "succeeded":
        user.balance -= value
        user.save()
        user_payout.status = "succeeded"
        user_payout.save()
    elif payout.status == "canceled":
        user_payout.status = "canceled"
        user_payout.save()
    elif payout.status == "pending":
        check_payout_status.apply_async(
            (payout.id, user_payout, user, value), countdown=120
        )
