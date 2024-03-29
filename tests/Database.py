from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, Text, Numeric
from sqlalchemy.orm import sessionmaker, relationship

# Don't warn about precision of decimal values in SQLite
# It's very much sufficient as long as I don't earn Millions
import warnings
from sqlalchemy.exc import SAWarning
warnings.filterwarnings('ignore', r".*support Decimal objects natively", SAWarning, r'^sqlalchemy\.sql\.sqltypes$')


Base = declarative_base()

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

class Invoice(Base):
  __tablename__ = "Invoices"

  Id = Column(Integer, primary_key=True)
  Date = Column(Text)
  fk_Clients = Column(Integer, ForeignKey("Clients.id"))

class InvoiceItem(Base):
  __tablename__ = "InvoiceItems"

  Id = Column(Integer, primary_key=True)
  Title = Column(Text)
  Quantity = Column(Numeric)
  Value = Column(Numeric)
  Total = Column(Numeric)
  Description = Column(Text)
  fk_Clients = Column(Integer, ForeignKey("Clients.id"))
  fk_Invoices = Column(Integer, ForeignKey("Invoices.id"))

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


class Database():
  def __init__(self, db_file='sqlite:///db.sqlite'):
    self.db_file = db_file
    self.eng = create_engine(self.db_file)

  def create_database(self, db_file):
    Base.metadata.create_all(self.eng)

  def get_session(self):
    Session = sessionmaker(bind=self.eng)
    ses = Session()
    return ses

