import xlrd as xl
import csv
import os
import dateparser
from config import *
from utils import *

class Repair:
  def __init__(self,year=None,country=None,hospital=None,engineers=None,
               equipment=None,oem=None,model=None,sn=None,fix=None,result=None,notes=None):
    self.year      = year
    self.country   = country
    self.hospital  = hospital
    self.engineers = engineers
    self.equipment = equipment
    self.oem       = oem
    self.model     = model
    self.sn        = sn
    self.fix       = fix
    self.result    = result
    self.notes     = notes
  def dir(self):
    return ['year','country','hospital','equipment','fix','result']
  def __str__(self):
    return print_obj(self)
  def __repr__(self):
    return self.equipment+':'+self.result

class WorkSummaryForm:
  def __init__(self,xlfile=None,country=None,date=None,hospital=None,engineers=None,repairs=None):
    self.file      = xlfile
    self.date      = date
    self.hospital  = hospital
    self.country   = country
    self.engineers = engineers
    self.repairs   = repairs
    xlfile = self.open_WSF()
    if xlfile is not None:
      if self.date is None:
        self.date = make_date(get_data_by_key(xlfile,'date'),xlfile.book.datemode)
      if self.country is None:
        self.country = str(get_data_by_key(xlfile,'country'))
      if self.hospital is None:
        self.hospital = str(get_data_by_key(xlfile,'hospital'))
      if self.engineers is None:
        self.engineers = str(get_data_by_key(xlfile,'engineers'))
      if self.repairs is None:
        self.get_repairs()
    #else:
      # fail gracefully

  def dir(self):
    return ['date','country','hospital','engineers','repairs']

  def __str__(self):
    return print_obj(self)

  def __repr__(self):
    return str(self.date.year)+':'+self.country+':'+self.hospital

  def open_WSF(self):
    if os.path.exists(self.file):
      return xl.open_workbook(filename=self.file).sheet_by_name('Work Summary Form')
    else:
      return None

  def get_repairs(self):
    xlfile = self.open_WSF()
    self.repairs = []
    for row in range(idx['equip']['0'],xlfile.nrows):
      equipment = str(get_data_by_idx (xlfile,row,idx['equip']['type']))
      oem       = str(get_data_by_idx (xlfile,row,idx['equip']['oem']))
      model     = str(get_data_by_idx (xlfile,row,idx['equip']['model']))
      sn        = str(get_data_by_idx (xlfile,row,idx['equip']['sn']))
      notes     = str(get_data_by_idx (xlfile,row,idx['repair']['notes']))
      fix       = str(get_switch_data(xlfile,[row],idx['repair']['type'],lut['fix']))
      result    = str(get_switch_data(xlfile,[row],idx['repair']['result'],lut['result']))
      if equipment and result: # define required fields
        repair = Repair(year      = self.date.year,
                        country   = self.country,
                        hospital  = self.hospital,
                        engineers = self.engineers,
                        equipment = equipment,
                        oem       = oem,
                        model     = model,
                        sn        = sn,
                        fix       = fix,
                        notes     = notes,
                        result    = result)
        self.repairs.append(repair)

def get_data_by_key(xlfile,idxkey):
  return xlfile.cell_value(*idx[idxkey])

def get_data_by_idx(xlfile,r,c):
  return xlfile.cell_value(r,c)

def get_switch_data(xlfile,row,col,lutname):
  cells = []
  for r in row:
    for c in col:
      cells.append(bool(xlfile.cell_value(r,c)))
  res = [s for (s,b) in zip(csv_LUT(lutname),cells) if b]
  if res:
    return res[0]
  else:
    return None

def make_date(rawDate,datemode=0):
  try:
    date = xl.xldate.xldate_as_datetime(rawDate,datemode)
  except:
    date = dateparser.parse(rawDate)
  return date

def get_all_work_summary_forms(root):
  WSF = []
  for (paths,dirs,files) in os.walk(root):
    for f in files:
      WSF.append(WorkSummaryForm(os.path.join(paths,f)))
  return WSF
