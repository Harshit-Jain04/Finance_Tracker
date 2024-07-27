from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
# Create your models here.


class Transaction(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=150)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    date = models.DateField()
    category = models.CharField(max_length=150)
    split = models.CharField(max_length=150,null=True,blank=True,default=None)
    recurring = models.BooleanField(default=False)
    recurring_date = models.DateField(null=True,blank=True,default=None)

class IncomeSource(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    amount = models.DecimalField(max_digits=15, decimal_places=2)

class ExpenseCategory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=150)
    limit = models.DecimalField(max_digits=15, decimal_places=2)
    pending = models.DecimalField(max_digits=15, decimal_places=2)


class Image(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField()