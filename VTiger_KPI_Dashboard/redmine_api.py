#https://www.redmine.org/projects/redmine/wiki/Rest_Issues

import requests, json, datetime

class Redmine_API:
    def __init__(self, username, access_key, host):

        self.username = username
        self.access_key = access_key
        self.host = host

    def api_call(self, url):
        '''
        Accepts a URL and returns the text
        '''
        r = requests.get(url, auth=(self.username, self.access_key))

        r_text = json.loads(r.text)
        return r_text

    def get_all_data(self):
        '''
        Returns a list of all issues in Redmine.
        Only a maximum of 100 issues can be returned at once which is why offset is used.
        Read more here: https://www.redmine.org/projects/redmine/wiki/Rest_Issues
        '''
        data = self.api_call(f"{self.host}/issues.json?status_id=*&limit=100&offset=0")
        total_count = data['total_count']
        self.all_issues = []
        for issue in data['issues']:
            self.all_issues.append(issue)

        while len(self.all_issues) < total_count:
            data = self.api_call(f"{self.host}/issues.json?status_id=*&limit=100&offset={len(self.all_issues)}")
            for issue in data['issues']:
                self.all_issues.append(issue)
            print("# of issues gathered", len(self.all_issues))
            print('total_count', total_count)
        return self.all_issues

    def get_recently_updated_data(self):
        '''
        To fetch issues for a date range (uncrypted filter is "><2012-03-01|2012-03-07") :
        GET /issues.xml?created_on=%3E%3C2012-03-01|2012-03-07

        To fetch issues created after a certain date (uncrypted filter is ">=2012-03-01") :
        GET /issues.xml?created_on=%3E%3D2012-03-01

        Or before a certain date (uncrypted filter is "<= 2012-03-07") :
        GET /issues.xml?created_on=%3C%3D2012-03-07

        To fetch issues created after a certain timestamp (uncrypted filter is ">=2014-01-02T08:12:32Z") :
        GET /issues.xml?created_on=%3E%3D2014-01-02T08:12:32Z

        To fetch issues updated after a certain timestamp (uncrypted filter is ">=2014-01-02T08:12:32Z") :
        GET /issues.xml?updated_on=%3E%3D2014-01-02T08:12:32Z
        '''
        now = datetime.datetime.now()
        thirty_days_ago_dt = now + datetime.timedelta(days=-30)
        thirty_days_ago = datetime.datetime.strftime(thirty_days_ago_dt, '%Y-%m-%dT%H:%M:%SZ')
        data = self.api_call(f"{self.host}/issues.json?updated_on=%3E%3D{thirty_days_ago}&status_id=*&limit=100&offset=0")
        recent_total_count = data['total_count']
        self.recent_issues = []
        for issue in data['issues']:
            self.recent_issues.append(issue)
        print("# of issues gathered", len(self.recent_issues))
        print('total_count', recent_total_count)

        while len(self.recent_issues) < recent_total_count:
            data = self.api_call(f"{self.host}/issues.json?updated_on=%3E%3D{thirty_days_ago}&status_id=*&limit=100&offset={len(self.recent_issues)}")
            for issue in data['issues']:
                self.recent_issues.append(issue)
            print("# of issues gathered", len(self.recent_issues))
            print('total_count', recent_total_count)
        return self.recent_issues

if __name__ == '__main__':
    with open('credentials.json') as f:
        data = f.read()
    credential_dict = json.loads(data)
    redmine_api = Redmine_API(credential_dict['redmine_username'], credential_dict['redmine_access_key'], credential_dict['redmine_host'])
    #response = redmine_api.get_all_data()
    response = redmine_api.get_recently_updated_data()
    data = json.dumps(response,  indent=4, sort_keys=True)
    with open('redmine_response.json', 'w') as f:
        f.write(data)