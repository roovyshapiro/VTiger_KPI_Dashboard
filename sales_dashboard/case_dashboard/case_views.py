from django.shortcuts import render, HttpResponseRedirect
from django.utils import timezone
from django.db.models import Q

from .tasks import populate_db_celery_cases
from .models import Cases

def main_dashboard(request):
    '''
    Send all cases from the Cases db to the html template to be used in the html table.
    Send all unique group names in the context so that it can be used in a dropdown.
    Get the data from the form inputs like "group name" and filter the cases to be displayed.
    '''
    #Returns all cases with the most recently modified first if no filter is applied
    full_cases = Cases.objects.all().order_by('-modifiedtime')
    #Returns dictionary with "assigned_groupname" as key, and the actual name as the value.
    #We pass these groups to the html to populate the drop down menu for filtering
    case_groups = Cases.objects.values('assigned_groupname').distinct()

    #We get the form submission from the drop down and use it to then filter the "full_case"
    #query set to only return and display the cases which match that group.
    group_request = request.GET.get('group_dropdown')
    if group_request != '' and group_request is not None and group_request != '--Select Group--':
        full_cases = full_cases.filter(assigned_groupname=group_request)

    date_start_request = request.GET.get('date_start')
    date_end_request = request.GET.get('date_end')

    if date_start_request != '' and date_start_request is not None:
        full_cases = full_cases.filter(modifiedtime__gte=date_start_request)

    if date_end_request != '' and date_end_request is not None:
        full_cases = full_cases.filter(modifiedtime__lt=date_end_request)

    #Prepare the date and group that was chosen, so it can be displayed on the dashboard
    date_group_dict = {}
    date_group_dict['date_start'] = date_start_request
    date_group_dict['date_end'] = date_end_request
    date_group_dict['group'] = group_request

    #If no date was selected, we'll display the time frame from the first modified case to the last
    #We use the custom "modifiedtime_date" method so we can display the time in the same format as the
    #date picker: "modifiedtime.strftime('%Y-%m-%d')"
    if group_request == '' or group_request == None:
        date_group_dict['group'] = 'All Groups'
    if date_start_request == '' or date_start_request == None:
        first_case = full_cases.order_by('modifiedtime').first()
        date_group_dict['date_start'] = first_case.modifiedtime_date
    if date_end_request == '' or date_end_request == None:
        last_case = full_cases.order_by('modifiedtime').last()
        date_group_dict['date_end'] = last_case.modifiedtime_date


    #Prepare calculated data to present as a simple summary overview of the cases
    case_stats_dict = {}
    case_stats = full_cases

    #These calculations are based on not having any date selected
    if date_start_request == '' or date_start_request is  None or date_end_request == '' or date_end_request is None:
        case_stats_closed = case_stats.filter(Q(casestatus="Resolved") | Q(casestatus="Closed"))
        case_stats_dict['closed'] = len(case_stats_closed)

        case_stats_opened = case_stats.filter(~Q(casestatus="Resolved") | ~Q(casestatus="Closed"))
        case_stats_dict['opened'] = len(case_stats_opened)
        try:
            case_stats_dict['kill_rate'] = int((case_stats_dict['closed'] / case_stats_dict['opened']) * 100)
        except ZeroDivisionError:
            #If there are 0 opened cases and 3 closed cases, the kill rate will become 300%.
            case_stats_dict['kill_rate'] = int(case_stats_dict['closed'] * 100)

    #If a date is selected, the calculations should only affect that time frame.
    if date_start_request != '' and date_start_request is not None and date_end_request != '' and date_end_request is not None:
        try:
            case_stats_opened = case_stats.filter(createdtime__gte=date_start_request, createdtime__lte=date_end_request)
            case_stats_dict['opened'] = len(case_stats_opened)
        except ValueError:
            case_stats_dict['opened'] = 0

        try:
            case_stats = case_stats.filter(modifiedtime__gte=date_start_request, modifiedtime__lte=date_end_request)
            case_stats_closed = case_stats.filter(Q(casestatus="Resolved") | Q(casestatus="Closed"))
            case_stats_dict['closed'] = len(case_stats_closed)
        except ValueError:
            case_stats_dict['closed'] = 0

        try:
            case_stats_dict['kill_rate'] = int((case_stats_dict['closed'] / case_stats_dict['opened']) * 100)
        except ValueError:
            case_stats_dict['kill_rate'] = int(0)
        except ZeroDivisionError:
            #If there are 0 opened cases and 3 closed cases, the kill rate will become 300%.
            case_stats_dict['kill_rate'] = int(case_stats_dict['closed'] * 100)

    context = {
        "full_cases":full_cases,
        "case_groups":case_groups,
        "case_stat_dict":case_stats_dict,
        "date_group_dict":date_group_dict,
    }

    #After returning the request, return the html file to go to, and the context to send to the html
    return render(request, "dashboard/case_dashboard.html", context)

def populate_cases(request):
    populate_db_celery_cases()
    return HttpResponseRedirect("/cases")

def delete_all_cases(request):
    '''
    Delete all the cases in the database from today only.
    Convenient to reset the day's data without deleting previous days' data.
    '''
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = timezone.now().replace(hour=23, minute=59, second=59, microsecond=0)
    cases = Cases.objects.all().filter(date_modified__gte=today_start, date_modified__lte=today_end)

    cases.delete()

    #This deletes all items:
    #Cases.objects.all().delete()
    return HttpResponseRedirect('/cases')