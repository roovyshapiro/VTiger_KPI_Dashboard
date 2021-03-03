from django.shortcuts import render, HttpResponseRedirect

def main(request):
    '''
    My Home Page.
    '''
    return render(request, "sales/ship.html") 