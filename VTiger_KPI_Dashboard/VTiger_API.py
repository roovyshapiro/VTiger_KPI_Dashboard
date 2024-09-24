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
        print('URL',url)
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
    
    def api_call_params(self, url, data):
        '''
        Accepts a URL and returns the text
        '''
        r = requests.get(url, auth=(self.username, self.access_key), params=data)
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

    def retrieve_data_id(self, id):
        '''
        Return all the fields associated to an item's id.
        This is used primarily for testing/troubleshooting
        and is not used as part of any of the workflows.
        '''
        data = self.api_call(f"{self.host}/retrieve?id={id};")
        return data

    def get_users(self):    	
        '''	
        Accepts User List and returns a dictionary of the username, first, last id and ID from the employee module
        '''	
        user_list = self.api_call(f"{self.host}/query?query=Select * FROM Users;")	
        employee_list = self.api_call(f"{self.host}/query?query=Select * FROM Employees WHERE is_user = '1';")

        num_of_users = len(user_list['result'])	
        username_list = []	
        for user in range(num_of_users):	
            username_list.append(user_list['result'][user]['id'])	

        #Creates a dictionary with every username as the key and an empty list as the value	
        user_dict = {i : [] for i in username_list}	

        #Assigns a list of the first name, last name and User ID to the username	
        for username in range(num_of_users): 	
            user_dict[username_list[username]] = [user_list['result'][username]['first_name'], user_list['result'][username]['last_name'], user_list['result'][username]['user_name'], user_list['result'][username]['user_primary_group']]       	

        for user_id, user_list in user_dict.items():
            for employee in employee_list['result']:
                if user_id == employee['user_id']:
                    user_list.append(employee['id'])
                    continue

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

    def get_users_and_groups_file(self):
        '''
        Get all users and groups with their corresponding IDs and save to a file for reference.
        '''
        group_dict = self.get_groups_id_first()
        user_dict = self.get_users()
        full_dict = {}
        full_dict['groups'] = group_dict
        full_dict['users'] = user_dict
        data = json.dumps(full_dict,  indent=4, sort_keys=True)
        with open('users_and_groups.json', 'w') as f:
            f.write(data)
        return full_dict


    def lookup_phone(self, phone):
        '''
        Rest API: GET endpoint/lookup?type=phone&value=286187&searchIn={“Contacts”:[“mobile”,”phone”]}
        type : phone / email
        value : search value
        searchIn : Module and fieldname to search

        Webservices:
        webservice.php?operation=lookup&type=phone&value=3434566&sessionName={session_name}&searchIn={“module_name”:[“field_names”]}
        '''
        phone = str(phone).replace('-','').replace('(','').replace(')','').replace(' ','').replace('+','')

        # Check if the phone number is 10 digits long and starts with 1
        if len(phone) == 11 and phone.startswith("1"):
            # Remove the initial '1' from the phone number
            phone = phone[1:]
        data = {
            "type": "phone",
            "value": phone,
            "searchIn": '{"Contacts":["mobile","phone"], "Leads":["mobile","phone"]}'
        }

        lookup = self.api_call_params(f"{self.host}/lookup", data)
        #print(len(lookup['result']))
        for contact in lookup['result']:
            if contact['phone'] != '':
                contact_phone = contact['phone'].replace('-','').replace('(','').replace(')','').replace(' ','').replace('+','')
                if phone in contact_phone:
                    return contact['id']

            if contact['mobile'] != '':
                contact_mobile = contact['mobile'].replace('-','').replace('(','').replace(')','').replace(' ','').replace('+','')
                if phone in contact_mobile:
                    return contact['id']

        return lookup['result'][0]['id']




    ####################
    ###Case Dashboard###
    ####################


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
                    modified_username = f"{data['users'][case['modifiedby']][0]} {data['users'][case['modifiedby']][1]}"
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
                try:
                    modified_username = f"{data['users'][case['modifiedby']][0]} {data['users'][case['modifiedby']][1]}"
                except KeyError:
                    modified_username = ''

                case['assigned_username'] = assigned_username
                case['assigned_groupname'] = assigned_groupname
                case['modified_username'] = modified_username
                self.case_list.append(case)

        return self.case_list


    ############################
    ###SALES & CASE Dashboard###
    ############################


    def retrieve_todays_cases(self, module='Cases', day='Today'):
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

        if day == 'month':
            ninety_days_ago = datetime.datetime.now() + datetime.timedelta(days = -30)
            today = ninety_days_ago.strftime("%Y-%m-%d") + ' 00:00:00'
        if day == 'all':
            module_count = self.api_call(f"{self.host}/query?query=SELECT COUNT(*) FROM {module};")
            total_count = module_count['result'][0]['count']
            num_items = int(total_count)
            vtiger_item_list = []
            offset = 0
            if num_items > 100:
                while num_items > 100:
                    item_batch = self.api_call(f"{self.host}/query?query=SELECT * FROM {module} limit {offset}, 100;")
                    print(f'API_call_complete. # of {module} returned: {num_items}')
                    vtiger_item_list.append(item_batch['result'])
                    offset += 100
                    num_items = num_items - 100
                    if num_items <= 100:
                        break
            if num_items <= 100:
                item_batch = self.api_call(f"{self.host}/query?query=SELECT * FROM {module}  limit {offset}, 100;")
                print(f'API_call_complete. # of {module} returned: {num_items}')
                vtiger_item_list.append(item_batch['result'])

            #Combine the multiple lists of dictionaries into one list
            #Before: [[{simcard1}, {simcard2}], [{simcard101}, {simcard102}]]
            #After: [{simcard1}, {simcard2}, {simcard101}, {simcard102}]
            all_items = []
            for item_list in vtiger_item_list:
                all_items += item_list
            return all_items

        if day != 'all':
            module_count = self.api_call(f"{self.host}/query?query=SELECT COUNT(*) FROM {module} WHERE modifiedtime >= '{today}' ;")
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
                    try:
                        assigned_username = f"{data['users'][item['assigned_user_id']][0]} {data['users'][item['assigned_user_id']][1]}"
                    except:
                        assigned_username = ''
                    try:
                        modified_username = f"{data['users'][item['modifiedby']][0]} {data['users'][item['modifiedby']][1]}"
                    except:
                        modified_username = ''
                    if 'group_id' in item and item['group_id'] == '':
                        assigned_groupname = ''
                    if 'group_id' not in item:
                        try:
                            users_primary_group_id = data['users'][item['assigned_user_id']][3]
                        except:
                            users_primary_group_id = ''
                        try:
                            assigned_groupname = data['groups'][users_primary_group_id]
                        except:
                            assigned_groupname = ''
                    else:
                        assigned_groupname = data['groups'][item['group_id']]
                    
                    try:
                        qualified_by_name = ''
                        qualified_by_employee_id = item['cf_potentials_qualifiedby']
                        if qualified_by_employee_id != '':
                            for user in data['users']:
                                if qualified_by_employee_id == data['users'][user][4]:
                                    qualified_by_name = f"{data['users'][user][0]} {data['users'][user][1]}"
                    except:
                        qualified_by_name = ''

                    
                    item['assigned_username'] = assigned_username
                    item['assigned_groupname'] = assigned_groupname
                    item['modified_username'] = modified_username
                    try:
                        item['assigned_employee_id'] = data['users'][item['assigned_user_id']][4]
                    except: 
                        item['assigned_employee_id'] = ''
                    item['qualified_by_name'] = qualified_by_name
                    self.today_item_list.append(item)
        except:
            self.today_item_list = []
            data = self.get_users_and_groups_file()
            for item in all_items:
                #Sometimes an opportunity can be assigned directly to the group
                if item['assigned_user_id'] in data['groups']:
                    assigned_groupname = data['groups'][item['assigned_user_id']]
                    assigned_username = data['groups'][item['assigned_user_id']]
                    try:
                        qualified_by_name = ''
                        qualified_by_employee_id = item['cf_potentials_qualifiedby']
                        if qualified_by_employee_id != '':
                            for user in data['users']:
                                if qualified_by_employee_id == data['users'][user][4]:
                                    qualified_by_name = f"{data['users'][user][0]} {data['users'][user][1]}"
                    except:
                        qualified_by_name = ''
                    try:
                        modified_username = f"{data['users'][item['modifiedby']][0]} {data['users'][item['modifiedby']][1]}"
                    except:
                        modified_username = ''
                    try:
                        employee_id =  {data['users'][item['modifiedby']][4]}
                    except:
                        employee_id = ''
                else:
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
                    try:
                        modified_username = f"{data['users'][item['modifiedby']][0]} {data['users'][item['modifiedby']][1]}"
                    except:
                        modified_username = ''
                    try:
                        employee_id =  {data['users'][item['modifiedby']][4]}
                    except:
                        employee_id = ''
                    try:
                        qualified_by_name = ''
                        qualified_by_employee_id = item['cf_potentials_qualifiedby']
                        if qualified_by_employee_id != '':
                            for user in data['users']:
                                if qualified_by_employee_id == data['users'][user][4]:
                                    qualified_by_name = f"{data['users'][user][0]} {data['users'][user][1]}"
                    except:
                        qualified_by_name = ''

                item['qualified_by_name'] = qualified_by_name
                item['assigned_username'] = assigned_username
                item['assigned_groupname'] = assigned_groupname
                item['modified_username'] = modified_username
                item['employee_id'] = employee_id

                self.today_item_list.append(item)

        return self.today_item_list


    ############################
    ###    Phone Calls        ###
    ############################

    def create_call(self, payload):
        '''
        Example Phone Call from VTiger:
        {
            "CreatedTime": "2020-12-10 14:48:02",
            "assigned_groupname": "",
            "assigned_user_id": "19x27",
            "assigned_username": "Randall Hoberman",
            "billduration": "56",
            "billrate": "0.0000",
            "callid": "",
            "callstatus": "completed",
            "campaign_name": "",
            "campaign_number": "",
            "cases_id": "",
            "created_user_id": "19x27",
            "customer": "2x930718",
            "customernumber": "9545556480",
            "customertype": "Leads",
            "direction": "outbound",
            "disposition_name": "",
            "endtime": "2020-12-10 09:49:21",
            "gateway": "Asterisk",
            "id": "43x930719",
            "isclosed": "0",
            "modifiedby": "19x27",
            "modifiedtime": "2020-12-10 14:48:02",
            "notes": "",
            "potentials_id": "",
            "recordingurl": "http://voipserver.com:4001/recordings/90a897aeb4e34d129749ca436728ace7",
            "source": "CRM",
            "sourceuuid": "90a897aeb4e34d129749ca436728ace7",
            "starred": "",
            "starttime": "2020-12-10 09:48:02",
            "tags": "",
            "ticket_id": "",
            "totalduration": "56",
            "transcription": "",
            "transferred_number": "",
            "transferred_user": "",
            "user": "19x27"
        },

        Example call from Dialpad:

        {
            "master_call_id": null,
            "date_ended": 168208074,
            "voicemail_recording_id": null,
            "internal_number": "+132154",
            "call_recording_ids": [],
            "duration": 11989.972,
            "mos_score": 4.41,
            "entry_point_target": {},
            "proxy_target": {},
            "entry_point_call_id": null,
            "operator_call_id": null,
            "call_id": 461114531840,
            "state": "hangup",
            "csat_score": null,
            "date_started": 16808017,
            "transcription_text": null,
            "direction": "outbound",
            "labels": [],
            "total_duration": 20056.427,
            "date_connected": 16826084,
            "routing_breadcrumbs": [],
            "voicemail_link": null,
            "is_transferred": "FALSE",
            "public_call_review_share_link": "https://dialpad.com/shared/call/yx91bVOx1Zf6gcbfUuxwcnjcCqz01qoUsO",
            "was_recorded": "FALSE",
            "date_rang": null,
            "target": {
            "phone": "+13213798154",
            "type": "user",
            "id": 6651106703015936,
            "name": "Roovy Shapiro",
            "email": "roovy@eyeride.io"
            },
            "event_timestamp": 168229176,
            "contact": {
            "phone": "+167922",
            "type": "local",
            "id": 560034183552,
            "name": "(619922",
            "email": ""
            },
            "company_call_review_share_link": "https://dialpad.com/shared/call/2jdW0pGpCtoUMHkFv5tSeGskEL1jKLpHNl",
            "group_id": null,
            "external_number": "+161922"
        }
        '''

        try:
            vtiger_id = self.lookup_phone(payload['external_number'])
        except IndexError:
            print('index-error: no contact found', payload['external_number'])
            return None
        cust_type = 'no_type'

        if '2x' in vtiger_id:
            cust_type = 'Leads'
        if '4x' in vtiger_id:
            cust_type = 'Contacts'
        else:
            pass

        dp_start = datetime.datetime.fromtimestamp(int(payload['date_started'] / 1000.0))
        dp_start_str = dp_start.replace(tzinfo=pytz.timezone('US/Central')).strftime('%Y-%m-%d %H:%M:%S')

        dp_end = datetime.datetime.fromtimestamp(int(payload['date_ended'] / 1000.0))
        dp_end_str = dp_end.replace(tzinfo=pytz.timezone('US/Central')).strftime('%Y-%m-%d %H:%M:%S')
 
        assigned_id = ''
        assigned_name = ''


        if payload['target']['type'] != 'user':
            user_full_name = self.lookup_dialpad_id(payload['sender_id'])
            with open('users_and_groups.json') as f:
                data = json.load(f)
                found = False
                for user in data['users']:
                    if f"{data['users'][user][0]} {data['users'][user][1]}" == user_full_name:
                        assigned_id = user
                        assigned_name = user_full_name
        else:
            with open('users_and_groups.json') as f:
                data = json.load(f)
                found = False
                for user in data['users']:
                    if f"{data['users'][user][2]}" == payload['target']['email']:
                        assigned_id = user
                        assigned_name = f"{data['users'][user][0]} {data['users'][user][1]}"
                        found = True
                        break
                if not found:
                    print(f"User not found for email: {payload['target']}")




        vtiger_update_dict = {
            'assigned_username': assigned_name,
            'totalduration': int(payload['total_duration'] / 1000),
            'callstatus': payload['state'] ,
            'customernumber': payload['external_number'],
            'starttime': dp_start_str,
            'endtime': dp_end_str,
            'recordingurl' : f"https://dialpad.com/callhistory/callreview/{payload['entry_point_call_id']}",
            'direction': payload['direction'],
            'assigned_user_id': assigned_id,
            'sourceuuid':payload['call_id'],
            "customer": vtiger_id,
            "customertype": cust_type,
            'user':assigned_id,
            'gateway':'Dialpad',
            }
        #print(vtiger_update_dict)
        jsondump =json.dumps(vtiger_update_dict)
        url = self.host + f"/create?elementType=PhoneCalls&element={jsondump}"
        code, reason, text = self.api_call_post(url)
        print('DIALPAD wehook success', code, reason)
 
                
                                

    def api_call_post(self, url):
        '''
        Accepts a URL for POST request
        Returns the status code and reason
        Similar to self.api_call_get(), wait until the minute API call limit resets
        '''
        r = requests.post(url, auth=(self.username, self.access_key))
        header_dict = r.headers
        if int(header_dict['X-FloodControl-Remaining']) <= 10:
            seconds_to_wait = abs(int(header_dict['X-FloodControl-Reset']) - int(time.time()))
            print(f"API minute limit reached! Pausing for {seconds_to_wait} seconds!")
            time.sleep(seconds_to_wait)
        return r.status_code, r.reason, r.text
        
    ############################
    ###    SMS Messages      ###
    ############################
    def lookup_dialpad_id(self, sender_id):
        '''
        '''
        with open('credentials.json') as f:
            data = f.read()
        credential_dict = json.loads(data)
        dialpad_key = credential_dict['dialpad_key']
        url = f"https://dialpad.com/api/v2/users?apikey={dialpad_key}"
        headers = {
            'accept': 'application/json'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            for user in data['items']:
                if user['id'] == str(sender_id):
                    user_full_name = f"{user['first_name']} {user['last_name']}"
        return user_full_name

        

    def create_sms(self, payload, user_full_name):
        '''

        Inbound SMS to Dialpad
        {
            "id": 5571516353560576,
            "created_date": 1725564299047,
            "direction": "inbound",
            "event_timestamp": 1725564299471,
            "target": {
                "id": 6755239348502528,
                "type": "user",
                "name": "Jimbo Lowfer",
                "phone_number": "(512) 555-5555"
            },
            "contact": {
                "id": "http://www.google.com/m8/feeds/contacts/email/base/2688a7ca0e67324d",
                "name": "Jember Shender",
                "phone_number": "+15555551234"
            },
            "sender_id": "NULL",
            "from_number": "+15555551234",
            "to_number": [
                "+15125555555"
            ],
            "mms": "FALSE",
            "is_internal": "FALSE",
            "message_status": "pending",
            "message_delivery_result": "NULL",
            "text": "This is a response text back to dialpad",
            "text_content": "This is a response text back to dialpad",
            "mms_url": "NULL"
        }

        Add Related: Establish a relationship between the two records.   

        POST endpoint/add_related?sourceRecordId=record_id&relatedRecordId=target_record_id&relationIdLabel=target_relation_label
        '''
        print(payload)
        vtiger_id = ''
        assigned_id = ''

        if payload['direction'] == 'outbound':
            direction = 'Outbound'
            cust_phone_numbers = payload['to_number']
        else:
            direction = 'Inbound'
            cust_phone_numbers = [payload['from_number']]

        # Loop through each recipient phone number
        for cust_phone in cust_phone_numbers:
            try:
                # Perform phone lookup for each recipient
                vtiger_id = self.lookup_phone(cust_phone)
            except IndexError:
                print('index-error: no contact found', cust_phone)
                vtiger_id = None  # Reset for each phone lookup if no contact is found
                continue

            if not vtiger_id:
                print(f"No VTiger ID found for {cust_phone}. Skipping SMS creation.")
                continue

            #if payload['target']['type'] != 'user':
            #    user_full_name = self.lookup_dialpad_id(payload['sender_id'])
            #else:
            #    user_full_name = payload['target']['name']

            # Prepare assigned user ID
            with open('users_and_groups.json') as f:
                data = json.load(f)
                for user in data['users']:
                    if f"{data['users'][user][0]} {data['users'][user][1]}" == user_full_name:
                        assigned_id = user
            # Prepare the data for each recipient
            vtiger_update_dict = {
                'assigned_user_id': assigned_id,
                'statusmessage': 'Delivered',
                'smsstatus': 'Delivered',
                'direction': direction,
                'phonenumber': cust_phone.replace('-', '').replace('(', '').replace(')', '').replace(' ', '').replace('+', ''),
                'message': payload['text'],
                'label': payload['text'],
            }

            # Encode and send the SMS data
            jsondump = json.dumps(vtiger_update_dict)
            import urllib.parse
            encoded_jsondump = urllib.parse.quote(jsondump)
            url = self.host + f"/create?elementType=SMSNotifier&element={encoded_jsondump}"

            code, reason, text = self.api_call_post(url)
            print('SMS webhook result', code, reason, text)

            # Process the response and relate the SMS to the lead/contact
            if code == 200 and vtiger_id:
                try:
                    response_data = json.loads(text)
                    sms_crm_id = response_data['result']['id']

                    # Now relate the SMS to the appropriate lead/contact
                    url = f"/add_related?sourceRecordId={sms_crm_id}&relatedRecordId={vtiger_id}"
                    url = self.host + url
                    code, reason, text = self.api_call_post(url)
                    print(code, reason, text)
                except json.JSONDecodeError:
                    print("Error decoding JSON response:", text)
            else:
                print(f"Failed to create SMS. Status: {code}, Reason: {reason}, Response: {text}")
    ############################
    ###    SHIP Dashboard    ###
    ############################


    def products_count(self):
        '''
        Get the amount of active Products.
        '''
        products_count = self.api_call(f"{self.host}/query?query=SELECT COUNT(*) FROM Products WHERE discontinued = '1';")
        #print(products_count)
        total_count = products_count['result'][0]['count']
        print('Total Active Products', total_count)
        return total_count

    def retrieve_all_products(self):
        '''
        This is called from ship.tasks
    
        A module can only return a maximum of 100 results. 
        To circumvent that, an offset can be supplied which starts returning data from after the offset.
        The amount must be looped through in order to retrieve all the results.
        For instance if there are 150 products, first 100 is retrieved, then another 100, and then 50.
        A list is returned of each dictionary that was retrieved this way.
        For 5000 products, 50 API calls will be used.
        '''
        num_items = self.products_count()

        num_items = int(num_items)
        vtiger_item_list = []
        offset = 0
        if num_items > 100:
            while num_items > 100:
                item_batch = self.api_call(f"{self.host}/query?query=Select * FROM Products WHERE discontinued = '1' limit {offset}, 100;")
                print('api_call_complete', num_items)
                vtiger_item_list.append(item_batch['result'])
                offset += 100
                num_items = num_items - 100
                if num_items <= 100:
                    break
        if num_items <= 100:
            item_batch = self.api_call(f"{self.host}/query?query=Select * FROM Products WHERE discontinued = '1' limit {offset}, 100;")
            print('api_call_complete', num_items)
            vtiger_item_list.append(item_batch['result'])
        
        #Combine the multiple lists of dictionaries into one list
        #Before: [[{product1}, {product2}], [{product101}, {product102}]]
        #After: [{product1}, {product2}, {product101}, {product102}]
        all_items = []
        for item_list in vtiger_item_list:
            all_items += item_list

        try:
            self.product_list = []
            with open('users_and_groups.json') as f:
                data = json.load(f)
                for item in all_items:
                    assigned_username = f"{data['users'][item['assigned_user_id']][0]} {data['users'][item['assigned_user_id']][1]}"
                    modified_username = f"{data['users'][item['modifiedby']][0]} {data['users'][item['modifiedby']][1]}"
    
                    item['assigned_username'] = assigned_username
                    item['modified_username'] = modified_username
                    self.product_list.append(item)
        except:
            self.product_list = []
            data = self.get_users_and_groups_file()
            for item in all_items:
                #Sometimes an product can be assigned directly to the group
                if item['assigned_user_id'] in data['groups']:
                    assigned_username = data['groups'][item['assigned_user_id']]
                else:
                    try:
                        assigned_username = f"{data['users'][item['assigned_user_id']][0]} {data['users'][item['assigned_user_id']][1]}"
                    except KeyError:
                        assigned_username = ''
                    try:
                        modified_username = f"{data['users'][item['modifiedby']][0]} {data['users'][item['modifiedby']][1]}"
                    except:
                        modified_username = ''

                item['assigned_username'] = assigned_username
                item['modified_username'] = modified_username
                self.product_list.append(item)
        
        return self.product_list


if __name__ == '__main__':
    with open('credentials.json') as f:
        data = f.read()
    credential_dict = json.loads(data)
    vtigerapi = Vtiger_api(credential_dict['username'], credential_dict['access_key'], credential_dict['host'])
    #response = vtigerapi.retrieve_todays_cases(module = 'Employees', day='all')
    #response = vtigerapi.get_users_and_groups_file()
    #response = vtigerapi.get_all_data()
    #response = vtigerapi.get_module_data("SMSNotifier")
    #response = vtigerapi.retrieve_todays_cases(module = 'Potentials')
    #response = vtigerapi.retrieve_todays_cases(module = 'Potentials', day='month')
    
    response = vtigerapi.lookup_phone('404 454 5460')
    #response = vtigerapi.retrieve_data_id('44x2623256')
    #vtigerapi.create_sms()
    data = json.dumps(response,  indent=4, sort_keys=True)
    with open('lookup_phone.json', 'w') as f:
        f.write(data)