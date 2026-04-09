from django.shortcuts import render, redirect
from .models import Customer, Account, Transaction
from django.db.models import Q
from decimal import Decimal, InvalidOperation
from django.db import transaction
from django.contrib import messages


# HOME
def home(request):
    return render(request, "index.html")


# ABOUT
def about(request):
    return render(request, "index2.html")


# CREATE ACCOUNT
def create_account(request):

    if request.method == "POST":
        name = request.POST.get("name")
        password = request.POST.get("password")
        address = request.POST.get("address")
        mobile = request.POST.get("mobile")
        email = request.POST.get("email")

        customer = Customer.objects.create(
            name=name,
            password=password,
            address=address,
            mobile=mobile,
            email=email
        )

        Account.objects.create(customer=customer, balance=2000)

        return redirect("login")

    return render(request, "index3.html")


# LOGIN
def login_view(request):

    if request.method == "POST":

        name = request.POST.get("name")
        password = request.POST.get("password")

        try:
            user = Customer.objects.get(name=name, password=password)
            request.session["user_id"] = user.id
            return redirect("dashboard")

        except Customer.DoesNotExist:
            return render(request, "login.html", {"error": "Invalid Login Details"})

    return render(request, "login.html")


# DASHBOARD
def dashboard(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")

    user = Customer.objects.get(id=user_id)

    txn_success = request.session.pop("txn_success", False)

    return render(request, "user.html", {
        "user": user,
        "txn_success": txn_success
    })



# CURRENT BALANCE
def current_balance(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")

    user = Customer.objects.get(id=user_id)
    account = Account.objects.get(customer=user)

    return render(request, "balance.html", {
        "user": user,
        "account": account
    })


# TRANSACTION HISTORY
def transaction_history(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")

    customer = Customer.objects.get(id=user_id)
    account = Account.objects.get(customer=customer)

    transactions = Transaction.objects.filter(
        Q(sender=account) | Q(receiver=account)
    ).order_by("-timestamp")

    return render(request, "history.html", {
        "transactions": transactions,
        "account": account
    })


# VERIFY ACCOUNT
def verify_account(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")

    user = Customer.objects.get(id=user_id)

    if request.method == "POST":
        password = request.POST.get("password")

        if password == user.password:
            return redirect("account")
        else:
            return render(request, "verify.html", {
                "error": "Wrong Password"
            })

    return render(request, "verify.html")


# ACCOUNT DETAILS
def account_details(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")

    user = Customer.objects.get(id=user_id)
    account = Account.objects.get(customer=user)

    return render(request, "account.html", {
        "user": user,
        "account": account
    })


# LOGOUT
def logout_view(request):
    request.session.flush()
    return redirect("index")


# DELETE ACCOUNT
def delete_account(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")

    user = Customer.objects.get(id=user_id)

    if request.method == "POST":
        user.delete()
        request.session.flush()
        return redirect("index")

    return render(request, "delete_confirm.html", {"user": user})


# TRANSFER MONEY
# TRANSFER MONEY
def transfer_money(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")

    sender_customer = Customer.objects.get(id=user_id)
    sender_account = Account.objects.get(customer=sender_customer)

    if request.method == "POST":

        receiver_acc_no = request.POST.get("account_number")
        amount_input = request.POST.get("amount")
        password = request.POST.get("password")

        # Convert amount safely
        try:
            amount = Decimal(amount_input)
            if amount <= 0:
                messages.error(request, "Invalid Amount")
                return redirect("transfer")
        except (InvalidOperation, TypeError):
            messages.error(request, "Invalid Amount")
            return redirect("transfer")

        # Password check
        if password != sender_customer.password:
            messages.error(request, "Incorrect Password")
            return redirect("transfer")

        # Receiver check
        try:
            receiver_account = Account.objects.get(account_number=receiver_acc_no)
        except Account.DoesNotExist:
            messages.error(request, "Account Number Not Found")
            return redirect("transfer")

        # Self transfer block
        if receiver_account == sender_account:
            messages.error(request, "You cannot transfer to your own account")
            return redirect("transfer")

        # Balance check
        if sender_account.balance < amount:
            messages.error(request, "Insufficient Balance")
            return redirect("transfer")

        # Atomic transaction
        with transaction.atomic():
            sender_account.balance -= amount
            receiver_account.balance += amount

            sender_account.save()
            receiver_account.save()

            txn = Transaction.objects.create(
                sender=sender_account,
                receiver=receiver_account,
                amount=amount
            )
        request.session["txn_success"] = True
        # Show success page (NOT redirect)
        return render(request, "transfer_success.html", {
            "txn_id": txn.transaction_id,
            "amount": amount,
            "time": txn.timestamp
        })

    return render(request, "transfer.html")
