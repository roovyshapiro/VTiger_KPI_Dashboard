from django.shortcuts import render, HttpResponseRedirect

def main_dashboard(request):
    print('cases!')
    return render(request, "dashboard/case_dashboard.html")