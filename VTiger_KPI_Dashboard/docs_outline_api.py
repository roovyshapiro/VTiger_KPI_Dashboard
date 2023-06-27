#https://www.getoutline.com/developers
import json, requests

class Docs_outline_api:
    def __init__(self, host, token, url, flock_url):

        self.host = host
        self.token = token
        self.url = url
        self.flock_url = flock_url

    def api_call(self, url, params):
        '''
        Accepts a URL and Params and returns the data
        '''
        headers = {
            'Authorization': f'Bearer {self.token}',
            "Content-Type": "application/json",
        }
        response = requests.post(url, headers=headers, json=params).json()
        return response


    def get_doc_info(self, id):
        '''
        Get Doc Info based on its ID
        '''
        url = f'{self.host}/documents.info'
        params = {
            "id": id,
        }
        response = self.api_call(url, params)
        return response['data']


    def get_recently_updated_docs(self):
        '''
        Get all docs ordered by recently updated
        '''

        url = f'{self.host}/documents.list'
        params = {
            "sort": "updatedAt",
            "direction": "DESC",
            "limit":25,
        }
        response = self.api_call(url, params)
        doc_list = response['data']

        #These are necessary for pagination
        p_limit = response['pagination']['limit']
        p_offset = response['pagination']['offset']
        p_nextpath = response['pagination']['nextPath']

        return doc_list


if __name__ == '__main__':
    with open('credentials.json') as f:
        data = f.read()
    credential_dict = json.loads(data)
    docs_outline_api = Docs_outline_api(credential_dict['docs_host'], credential_dict['docs_token'], credential_dict['docs_url'], credential_dict['docs_flock_url'])

    response = docs_outline_api.get_recently_updated_docs()

    data = json.dumps(response,  indent=4, sort_keys=True)
    with open('get_recent_docs.json', 'w') as f:
        f.write(data)