from django.shortcuts import render, HttpResponseRedirect

def home(request):
    '''
    My Home Page.
    '''
    print('test!')
    return render(request, "sales/home.html") 
