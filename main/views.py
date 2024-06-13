from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView

def home(request):
    user = request.user
    context = {'user': user}
    return render(request, 'main/main_page.html', context)