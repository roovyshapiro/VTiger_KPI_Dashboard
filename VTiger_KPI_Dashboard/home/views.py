from django.shortcuts import render, HttpResponseRedirect

def home(request):
    '''
    My Home Page.
    '''
    return render(request, "sales/home.html") 

def handler404(request):
    return render(request, 'sales/404.html', status=404)

def handler500(request):
    return render(request, 'sales/500.html', status=500)
