from django.shortcuts import render, HttpResponseRedirect

def home(request):
    '''
    My Home Page.
    '''
    return render(request, "sales/home.html") 
