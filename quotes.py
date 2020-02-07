import sys, traceback, os
from datetime import datetime
from pytz import timezone
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

    # def get_next_id(self):
    #     self.create_session()
    #     #result = self.session.query(Quote.ID).max()
    #     for i in self.session.query(sa.sql.functions.max(Quote.ID)):
    #         result = i[0]
    #     self.session.flush()
    #     return result+1

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

# conn = QuotesConnection() 
# print(conn.get_quotes("Random Person"))
# print(conn.insert_quote("This is a dummy quote!", "Random Person", "Matthew Shan"))
# print(conn.insert_quote("This is a dummy quote2!", "Random Person", "Matthew Shan"))
