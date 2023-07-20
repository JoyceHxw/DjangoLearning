from django.shortcuts import render

def wiki(request, project_id):
    return render(request, 'wiki.html')