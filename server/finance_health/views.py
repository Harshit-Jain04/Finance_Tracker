from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render
from .forms import RegisterForm, TransactionForm, IncomeForm, ExpenseCategoryForm,ImageForm
from django.contrib.auth import login as auth_login,logout as auth_logout, authenticate
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from .models import Transaction, IncomeSource, ExpenseCategory
from django.db.models import Sum
from django.contrib.auth.models import User
from django.utils.dateformat import DateFormat
import json
from django.http import JsonResponse
from datetime import date,timedelta
from django.core.mail import send_mail
import os
from .image import extract
from PIL import Image
from django.conf import settings
from dateutil import relativedelta



def send(email,subject,message):
    
    recipient_list = [email,]

    send_mail(subject, message,os.getenv('EMAIL'), recipient_list)
# Create your views here.




def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')




def register(request):
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            auth_login(request, user)
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'registration/registration.html', {'form': form})




def login(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = AuthenticationForm(request.POST)
            if form.is_valid():
                form.save()
                user  = form.get_user()
                auth_login(request,user)
                return redirect('dashboard')
        else:
            form = AuthenticationForm()
        print('register')
        return render(request, 'login.html', {'form': form})
    else:
        return redirect('register')





def transactions(request):
    transactions = Transaction.objects.filter(user=request.user,date__month=date.today().month,date__year=date.today().year).order_by('-date')
    form  = ImageForm()
    return render(request, 'transaction.html',{'transactions':transactions,'form':form})




def logout(request):
    auth_logout(request)
    return redirect('login')





def add_transaction(request):
    print("add")
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            
            if transaction.split:
                transaction.amount = transaction.amount/2
                user = get_object_or_404(User,id=request.POST.get('split')[0])
                temp = Transaction(
                    user = user,
                    category = transaction.category,
                    amount = transaction.amount,
                    date = transaction.date,
                    description= transaction.description,
                    recurring = transaction.recurring,
                    recurring_date = transaction.recurring_date
                )
                temp.save()
                send(user.email,"Transaction Split From "+str(transaction.user),"Your transaction has been split.\nThe amount - "+str(transaction.amount/2)+" has been deducted from your account. \n Thank you for using our services.")
            if transaction.recurring:
                transaction.recurring_date = transaction.date 
                i = transaction
                for x in range(0,12):
                    t = Transaction(
                        user=i.user,
                        category=i.category,
                        amount=i.amount,
                        date=i.recurring_date,
                        description=i.description,
                        recurring_date=i.recurring_date,
                        recurring=True,
                        split=i.split
                    )
                    i.recurring_date = i.recurring_date + timedelta(days=30)
                    t.save()   
            try:
                alter = get_object_or_404(ExpenseCategory, user=request.user, category=transaction.category)
                alter.pending = alter.pending - transaction.amount
                if alter.pending < 0 or alter.pending ==0:
                    send(request.user.email,"Insufficient Balance","Your account balance is less than the amount you are trying to add. \n Please add more balance to continue using our services.")
                
                alter.save()
            except:
                pass
            transaction.save()
            return redirect('transactions')
    else:
        form = TransactionForm()
    
    return render(request, 'add_trans.html', {'form': form,'transaction':'Add Transaction'})







def edit_transaction(request, pk):
    print(pk)
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            transaction = form.save(commit=False)
            alter = get_object_or_404(ExpenseCategory, user=request.user, category=transaction.category)
            alter.pending = alter.pending - transaction.amount
            if alter.pending < 0 or alter.pending ==0:
                send(request.user.email,"Insufficient Balance","Your account balance is less than the amount you are trying to add. \n Please add more balance to continue using our services.")
            alter.save()
            transaction.save()
            return redirect('transactions')
    else:
        form = TransactionForm(instance=transaction)
        alter = get_object_or_404(ExpenseCategory, user=request.user, category=transaction.category)
        alter.pending = alter.pending + transaction.amount
        alter.save()


    return render(request, 'add_trans.html', {'form': form,'transaction':'Edit Transaction'})







def delete_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'GET':
        transaction.delete()
        try:
            alter = get_object_or_404(ExpenseCategory, user=request.user, category=transaction.category)
            alter.pending = alter.pending + transaction.amount
            alter.save()
        except:
            pass
        return redirect('transactions')






def add_income(request):
    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user
            income.save()
            return redirect('dashboard')
    else:
        form = IncomeForm()
    return render(request, 'add_income.html', {'form': form,'data':'Add Income'})






def expense_category(request):
    if request.method == 'POST':
        form = ExpenseCategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.pending = category.limit
            category.save()
            return redirect('/budget_goal')
    else:
        form = ExpenseCategoryForm()
    return render(request, 'add_income.html', {'form': form,'data':'Add Expense'})






def dashboard(request):
    print('dashboard')

    transactions = Transaction.objects.filter(user=request.user,date__month=date.today().month).order_by('-date')
    
    expense = (transactions.aggregate(Sum('amount'))['amount__sum']) or 0
    income = (IncomeSource.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum']) or 0
    budget = ExpenseCategory.objects.filter(user=request.user).aggregate(Sum('limit'))['limit__sum'] or 0
    saving = ExpenseCategory.objects.filter(user=request.user).aggregate(Sum('pending'))['pending__sum'] or 0

    return render(request, 'dashboard.html', {'transactions': transactions,'income':round(income,2),'expense':round(expense,2),'budget':round(budget,2),'saving':round(saving,2),'balance':round(income-expense,2),'user':request.user})





def budget_goal(request):
    budget = ExpenseCategory.objects.filter(user=request.user)
    
    return render(request, 'budget_goal.html',{'budget':budget})  





def pie_chart(request):
    if request.user.is_authenticated:
        today = date.today()
        budget = ExpenseCategory.objects.filter(user=request.user)
        temp = []
        pie_data=[]
        for i in budget:
            temp.append(str(i.category))
            r = Transaction.objects.filter(user=request.user,category=i.category,date__year=today.year,date__month=today.month).aggregate(Sum('amount'))['amount__sum']
            pie_data.append(str(r))
        return JsonResponse({'label':temp,'data':pie_data})
    else:
        redirect('login')





def bar_chart(request):
    if request.user.is_authenticated:
        today = date.today()
        transactions = Transaction.objects.filter(user=request.user,date__year=today.year,date__month=today.month)
        expense = (transactions.aggregate(Sum('amount'))['amount__sum']) or 0
        income = (IncomeSource.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum']) or 0
        budget = ExpenseCategory.objects.filter(user=request.user)
        
        saving = 0
        for i in budget:
            saving+=i.limit
        saving = saving - expense
        chart = {'label':['Income','Expense','Saving'],'income_data':[str(income)],'expense_data':[str(expense)],'saving_data':[str(saving)]}
        return JsonResponse(chart)

    else:
        redirect('login')





def expense_chart(request):
    if request.user.is_authenticated:
        today = date.today()
        label = []
        data = []
        for i in range(0,31):
            label.append(i+1)
            r = Transaction.objects.filter(user=request.user,date__year=today.year,date__month=today.month,date__day=i).aggregate(Sum('amount'))['amount__sum'] or 0
            data.append(r)
        print(data)
        return JsonResponse({'label':label,'data':data})
    else:
        redirect('login')





def visualise(request):
    if request.user.is_authenticated:
        return render(request, 'visualise.html')
    else:
        redirect('login')





def image(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = ImageForm(request.POST, request.FILES)
            if form.is_valid():
                
                image_instance = form.save(commit=False)
                image_instance.user = request.user
                i = Image.open(image_instance.image)    
                
                image_instance.save()
                
            
                a = extract(image_instance.image)
                
                tran = Transaction(
                    user = request.user,
                    category = 'Bills',
                    amount = a['Amount'],
                    date = a['Date'],
                    description= a['Description']
                )
                a = get_object_or_404(ExpenseCategory,user = tran.user,category = tran.category)
                a.pending = a.pending - tran.amount
                a.save()
                tran.save()
                return redirect('transactions')
    else:
        redirect('login')
                