from django.shortcuts import render
from web.forms.project import ProjectModelForm
from django.http import JsonResponse

from web import models

def project_list(request):
    if request.method=='GET':
        project_dict={'star':[],'my':[],'join':[]}
        # 自己创建的项目
        my_list=models.Project.objects.filter(creator=request.user_obj)
        for row in my_list:
            if row.star:
                project_dict['start'].append({'value':row,'type':'my'})
            else:
                project_dict['my'].append(row)
        # 参与的项目
        join_list=models.ProjectUser.objects.filter(user=request.user_obj)
        for row in join_list:
            if row.star:
                project_dict['star'].append({'value':row,'type':'join'})
            else:
                project_dict['join'].append(row)

        form=ProjectModelForm(request)
        return render(request,'project_list.html',{"form":form, "project_dict":project_dict})
    form=ProjectModelForm(request,data=request.POST)
    if form.is_valid():
        # 添加项目
        form.instance.creator=request.user_obj
        form.save()
        return JsonResponse({'status':True})
    return JsonResponse({'status':False, 'error':form.errors})