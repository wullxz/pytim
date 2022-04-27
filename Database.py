from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, Text, Numeric, DateTime
from sqlalchemy.orm import sessionmaker, relationship

# Don't warn about precision of decimal values in SQLite
# It's very much sufficient as long as I don't earn Millions
import warnings
from datetime import datetime
from pprint import pprint
from sqlalchemy.exc import SAWarning
warnings.filterwarnings('ignore', r".*support Decimal objects natively", SAWarning, r'^sqlalchemy\.sql\.sqltypes$')


Base = declarative_base()

class Database():
  def __init__(self, db_file='sqlite:////home/ms/Dropbox/tim/db.sqlite'):
    self.db_file = db_file
    self.eng = create_engine(self.db_file)

  def create_database(self, db_file):
    Base.metadata.create_all(self.eng)

  def get_session(self):
    Session = sessionmaker(bind=self.eng)
    ses = Session()
    return ses

session = Database().get_session()

class Client(Base):
    __tablename__ = "Clients"

    Id = Column(Integer, primary_key=True)
    Name = Column(Text)
    Street1 = Column(Text)
    Street2 = Column(Text)
    Zip = Column(Text)
    City = Column(Text)
    Email = Column(Text)
    Short = Column(Text, unique=True)

    def choose(client_list):
      pprint(client_list)

    def get_byName(name):
      res = session.query(Client).filter(Client.Name.ilike('%' + name + '%'))
      if (res.count() == 1):
        return res.first()
      elif (res.count() > 1):
        print("TODO: select from multiple results")
        Client.choose(res)
      else:
        print("No results!")
        return None

    def get_byShortcode(shortcode):
      res = session.query(Client).filter(Client.Short == shortcode)
      return res.first()

class Invoice(Base):
  __tablename__ = "Invoices"

  Id = Column(Integer, primary_key=True)
  #Date = Column(Text)
  Date = Column(Integer)
  fk_Clients = Column(Integer, ForeignKey("Clients.Id"))
  items = relationship("InvoiceItem")
  client = relationship(Client)

  @property
  def No(self):
    return str(self.Id).zfill(4)

  @property
  def Total(self):
    return round(sum(i.Total for i in self.items), 2)

  @property
  def InvDate(self):
    return datetime.fromtimestamp(self.Date/1000)

  @property
  def InvDate_asStr(self):
    return self.InvDate.strftime("%d.%m.%Y")

  def get_byNo(invno):
    return session.query(Invoice).filter(Invoice.Id == invno).first()

  def get_inDateRange(startdate, enddate):
    startdate = int(startdate.strftime('%s')) * 1000
    enddate = int(enddate.strftime('%s')) * 1000
    return session.query(Invoice).filter(Invoice.Date > startdate, Invoice.Date < enddate)


class InvoiceItem(Base):
  __tablename__ = "InvoiceItems"

  Id = Column(Integer, primary_key=True)
  Title = Column(Text)
  Quantity = Column(Numeric(scale=2))
  Value = Column(Numeric(scale=2))
  Total = Column(Numeric(scale=2))
  Description = Column(Text)
  fk_Clients = Column(Integer, ForeignKey("Clients.Id"))
  fk_Invoices = Column(Integer, ForeignKey("Invoices.Id"))

  @property
  def hasDescription(self):
    return bool(self.Description.strip())

  @property
  def Description_parsed(self):
    return self.Description.replace("\\n", "\r\n")

class Time(Base):
  __tablename__ = "Times"

  Id = Column(Integer, primary_key=True)
  Start = Column(Text)
  End = Column(Text)
  Title = Column(Text)
  Description = Column(Text)
  Archived = Column(Integer, default=0)
  fk_Clients = Column(Integer, ForeignKey("Clients.id"))
  fk_InvoiceItems = Column(Integer, ForeignKey("InvoiceItems.id"))


