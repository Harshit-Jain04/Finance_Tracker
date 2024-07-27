from django.urls import path
from .views import home, login,logout,dashboard, add_transaction, edit_transaction, delete_transaction,register,transactions,expense_category,add_income,budget_goal
from .views import pie_chart,bar_chart,visualise,expense_chart,image
urlpatterns = [
    path('',home,name='home'),
    path('dashboard/',dashboard,name='dashboard'),
    path('transactions/',transactions,name='transactions'),
    path('add_trans/',add_transaction,name='add_trans'),
    path('edit_trans/<int:pk>/',edit_transaction,name='edit_trans'),
    path('delete_trans/<int:pk>/',delete_transaction,name='delete_trans'),
    path('expense_category/',expense_category,name='expense_category'),
    path('add_income/',add_income,name='add_income'),
    path('budget_goal/',budget_goal,name='budget_goal'),
    path('login',login,name='login'),
    path('logout',logout,name='logout'),
    path('pie_chart',pie_chart,name='pie_chart'),
    path('bar_chart',bar_chart,name='bar_chart'),
    path('register',register,name='register'),
    path('visualise',visualise,name='visualise'),
    path('expense_chart',expense_chart,name='expense_chart'),
    path('image/',image,name='image')

]