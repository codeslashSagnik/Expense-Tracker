from django.shortcuts import render

def index(request):
    return render(request,'expenses/index.html')
def add_expenses(request):
    return render(request,'expenses/add-expenses.html')
