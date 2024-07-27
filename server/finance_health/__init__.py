from datetime import datetime,date
from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand
class Command(BaseCommand):
    def handle(self, *args, **options):
        from .models import Transaction
        today = date.today()
        trans = Transaction.objects.filter(recurring_date=today)
        for i in trans:
            next_date = i.recurring_date + relativedelta(months=+1)
            t = Transaction(
                user=i.user,
                category=i.category,
                amount=i.amount,
                date=today,
                description=i.description,
                recurring_date=next_date,
                recurring=True,
                split=i.split
            )
            t.save()