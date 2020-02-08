import sys, traceback, os, requests, json
from datetime import datetime
from pytz import timezone

class QuotesConnection():
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
        headers = {'Content-type': 'text/json', 'ApiKey': os.environ['API_KEY']}
        body = "[\""
        body += '", \"'.join(old_list)
        body += "\"]"
        response = requests.put(self.base_address + 'merge', params=params, data=body, headers=headers)
        if response.status_code != 200:
            return 'There was an issue merging... (Status Code: ' + str(response.status_code) + ')'
        return "Merge Successfully!"

    def insert_quote(self, quote, person, author):
        time_zone = timezone('EST')
        est_time = datetime.now(time_zone)
        time_str = est_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        headers = {'Content-Type': 'application/json', 'ApiKey': os.environ['API_KEY']}
        body = json.dumps({
            "quote": quote,
            "person": person,
            "author": str(author),
            "dateAdded": time_str,
            "source": "Discord"
        })
        print(str(body))
        response = requests.post(self.base_address + 'new', data=body, headers=headers)
        if response.status_code != 200:
            return 'There was an issue inserting... (Status Code: ' + str(response.status_code) + ')'
        return "Quote Successfully added!"


"""
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
class Quote(Base):
    __tablename__ = 'CustardQuotes'

    ID = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    Quote = sa.Column(sa.String)
    Person = sa.Column(sa.String)
    Author = sa.Column(sa.String)
    DateAdded = sa.Column(sa.String)
    Source = sa.Column(sa.String)

    def __repr__(self):
        return "<Quote(ID='%s', Quote='%s', Person='%s', Author='%s', DateAdded='%s', Source='%s')>" % (
                            self.ID, self.Quote, self.Person, self.Author, self.DateAdded, self.Source)


class QuotesConnection():
    def __init__(self):
        self.connection_string = 'mssql+pymssql://' + os.environ['DB_USER'] + ':' + os.environ['DB_PASS'] + '@' + os.environ['DB_SERVER'] + '/custardquotes'
        
    def create_session(self):
        engine = sa.create_engine(self.connection_string)
        Session = sa.orm.sessionmaker(bind=engine)
        self.session = Session()

    def get_people(self):
        self.create_session()
        people = []
        for person in self.session.query(Quote.Person).distinct():
            people.append(person[0])
        self.session.flush()
        return people
        
    def get_quotes(self, person):
        self.create_session()
        quotes = []
        for quote in self.session.query(Quote).filter_by(Person=person):
            quotes.append(quote.Quote)
        self.session.flush()
        return quotes

    def insert_quote(self, quote, person, author):
        time_zone = timezone('EST')
        est_time = datetime.now(time_zone)
        time_str = est_time.strftime("%Y-%m-%d")
        try:
            quote_obj = Quote(Quote=quote, Person=person, Author=author, DateAdded=time_str, Source='Discord')
            self.create_session()
            self.session.add(quote_obj)   
            self.session.commit()
            self.session.flush()
            return "Quote Successfully added!"
        except:
            traceback.print_exc(file=sys.stdout)
            self.session.flush()
            return 'There was an issue inserting..'
"""