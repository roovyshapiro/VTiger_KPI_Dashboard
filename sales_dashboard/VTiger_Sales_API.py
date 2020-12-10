import requests, json, datetime, time, pytz

class Vtiger_api:
    def __init__(self, username, access_key, host):

        self.username = username
        self.access_key = access_key
        self.host = host

        self.first_name, self.last_name, self.primary_email, self.utc_offset = self.get_user_personal_info()
        self.today, self.beginning_of_week, self.beginning_of_month = self.day_week_month_times()
        self.sales_stages = []


    def day_week_month_times(self):
        '''
        Times are set in UTC, but VTiger is configured to display data in the user's
        configured time zone. As an example:
        A case might return a created time of '2019-12-02 01:00:44 UTC', 
        but the created time displayed in VTiger is 12-01-2019 08:00 PM EST.
        This case should not be part of the week's data since it appears to be from the previous week
        according to the user. Therefore, we add the offset to the time.
        If the user has an offset of -5 (EST), then the first of the week would now be 2019-12-02 05:00:00

        The same is true for the month.
        A case might return a created time of '2019-12-01 01:00:44 UTC', 
        but the created time displayed in VTiger is 11-30-2019 08:00 PM EST.
        This case should not be part of the month's data since it appears to be from the previous month
        according to the user. 

        Assuming that datetime.datetime.now() == 2020-01-14 13:18:04.921655

        >>>self.today
        2020-01-14 05:00:00

        >>>self.beginning_of_week
        2020-01-13 05:00:00

        >>>self.beginning_of_month
        2020-01-01 05:00:00
        '''
        today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        #0 = monday, 5 = Saturday, 6 = Sunday 
        day = today.weekday()

        today_time = today - datetime.timedelta(hours = self.utc_offset)

        first_of_week = today + datetime.timedelta(days = -day)
        first_of_week = first_of_week - datetime.timedelta(hours = self.utc_offset)

        first_of_month = datetime.datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        first_of_month = first_of_month - datetime.timedelta(hours = self.utc_offset)

        return today_time, first_of_week, first_of_month


    def api_call(self, url):
        '''
        Accepts a URL and returns the text
        '''
        r = requests.get(url, auth=(self.username, self.access_key))
        header_dict = r.headers

        #We're only allowed 60 API requests per minute. 
        #When we are close to reaching this limit,
        #We pause for the remaining time until it resets.
        if int(header_dict['X-FloodControl-Remaining']) <= 5:
            self.seconds_to_wait = abs(int(header_dict['X-FloodControl-Reset']) - int(time.time()))
            time.sleep(self.seconds_to_wait)
            self.seconds_to_wait = 0

        r_text = json.loads(r.text)
        return r_text


    def get_all_data(self):
        '''
        Returns data about all modules within VTiger
        '''
        data = self.api_call(f"{self.host}/listtypes?fieldTypeList=null")
        return data


    def get_module_data(self, module):
        '''
        Get information about a module's fields, Cases in this example
        url = f"{host}/describe?elementType=Cases"
        '''
        data = self.api_call(f"{self.host}/describe?elementType={module}")
        return data


    def get_user_personal_info(self):
        '''
        Retrieves the name, email and utc_offset of the user whose credentials are used to run this script
        '''
        data = self.api_call(f"{self.host}/me")
        first_name = data['result']['first_name']
        last_name = data['result']['last_name']
        email = data['result']['email1']
        
        #Time zone is presented as 'America/New_York'
        #pytz is used to determine the utc_offset based on the time zone
        timezone = data['result']['time_zone']
        current_time = datetime.datetime.now().astimezone(pytz.timezone(timezone))
        utc_offset = current_time.utcoffset().total_seconds()/60/60

        return first_name, last_name, email, utc_offset


    def get_users(self, get_all_users=False):    
        '''
        Accepts User List and returns a dictionary of the username, first, last and id
        '''
        if get_all_users == False:
            group_dict = self.get_groups()
            user_list = self.api_call(f"{self.host}/query?query=Select * FROM Users WHERE user_primary_group = '{group_dict['Sales']}';")
        else:
            user_list = self.api_call(f"{self.host}/query?query=Select * FROM Users;")

        num_of_users = len(user_list['result'])
        username_list = []
        for user in range(num_of_users):
            username_list.append(user_list['result'][user]['id'])
            
        #Creates a dictionary with every username as the key and an empty list as the value
        user_dict = {i : [] for i in username_list}

        #Assigns a list of the first name, last name and User ID to the username
        for username in range(num_of_users): 
            user_dict[username_list[username]] = [user_list['result'][username]['first_name'], user_list['result'][username]['last_name'], user_list['result'][username]['user_name'], user_list['result'][username]['user_primary_group']]       
        
        self.full_user_dict = user_dict
        return user_dict


    def get_groups_id_first(self):
        '''
        Returns a dict with group IDs as they keys and groupnames as the values.
        '''
        group_list = self.api_call(f"{self.host}/query?query=Select * FROM Groups;")
        group_dict = {}
        for group in group_list['result']:
            group_dict[group['id']] = group['groupname']
        return group_dict

    def get_groups(self):    
        '''
        Accepts Group List and returns a dictionary of the Group Name and ID
        '''
        group_list = self.api_call(f"{self.host}/query?query=Select * FROM Groups;")
        num_of_groups = len(group_list['result'])
        groupname_list = []
        for group in range(num_of_groups):
            groupname_list.append(group_list['result'][group]['groupname'])
            
        #Creates a dictionary with every group name as the key and an empty list as the value
        group_dict = {i : [] for i in groupname_list}

        #Assigns a list of the first name, last name and User ID to the username
        for groupname in range(num_of_groups): 
            group_dict[groupname_list[groupname]] = group_list['result'][groupname]['id']  
        return group_dict


    def get_phone_call_count(self, user_id, date):
        '''
        Returns an int equal to the number of items in the Phone Calls module requested by the specific URL.
        '''
        module_amount = self.api_call(f"{self.host}/query?query=SELECT COUNT(*) FROM PhoneCalls WHERE user = {user_id} and CreatedTime >= '{date}';")
        num_items = module_amount['result'][0]['count']
        return num_items


    def time_adjust(self, time_string):
        '''
        Receives a time string with this format:    02-27-2020 01:02 PM
        Returns a datetime object with this format: 2020-02-27 13:02:00
        '''
        return datetime.datetime.strptime(time_string, '%m-%d-%Y %I:%M %p')


    def get_sales_stages(self):
        '''
        Populates self.sales_stages with all the sales stages in Opportunities:
        ['Demo Scheduled', 'Demo Given', 'Quote Sent', 'Pilot', 'Needs Analysis', 'Closed Won', 'Closed Lost']
        '''
        self.sales_stages = []
        potentials = self.get_module_data('Potentials')
        for item in potentials['result']['fields'][5]['type']['picklistValues']:
            self.sales_stages.append(item['value'])

        #Remove white space from stages
        #['demo_scheduled', 'demo_given', 'quote_sent', 'pilot', 'needs_analysis', 'closed_won', 'closed_lost'] 
        stages_nospace = []
        for stage in self.sales_stages:
            stage_nospace = stage.replace(' ', '_').lower()
            stages_nospace.append(stage_nospace)

        return stages_nospace


    def retrieve_data(self):
        '''
        This gathers all the opportunities that were changed throughout the day, phone calls that
        were made that day, the date of the beginning of the day and the user's name and returns
        it as a dictionary like this:
        {'gareth_bunkard': [0, 0, 0, 0, 0, 0, 0, '0', '2020-02-27 05:00:00', 'gareth_bunkard'], 
         'salvadore_louise': [0, 1, 3, 0, 0, 1, 0, '28', '2020-02-27 05:00:00', 'salvadore_louise'], 
         'shiminy_cartwheel': [0, 0, 0, 0, 0, 0, 0, '95', '2020-02-27 05:00:00', 'shiminy_cartwheel'], 
         'johnny_flinkson': [2, 1, 0, 1, 0, 0, 0, '74', '2020-02-27 05:00:00', 'johnny_flinkson']}

        This Djangoapp takes this data via the celery task and updates the database with it. 
        '''
        #Get all the opportunities that were changed today
        opportunities = self.api_call(f"{self.host}/query?query=SELECT * FROM Potentials WHERE current_stage_entry_time >= '{self.today}';")
        #Get a list of users with 'Sales' as their primary group
        user_dict = self.get_users()
        #Gather the sales stages if its empty
        if self.sales_stages == []:
            self.get_sales_stages()
        
        full_stat_dict = {}

        for user in user_dict:
            #Create dictionary of each user connected to list with 0's for the length of sales stages
            #{'jack_biscuit':[0,0,0,0,0,0,0]}
            user_name = f"{user_dict[user][0].lower()}_{user_dict[user][1].lower()}"
            full_stat_dict[user_name] = [0 for i in range(len(self.sales_stages))]
            
            #Get daily phone calls for the user and append it to the user's list
            phone_call_amount = self.get_phone_call_count(user, self.today)
            full_stat_dict[user_name].append(phone_call_amount)
            #Append a string of the time from when this data was gathered
            full_stat_dict[user_name].append(self.today.strftime('%Y-%m-%d %H:%M:%S'))
            #Append the user's name to the user's list
            full_stat_dict[user_name].append(user_name)

            #Every time an opportunity sales stage is changed, a VTiger workflow triggers
            #which fills in read-only fields with the modified time for when the stage was changed.
            #These fields ensures a record of an opportunity's stages if it was changed multiple times
            #throughout the day. The original list of 0's are then incremented by 1 for each time they're 
            #filled out in the opportunity since the beginning of the day.
            for opportunity in opportunities['result']:

                if opportunity['assigned_user_id'] == user:
                    demo_scheduled = opportunity['cf_potentials_demoscheduledchangedat']
                    demo_given = opportunity['cf_potentials_demogivenchangedat']
                    quote_sent = opportunity['cf_potentials_quotesentchangedat']
                    pilot = opportunity['cf_potentials_pilotchangedat']
                    needs_analysis = opportunity['cf_potentials_needsanalysischangedat']
                    closed_won = opportunity['cf_potentials_closedwonchangedat']
                    closed_lost = opportunity['cf_potentials_closedlostchangedat']


                    if demo_scheduled != '' and self.time_adjust(demo_scheduled) > self.today:
                        full_stat_dict[user_name][0] += 1
                    if demo_given != '' and self.time_adjust(demo_given) > self.today:
                        full_stat_dict[user_name][1] += 1
                    if quote_sent != '' and self.time_adjust(quote_sent) > self.today:
                        full_stat_dict[user_name][2] += 1
                    if pilot != '' and self.time_adjust(pilot) > self.today:
                        full_stat_dict[user_name][3] += 1
                    if needs_analysis != '' and self.time_adjust(needs_analysis) > self.today:
                        full_stat_dict[user_name][4] += 1
                    if closed_won != '' and self.time_adjust(closed_won) > self.today:
                        full_stat_dict[user_name][5] += 1
                    if closed_lost != '' and self.time_adjust(closed_lost) > self.today:
                        full_stat_dict[user_name][6] += 1

        return full_stat_dict

    ####################
    ###Case Dashboard###
    ####################

    def get_users_and_groups_file(self):
        '''
        Get all users and groups with their corresponding IDs and save to a file for reference.
        '''
        group_dict = self.get_groups_id_first()
        user_dict = self.get_users(get_all_users=True)
        full_dict = {}
        full_dict['groups'] = group_dict
        full_dict['users'] = user_dict
        data = json.dumps(full_dict,  indent=4, sort_keys=True)
        with open('users_and_groups.json', 'w') as f:
            f.write(data)
        return full_dict

    def retrieve_all_open_cases_count(self):
        '''
        Function to retrieve all open cases. One of its functions is to perform regular checks to see if any older vtiger cases have been deleted,
        If so, case_dashboard.tasks will run /populateallcases.
        '''
        case_count = self.api_call(f"{self.host}/query?query=SELECT COUNT(*) FROM Cases WHERE casestatus != 'Closed' AND casestatus != 'Resolved';")
        total_count = case_count['result'][0]['count']
        num_items = int(total_count)
        return num_items


    def retrieve_all_open_cases_created_time(self):
        '''
        The intention of this function is to find the case with the earliest created date. This created date will then be used to populate
        the entire db with cases from that date. This population will be a one time event to fill up the db or can be used to refill
        the data in case of an emergency. We only need cases from the open cases earliest created date so that the total number of open
        cases will be accurate on the display.
        '''
        num_items = self.retrieve_all_open_cases_count()
        vtiger_item_list = []
        offset = 0
        if num_items > 100:
            while num_items > 100:
                item_batch = self.api_call(f"{self.host}/query?query=SELECT * FROM Cases WHERE casestatus != 'Closed' AND casestatus != 'Resolved' limit {offset}, 100;")
                print('api_call_complete', num_items)
                vtiger_item_list.append(item_batch['result'])
                offset += 100
                num_items = num_items - 100
                if num_items <= 100:
                    break
        if num_items <= 100:
            item_batch = self.api_call(f"{self.host}/query?query=SELECT * FROM Cases WHERE casestatus != 'Closed' AND casestatus != 'Resolved'  limit {offset}, 100;")
            print('api_call_complete', num_items)
            vtiger_item_list.append(item_batch['result'])
        
        #Combine the multiple lists of dictionaries into one list
        #Before: [[{simcard1}, {simcard2}], [{simcard101}, {simcard102}]]
        #After: [{simcard1}, {simcard2}, {simcard101}, {simcard102}]
        full_item_list = []
        for item_list in vtiger_item_list:
            full_item_list += item_list

        self.earliest_created_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for case in full_item_list:
            if case['createdtime'] < self.earliest_created_time:
                self.earliest_created_time = case['createdtime']

        return self.earliest_created_time


    def case_count(self, created_time):
        '''
        Get the amount of cases from after "created_time" and return the number as an int.
        '''
        case_count = self.api_call(f"{self.host}/query?query=SELECT COUNT(*) FROM Cases WHERE createdtime >= '{created_time}' ;")
        print(case_count)
        total_count = case_count['result'][0]['count']
        print('total_cases', total_count)
        return total_count

    def retrieve_all_cases(self):
        '''
        This method is meant to be used only once to populate the entire db of cases from a certain date.
        The date is determined by finding the earliest created date from all open cases using
        self.retrieve_all_open_cases_created_time()
        It can be used to get all the cases for an entire year or more.
        This is called from case_dashboard.tasks.
    
        A module can only return a maximum of 100 results. 
        To circumvent that, an offset can be supplied which starts returning data from after the offset.
        The amount must be looped through in order to retrieve all the results.
        For instance if there are 250 cases, first 100 is retrieved, then another 100, and then 50.
        A list is returned of each dictionary that was retrieved this way.
        For 5000 cases, 50 API calls will be used.
        '''
        created_time = self.retrieve_all_open_cases_created_time()

        num_items = self.case_count(created_time)
        num_items = int(num_items)
        vtiger_item_list = []
        offset = 0
        if num_items > 100:
            while num_items > 100:
                item_batch = self.api_call(f"{self.host}/query?query=Select * FROM Cases WHERE createdtime >= '{created_time}' limit {offset}, 100;")
                print('api_call_complete', num_items)
                vtiger_item_list.append(item_batch['result'])
                offset += 100
                num_items = num_items - 100
                if num_items <= 100:
                    break
        if num_items <= 100:
            item_batch = self.api_call(f"{self.host}/query?query=Select * FROM Cases WHERE createdtime >= '{created_time}' limit {offset}, 100;")
            print('api_call_complete', num_items)
            vtiger_item_list.append(item_batch['result'])
        
        #Combine the multiple lists of dictionaries into one list
        #Before: [[{simcard1}, {simcard2}], [{simcard101}, {simcard102}]]
        #After: [{simcard1}, {simcard2}, {simcard101}, {simcard102}]
        full_item_list = []
        for item_list in vtiger_item_list:
            full_item_list += item_list

        try:
            self.case_list = []
            with open('users_and_groups.json') as f:
                data = json.load(f)
                for case in full_item_list:
                    assigned_username = f"{data['users'][case['assigned_user_id']][0]} {data['users'][case['assigned_user_id']][1]}"
                    assigned_groupname = data['groups'][case['group_id']]
                    case['assigned_username'] = assigned_username
                    case['assigned_groupname'] = assigned_groupname
                    self.case_list.append(case)
        except:
            self.case_list = []
            data = self.get_users_and_groups_file()
            for case in full_item_list:
                try:
                    assigned_username = f"{data['users'][case['assigned_user_id']][0]} {data['users'][case['assigned_user_id']][1]}"
                except KeyError:
                    assigned_username = ''
                try:
                    assigned_groupname = data['groups'][case['group_id']]
                except KeyError:
                    assigned_groupname = ''

                case['assigned_username'] = assigned_username
                case['assigned_groupname'] = assigned_groupname
                self.case_list.append(case)

        return self.case_list

    def retrieve_todays_cases(self, module='Cases'):
        '''
        Returns a list of all the cases that have been modified since the beginning of today.
        In most cases, this should be less than 100. Since there could be a scenario where more than 100
        cases would be modified in a single day, we'll need to account for that and therefore must utilize 2 API
        calls for "count" instead of just retrieving cases as there is a maximum of 100 returned cases per call.

        self.get_users_and_groups_file() retrieves all Users and Groups with their IDs and names
        and writes it to a file. The data in this file is used to translate the IDs that
        are retrieved in the cases. This way, we don't want unnecessary API calls to translate
        User and Group IDs everytime we retrieve the cases from today.
        If the username, groupname, or file isn't present or returns any errors,
        the function to populate this data is called again and continues as normal.
        This should take care of any situation where a new user is added, a group name is changed,
        or the file is deleted for any reason.
        '''

        today = datetime.datetime.now().strftime("%Y-%m-%d") + ' 00:00:00'

        module_count = self.api_call(f"{self.host}/query?query=SELECT COUNT(*) FROM {module} WHERE modifiedtime >= '{today}';")
        total_count = module_count['result'][0]['count']
        num_items = int(total_count)
        vtiger_item_list = []
        offset = 0
        if num_items > 100:
            while num_items > 100:
                item_batch = self.api_call(f"{self.host}/query?query=SELECT * FROM {module} WHERE modifiedtime >= '{today}' limit {offset}, 100;")
                print(f'API_call_complete. # of {module} returned: {num_items}')
                vtiger_item_list.append(item_batch['result'])
                offset += 100
                num_items = num_items - 100
                if num_items <= 100:
                    break
        if num_items <= 100:
            item_batch = self.api_call(f"{self.host}/query?query=SELECT * FROM {module} WHERE modifiedtime >= '{today}'  limit {offset}, 100;")
            print(f'API_call_complete. # of {module} returned: {num_items}')
            vtiger_item_list.append(item_batch['result'])

        #Combine the multiple lists of dictionaries into one list
        #Before: [[{simcard1}, {simcard2}], [{simcard101}, {simcard102}]]
        #After: [{simcard1}, {simcard2}, {simcard101}, {simcard102}]
        all_items = []
        for item_list in vtiger_item_list:
            all_items += item_list

        try:
            self.today_item_list = []
            with open('users_and_groups.json') as f:
                data = json.load(f)
                for item in all_items:
                    assigned_username = f"{data['users'][item['assigned_user_id']][0]} {data['users'][item['assigned_user_id']][1]}"
                    assigned_groupname = data['groups'][item['group_id']]
                    item['assigned_username'] = assigned_username
                    item['assigned_groupname'] = assigned_groupname
                    self.today_item_list.append(item)
        except:
            self.today_item_list = []
            data = self.get_users_and_groups_file()
            for item in all_items:
                try:
                    assigned_username = f"{data['users'][item['assigned_user_id']][0]} {data['users'][item['assigned_user_id']][1]}"
                except KeyError:
                    assigned_username = ''
                try:
                    assigned_groupname = data['groups'][item['group_id']]
                except KeyError:
                    assigned_groupname = ''

                item['assigned_username'] = assigned_username
                item['assigned_groupname'] = assigned_groupname
                self.today_item_list.append(item)

        return self.today_item_list


if __name__ == '__main__':
        with open('credentials.json') as f:
            data = f.read()
        credential_dict = json.loads(data)
        vtigerapi = Vtiger_api(credential_dict['username'], credential_dict['access_key'], credential_dict['host'])
        response = vtigerapi.retrieve_todays_cases(module = 'PhoneCalls')
        data = json.dumps(response,  indent=4, sort_keys=True)
        with open('PhoneCalls.json', 'w') as f:
            f.write(data)