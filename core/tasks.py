from celery import shared_task
from django.core.mail import send_mail
from .models import Payment

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={"max_retries": 3})
def process_mpesa_callback(self, callback_data):
    stk = callback_data["Body"]["stkCallback"]

    payment = Payment.objects.get(
        checkout_request_id=stk["CheckoutRequestID"]# Since checkoutrequestid is unique
    )

    if stk["ResultCode"] != 0:
        payment.status = Payment.Status.FAILED
        return {
                "ResultCode": stk["ResultCode"],
                "mpesa_ref": None
            }

    metadata = {
        item["Name"]: item.get("Value")
        for item in stk["CallbackMetadata"]["Item"]
    }

    receipt = metadata.get("MpesaReceiptNumber")
    amount = metadata.get("Amount")


    payment.status = Payment.Status.SUCCESSFUL
    payment.mpesa_ref = receipt

    payment.save(update_fields=["status", "mpesa_ref"])

    send_mail(
        subject=f"Payment Confirmation for Booking: {payment.booking__id}",
        message=f"Payment of KES {amount} received. Receipt: {receipt}",
        from_email=None,
        recipient_list=[payment.payer.email],
        fail_silently=False,
    )

    return {
                "ResultCode": 0,
                "mpesa_ref": receipt
            }