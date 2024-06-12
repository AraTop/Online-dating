from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView


def home(request):
    return render(request, 'main/main_page.html')