from django.shortcuts import render
from django.http import HttpResponse
from .tasks import get_issues

def main(request):
    get_issues()
    return HttpResponse("Future site of the Dev Dashboard!")
