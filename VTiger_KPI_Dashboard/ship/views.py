from django.shortcuts import render, HttpResponseRedirect
from .tasks import get_products

def main(request):
    '''
    My Home Page.
    '''
    get_products()
    return render(request, "sales/ship.html") 