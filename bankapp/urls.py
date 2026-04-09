from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="index"),
    path('about/', views.about, name="index2"),
    path('create/', views.create_account, name="index3"),
    path('login/', views.login_view, name="login"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("balance/", views.current_balance, name="balance"),
    path("history/", views.transaction_history, name="history"),
    path("verify/", views.verify_account, name="verify"),
    path("account/", views.account_details, name="account"),
    path("logout/", views.logout_view, name="logout"),
    path("delete/", views.delete_account, name="delete"),
    path("transfer/", views.transfer_money, name="transfer"),
]
