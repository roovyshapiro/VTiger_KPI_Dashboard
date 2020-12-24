from django.shortcuts import render, HttpResponseRedirect

def home(request):
    '''
    My Home Page.
    '''
    return render(request, "sales/home.html") 

def handler404(request, exception):
    return render(request, 'sales/404.html')

def handler500(request, exception):
    return render(request, 'sales/500.html')
