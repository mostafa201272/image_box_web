from django.shortcuts import render, redirect
from django.contrib import messages

from .forms import UserRegisteration
# Create your views here.

def registeration(request):
    if request.method == 'POST':
        form = UserRegisteration(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"thank you {username} Account Created Successfully")
            return redirect('Login')
    else:
        form = UserRegisteration()
    return render(request, "pages/users/registeration.html" , {"form": form})