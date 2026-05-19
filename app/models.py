from django.db import models
from django.contrib.auth.models import User


class Contact(models.Model):
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=255)
    message = models.TextField()

    def __str__(self):
        return self.full_name
    
class ResumeHistory(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    filename = models.CharField(max_length=255)

    ats_score = models.IntegerField()

    predicted_role = models.CharField(max_length=100)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.filename}"
    

class Donation(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    name = models.CharField(max_length=100)

    amount = models.IntegerField()

    razorpay_order_id = models.CharField(max_length=255)

    razorpay_payment_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    paid = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - ₹{self.amount}"    