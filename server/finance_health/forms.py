from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Transaction, IncomeSource, ExpenseCategory,Image
class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class TransactionForm(forms.ModelForm):

    split = forms.ModelChoiceField(queryset=User.objects.all(),required=False)
    class Meta:
        model = Transaction
        split = forms.ModelChoiceField(queryset=User.objects.all(),required=False)
        fields = [ "description", "amount", "date",  "category", "split", "recurring"]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'split': forms.Select(attrs={'class': 'form-control'}),
            'recurring': forms.CheckboxInput(attrs={'class': 'form-control'}),
        }
class IncomeForm(forms.ModelForm):
    class Meta:
        model = IncomeSource
        fields = [ "name", "amount"]
class ExpenseCategoryForm(forms.ModelForm):
    class Meta:
        model = ExpenseCategory
        fields = [ "category", "limit"] 
class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image']