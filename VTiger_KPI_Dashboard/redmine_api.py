#https://www.redmine.org/projects/redmine/wiki/Rest_Issues

import requests, json

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


if __name__ == '__main__':
    with open('credentials.json') as f:
        data = f.read()
    credential_dict = json.loads(data)
    redmine_api = Redmine_API(credential_dict['redmine_username'], credential_dict['redmine_access_key'], credential_dict['redmine_host'])
    response = redmine_api.get_all_data()
    data = json.dumps(response,  indent=4, sort_keys=True)
    with open('redmine_response.json', 'w') as f:
        f.write(data)