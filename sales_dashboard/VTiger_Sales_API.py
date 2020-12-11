import requests, json, datetime, time, pytz

class Vtiger_api:
    def __init__(self, username, access_key, host):

        self.username = username
        self.access_key = access_key
        self.host = host

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


    ############################
    ###SALES & CAse Dashboard###
    ############################


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
                    if 'group_id' in item and item['group_id'] == '':
                        assigned_groupname = ''
                    if 'group_id' not in item:
                        users_primary_group_id = data['users'][item['assigned_user_id']][3]
                        assigned_groupname = data['groups'][users_primary_group_id]
                    else:
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
                    #Some modules like "Potentials" dont have group_id's as part of the item.
                    #Others like Cases can have a group_id, but it might be blank.
                    if 'group_id' in item:
                        assigned_groupname = ''
                    else:
                        users_primary_group_id = data['users'][item['assigned_user_id']][3]
                        assigned_groupname = data['groups'][users_primary_group_id]

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