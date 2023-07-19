from django.shortcuts import redirect, render,HttpResponse
def index(request):
    return render(request, 'index.html')