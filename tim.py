#!/usr/bin/python3

import argparse
import sys
import os
import subprocess

from tempfile import NamedTemporaryFile
from relatorio.templates.opendocument import Template
from datetime import datetime
from dateutil.parser import parse
from Database import *
from pprint import pprint
from pathlib import Path

from tempfile import NamedTemporaryFile

def printf(fmtstr, args):
  sys.stdout.write(fmtstr % tuple(args))

def invoice(args):
  invoices = []
  # fetch part
  if args.from_date or args.to_date or not args.invoice_no:
    startdate = parse(args.from_date) if args.from_date else parse('01-01-1970')
    enddate = parse(args.to_date) if args.to_date else datetime.now()
    invoices = Invoice.get_inDateRange(startdate, enddate)
  if args.invoice_no:
    invoices = [Invoice.get_byNo(args.invoice_no)]

  # action part
  if args.action == 'print':
    create_invoice(args, invoices)
  if args.action == 'list':
    ilist = []
    for i in invoices:
      ilist.append({
        "Inv. No.": i.No,
        "Client Name": i.client.Name,
        "Date": i.InvDate,
        "Total Sum": i.Total
      })
    print_table(ilist, ilist[0].keys())

def print_table(list_of_objects, fields):
  lengths = { f : len(f) for f in fields }
  for o in list_of_objects:
    for f in fields:
      val = str(o[f])
      if len(val) > lengths[f]:
        lengths[f] = len(val)

  pattern = " | ".join([f"%-{lengths[l]}s" for l in lengths.keys()])
  pattern = pattern + "\n"

  printf(pattern, fields) # print header
  for o in list_of_objects:
    printf(pattern, [o[f] for f in fields])

def create_invoice(args, invoices):
  for inv in invoices:
    class Obj(object):
      pass
    o = Obj()
    setattr(o, 'invoice', inv)
    setattr(o, 'customer', inv.client)

    if args.verbose:
      print("Client: " + o.customer.Name)
      print("Invoice: " + inv.No)
      print("Date: " + inv.InvDate.strftime("%d.%m.%Y"))
      for item in inv.items:
        print("%d | %d | %d | %30s" % (item.Quantity, item.Value, item.Total, item.Title))
      print("Grand Total: " + str(inv.Total))

    tpl = Template(source='', filepath="invoice_template.odt")
    generated = tpl.generate(o=o).render()
    temp_odt_file = NamedTemporaryFile(suffix='.odt', delete=True)
    temp_odt_file.write(generated.getvalue())
    subprocess.call(['libreoffice', '--headless', '--convert-to', 'pdf', temp_odt_file.name, '--outdir', 'files'])
    #fname = re.sub(r'.odt$', '', temp_odt_file.name)
    fname = Path(temp_odt_file.name).stem
    os.rename("./files/" + fname + ".pdf", "./files/" + inv.No + ".pdf")
    temp_odt_file.close()

def invoice_help():
  print("Usage: tim invoice ACTION --invoice-no <INVOICE_NO>")
  print("\tACTION\n\t\tCan be 'print'.")
  print("\tINVOICE_NO\n\t\tThe invoice number to work on.")

parser = argparse.ArgumentParser()
parser.add_argument('--verbose', '-v', action='count', default=0)
subparsers = parser.add_subparsers(help='sub-command help')

p_invoice = subparsers.add_parser('invoice', aliases=['inv'], help='invoice help')
p_invoice.set_defaults(func=invoice)
p_invoice.add_argument('action')
p_invoice.add_argument('--invoice-no', type=str)
p_invoice.add_argument('--from', dest='from_date', type=str)
p_invoice.add_argument('--to', dest='to_date', type=str)

args = parser.parse_args()
if not len(sys.argv) > 1:
  invoice_help()
  exit(0)
args.func(args)
