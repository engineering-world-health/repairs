import os
import re
import csv
import xlrd
import json
import argparse
import dateparser
from collections import OrderedDict as odict

# Config -----------------------------------------------------------------------

verbose = False
pdir = os.path.dirname(__file__)
wsf = os.path.join(pdir,'..','data')
csvdb = os.path.join(pdir,'data.csv')
lut = json.load(open(os.path.join(pdir,'meta.json')),object_pairs_hook=odict)
idx = json.load(open(os.path.join(pdir,'idx.json')),object_pairs_hook=odict)

# Classes & Workers ------------------------------------------------------------

class ExcelFile:
  def __init__(self,filename,sheet=0):
    self.filename = filename
    self.sheet = int(sheet)

  def open(self):
    if os.path.exists(self.filename):
      return xlrd.open_workbook(filename=self.filename).sheet_by_index(self.sheet)

  def col(self,colStr):
    idxs = [match for match in re.compile('(\D+?)').findall(colStr)]
    return reduce_list([ord(c.upper())-65 for c in [idx for idx in idxs]])

  def row(self,rowStr):
    idxs = [match for match in re.compile('(\d+)').findall(rowStr)]
    return reduce_list([int(r)-1 for r in [idx for idx in idxs]])

  def row_col(self,idxStr):
    idxs = [match for match in re.compile('(\D+?)(\d+)').findall(idxStr)]
    return reduce_list([(int(r)-1,ord(c.upper())-65) for (c,r) in [idx for idx in idxs]])

  def date(self,rawDate,datemode=0,defaultyear=''):
    if rawDate:
      try:
        date = xlrd.xldate.xldate_as_datetime(rawDate,datemode)
      except:
        date = dateparser.parse(rawDate)
      return date
    else:
      return dateparser.parse(defaultyear)

  def get(self,*args): # need optimization for repeated calls...
    return self.open().cell_value(*args)

class CSVTable:

  def __init__(self,name,header):
    self.name = name
    self.header = header
    self.create()

  def __str__(self):
    pass

  def create(self):
    if verbose:
      print('> CREATING TABLE: {}'.format(self.name))
    with open(self.name,'a+') as csvfile:
      if sum(1 for row in csv.reader(csvfile)) == 0:
        csv.writer(csvfile).writerow(self.header)

  def delete(self):
    if verbose:
      print('> DELETING TABLE: {}'.format(self.name))
    os.remove(self.name)

  def add_row(self,rowDict,commit=None):
    with open(self.name,'a+') as csvfile:
      csv.writer(csvfile).writerow(rowDict.values())

  def add_rows(self,rowDictList,commit=None):
    with open(self.name,'a+') as csvfile:
      writer = csv.writer(csvfile)
      for rowDict in rowDictList:
        writer.writerow(rowDict.values())

  def get_rows(self):
    rows = []
    with open(self.name,'r+') as csvfile:
      for row in csv.reader(csvfile):
        rows.append(row)
    return rows

  def get_header(self):
    return self.header

  def count_rows(self):
    with open(self.name,'r+') as csvfile:
      return sum(1 for row in csv.reader(csvfile))-1

  def commit(self):
    pass

