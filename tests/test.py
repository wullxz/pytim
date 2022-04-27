#!/usr/bin/python3
# -*- coding: utf-8 -*-

from pprint import pprint
from Database import *
import argparse

parser = argparse.ArgumentParser(description="TIM: Time Is Money - time tracking and invoice hacking")
# global args
parser.add_argument('--verbose', '-v', action='count', default=0)


db = Database()
ses = db.get_session()

res = ses.query(InvoiceItem).filter(Invoice.Id == 13)
for r in res:
  print(r.Title, str(r.Quantity), str(r.Value), str(r.Total))
#res = ses.query(Client).filter(Client.Name.like('%o%'))
#for r in res:
#  print(r.Name)
