import uuid
import random
from decimal import Decimal
from django.db import models


# -------------------------------
# CUSTOMER MODEL
# -------------------------------
class Customer(models.Model):
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    address = models.TextField()
    mobile = models.CharField(max_length=15)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name


# -------------------------------
# ACCOUNT MODEL
# -------------------------------
class Account(models.Model):

    customer = models.OneToOneField(
        Customer,
        on_delete=models.CASCADE,
        related_name="account"
    )

    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("2000.00")
    )

    account_number = models.CharField(
        max_length=6,
        unique=True,
        blank=True
    )

    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = self.generate_account_number()
        super().save(*args, **kwargs)

    def generate_account_number(self):
        while True:
            number = str(random.randint(100000, 999999))
            if not Account.objects.filter(account_number=number).exists():
                return number

    def __str__(self):
        return f"{self.customer.name} - {self.account_number}"


# -------------------------------
# TRANSACTION MODEL
# -------------------------------
class Transaction(models.Model):

    transaction_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False
    )

    sender = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="sent_transactions"
    )

    receiver = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="received_transactions"
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = "TXN" + uuid.uuid4().hex[:10].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.transaction_id} - ₹{self.amount}"