class WorkSummaryForm(ExcelFile):

  def __init__(self,filename):
    ExcelFile.__init__(self,filename,idx['sheet'])
    if verbose:
      print('> LOADING REPAIRS IN: {}'.format(filename))
    self.filename = filename
    self.lut      = self.load_luts()
    self.meta     = self.load_meta()
    self.repairs  = self.load_repairs()

  def load_luts(self):
    return {
      'result' : lut['pies']['result'],
      'fix'    : lut['pies']['fix']
    }

  def load_meta(self):
    get = self.open().cell_value
    return odict([
     #'year'     : str(self.date(get(*self.row_col(idx['date']))).year),
      ('year'     , str(self.date('',defaultyear=self.defaultyear()).year)),
      ('country'  , str(get(*self.row_col(idx['country'])))),
      ('hospital' , str(get(*self.row_col(idx['hospital'])))),
      ('engineers', str(get(*self.row_col(idx['engineers'])))),
      ])

  def load_repairs(self):
    sheet = self.open()
    get = sheet.cell_value
    repairs = []
    for row in range(self.row(idx['repair']['row0']),sheet.nrows):
      if get(row,self.col(idx['repair']['equip'])):
        repair = odict(list(self.meta.items())+[
          ('equipment', str(get(row,self.col(idx['repair']['equip'])))),
          ('oem'      , str(get(row,self.col(idx['repair']['oem'])))),
          ('model'    , str(get(row,self.col(idx['repair']['model'])))),
          ('sn'       , str(get(row,self.col(idx['repair']['sn'])))),
          ('fix'      , self.switch_to_str(
                         [get(row,self.col(c)) for c in idx['repair']['fix']],
                         self.lut['fix'])),
          ('result'   , self.switch_to_str(
                         [get(row,self.col(c)) for c in idx['repair']['result']],
                         self.lut['result'])),
          ('notes'    , str(get(row,self.col(idx['repair']['notes'])))),
        ])
        if verbose:
          print('  > LOADED: {}'.format(repair_str(repair)))
        repairs.append(repair)
    return repairs

  def switch_to_str(self,index_list,lut):
    res = [s for (s,b) in zip(lut,index_list) if bool(b)]
    if res:
      return str(res[0])
    else:
      return None

  def defaultyear(self):
    return str(int(re.compile('.*/(.*) Work Summary Forms/').findall(self.filename)[0]))

def reduce_list(L):
  if len(L) == 0:
    return []
  elif len(L) == 1:
    return L[0]
  else:
    return L

def repair_str(repair):
  return str(repair['equipment']+': '+repair['model'])

def parse_all_work_summary_forms(D,T):
  repairs = []
  if verbose:
    print('LOADING WORK SUMMARY FORMS')
  for (paths,dirs,files) in os.walk(D):
    for f in files:
      form = WorkSummaryForm(os.path.join(paths,f))
      repairs += form.repairs
  if verbose:
    print('> UPDATING DATABASE: {}'.format(T.name))
  T.add_rows(repairs,commit=True)
  for repair in repairs:
    #T.add_row(repair,commit=False)
    if verbose:
      print('  > ADDED: {}'.format(repair_str(repair)))
  T.commit()

def load_all_repairs(T):
  if verbose:
    print('> LOADING REPAIRS IN: {}'.format(T.name))
  repairs = []
  header = T.get_header()
  for row in T.get_rows():
    repairs.append(odict([(key,str(value)) for key,value in zip(header,row)]))
    print('  > LOADED: {}'.format(repair_str(repair)))
  return repairs

def init_table(args):
  def init(csvname):
    return CSVTable(csvname, lut['cols'])
  if verbose:
    print('INITIALIZING DATABASE')
  T = init(args['c'])
  if args['o']:
    T.delete()
    T = init(args['c'])
  return T

def get_cli():
  cli = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,\
    description='''\
    Utility for parsing and transferring EWH Repair logs from Work Summary Forms
    to a local CSV database.''')
  cli.add_argument('-d', metavar='DIR', default=wsf, help='''\
    Parent directory containing all Work Summary Forms to be parsed
    and added to the database
      Optional - default is: {}'''.format(wsf))
  cli.add_argument('-c', metavar='CSV', default=csvdb, help='''\
    Name of a local CSV file for storing the repair logs
      Optional - default is: {}'''.format(csvdb))
  cli.add_argument('-o', action='store_true', help='''\
    Flag: Overwrite the existing repair logs database
      Optional - default is: append repair logs to the database''')
  cli.add_argument('-x', action='store_true', help='''\
    Flag: Do not add any repair logs to the database
      Optional - default is: add from all Work Summary Forms''')
  cli.add_argument('-n', action='store_true', help='''\
    Flag: Count the number of logs in the database
      Optional - default is: off''')
  cli.add_argument('-v', action='store_true', help='''\
    Flag: Display verbose information
      Optional - default is: off''')
  args = vars(cli.parse_args())
  return args

if __name__ == '__main__':
  # load the command line arguments
  args = get_cli()

  # set the verbosity flag
  verbose = args['v']

  # initialize the database CSV table
  T = init_table(args)

  # parse all work summary forms and add the repairs to the database
  if not args['x']:
    parse_all_work_summary_forms(args['d'],T)

  # count repair logs in the table
  if args['n']:
    print('# Repairs: '+str(T.count_rows()))
