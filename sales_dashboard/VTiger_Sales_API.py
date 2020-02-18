import requests, json, datetime, collections, time, pytz, os, sqlite3

class Vtiger_api:
    def __init__(self, username, access_key, host):

        self.username = username
        self.access_key = access_key
        self.host = host

        self.first_name, self.last_name, self.primary_email, self.utc_offset = self.get_user_personal_info()

        self.today, self.beginning_of_week, self.beginning_of_month = self.day_week_month_times()

        self.dbfilename = 'db.sqlite3'
        self.dbfilepath = os.path.join(os.path.abspath('.'), self.dbfilename)
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

    def get_users(self):    
        '''
        Accepts User List and returns a dictionary of the username, first, last and id
        '''
        group_dict = self.get_groups()
        user_list = self.api_call(f"{self.host}/query?query=Select * FROM Users WHERE user_primary_group = '{group_dict['Sales']}';")

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


    def get_opportunity_count(self, user_id, date):
        '''
        Returns an int equal to the number of items in the Opportunities module requested by the specific URL.
        Additionally returns a dictionary with the amount of each sales stages.
        '''
        module_amount = self.api_call(f"{self.host}/query?query=SELECT COUNT(*) FROM Potentials WHERE assigned_user_id = {user_id} AND current_stage_entry_time >= '{date}';")
        num_items = module_amount['result'][0]['count']

        opportunities = self.api_call(f"{self.host}/query?query=SELECT * FROM Potentials WHERE assigned_user_id = {user_id} AND current_stage_entry_time >= '{date}';")
        
        #All sales stages are added to this dict with '0' as the default value.
        #Here's what this ends up looking like as an example:
        #{'Demo Scheduled': 2, 'Demo Given': 0, 'Quote Sent': 3, 'Pilot': 0, 'Needs Analysis': 0, 'Closed Won': 3, 'Closed Lost': 3}
        if self.sales_stages == []:
            self.get_sales_stages()

        sales_stage_dict = {i:0 for i in self.sales_stages}
        for item in opportunities['result']:
            stage = item['sales_stage']
            sales_stage_dict[stage] += 1

        return num_items, sales_stage_dict


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


    def sales_stats(self, timeframe):
        '''
        Prints out the stats for each user who has "Sales" as their primary group.
        '''
        if timeframe.strip().lower() == 'day':
            date = self.today
        elif timeframe.strip().lower() == 'week':
            date = self.beginning_of_week
        elif timeframe.strip().lower() == 'month':
            date = self.beginning_of_month
        else:
            print("Not a valid timeframe! 'day', 'week' or 'month' only!") 

        user_dict = self.get_users()
        print(f"This {timeframe.title()}'s Phone Calls and Opportunities:")
        for key in user_dict:
            print(f"{user_dict[key][0]} {user_dict[key][1]}:")
            print("\tPhone Calls:", self.get_phone_call_count(key, date))
            num_items, sales_stage_dict = self.get_opportunity_count(key, date)
            print("\tOpportunity Stage Changed:", num_items)
            #Convert dictionary into a list of tuples ordered by values from highest to lowest
            #Example output: [(8, 'Quote Sent'), (2, 'Closed Lost'), (1, 'Closed Won')]
            data = sorted( ((v,k) for k,v in sales_stage_dict.items()), reverse=True) 
            for item in data:
                print(f"\t\t{item[1]}: {item[0]}")


    def retrieve_data(self, timespan):
        '''
        Retrieves data from VTiger for each sales person and then
        returns it as a dictionary of lists.
        This is then passed to dashboard/views.py to populate the Django database.
        '''
        #The date passed here is from the most recent item in the database.
        #If there are no items in the database, 'today' is passed here and
        #We collect all data from the beginning of the day.
        if timespan == 'today':
            timespan = self.today

        user_dict = self.get_users()
        full_user_dict = {}

        for key in user_dict:
            
            full_stat_list = []
            num_phone_calls = self.get_phone_call_count(key, self.today)

            num_items, sales_stage_dict = self.get_opportunity_count(key, timespan)
            for v in sales_stage_dict.values():
                full_stat_list.append(v)

            full_stat_list.append(num_phone_calls)
            full_stat_list.append(timespan.strftime('%Y-%m-%d %H:%M:%S'))
            full_stat_list.append(f"{user_dict[key][0].lower()}_{user_dict[key][1].lower()}")

            full_user_dict[f"{user_dict[key][0].lower()}_{user_dict[key][1].lower()}"] = full_stat_list

            #full_user_dict
            #{james_frinkle:[0, 1, 15, 0, 0, 3, 6, '215', '2020-01-28 21:30:00', 'james_frinkle']}

        return full_user_dict

if __name__ == '__main__':
        with open('credentials.json') as f:
            data = f.read()
        credential_dict = json.loads(data)
        vtigerapi = Vtiger_api(credential_dict['username'], credential_dict['access_key'], credential_dict['host'])
        #response = vtigerapi.get_module_data('Potentials')
        #data = json.dumps(response,  indent=4, sort_keys=True)
        #with open('potentials.json', 'w') as f:
        #    f.write(data)
        #vtigerapi.sales_stats('week')