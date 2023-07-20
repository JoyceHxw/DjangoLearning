from django.shortcuts import render
from web.forms.project import ProjectModelForm
from django.http import JsonResponse

def project_list(request):
    if request.method=='GET':
        form=ProjectModelForm(request)
        return render(request,'project_list.html',{"form":form})
    form=ProjectModelForm(request,data=request.POST)
    if form.is_valid():
        # 添加项目
        form.instance.creator=request.user_obj
        form.save()
        return JsonResponse({'status':True})
    return JsonResponse({'status':False, 'error':form.errors})