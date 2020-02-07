import sys, traceback, os, requests, json

class Quotes():
    def __init__(self):
        self.base_address = "https://custardquotesapi.azurewebsites.net/Quotes/"

    def get_people(self):
        headers = {'ApiKey': os.environ['API_KEY']}
        result = requests.get(self.base_address + 'allNames', headers=headers).json()
        return result

    def get_quotes(self, person):
        params = {'name': person}
        headers = {'ApiKey': os.environ['API_KEY']}
        response = requests.get(self.base_address + 'byName', params=params, headers=headers).json()
        result = [entry['quote'] for entry in response]
        return result

    def merge_people(self, old_list, new_person):
        params = {'newName': new_person}
        headers = {'ApiKey': os.environ['API_KEY']}
        body = "[\""
        body += '", \"'.join(old_list)
        body += "\"]"
        print(body)
        response = requests.put(self.base_address + 'merge', params=params, data=body, headers=headers)
        return response

    def insert_quote(self, quote, person, author):
        time_zone = timezone('EST')
        est_time = datetime.now(time_zone)
        time_str = est_time.strftime("%Y-%m-%d")

os.environ['API_KEY'] = '^!*Y8f_xDyAK3ZLM99%5n@s39e2Kr'
q = Quotes()
print(q.get_people())
print(q.merge_people(['Matehew Shane', 'Matew Shanny', 'Mathew Shan', 'Mattew Shan'], "Matthew Shan"))
print(q.get_people())