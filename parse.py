from collections import OrderedDict as odict
import os
import json
import csv
import xlrd

root  = os.path.dirname(__file__)
path = {
  'raw':   os.path.join(root,'raw'),
  'csv':   os.path.join(root,'repairs.csv'),
  'meta':  os.path.join(root,'meta.json'),
}

with open(path['meta']) as f:
  meta = json.load(f,object_pairs_hook=odict)

def get_wsf_repairs(fname):
  x = xlrd.open_workbook(filename=fname).sheet_by_index(0)

  # index functions: c-1 based to 0-0
  def row_fun(row):
    return int(row)-1
  def col_fun(col):
    return ord(col.upper())-65

  # pre-compute some constants
  r0 = row_fun(meta['Model']['row-1'])
  r1 = x.nrows
  slicer = slice(r0,r1)
  required = [label.get('required',False) for label in meta.values()]

  def get_year(fname):
    return fname.split(os.path.sep)[-2]

  def get_cell(label):
    return str(x.cell_value(row_fun(meta[label]['row']),col_fun(meta[label]['col'])))

  def repeat(value):
    return [value]*(r1-r0)

  def get_repair_col(label):
    return list(map(str,x.col_values(col_fun(meta[label]['col']))[slicer]))

  def get_repair_col_map(label):
    def bool_to_str(bools):
      return ', '.join([value for b,value in zip(bools,meta[label]['values']) if b])
    bcols = [list(map(bool,x.col_values(col_fun(col))[slicer])) for col in meta[label]['col']]
    return list(map(bool_to_str,zip(*bcols)))

  def filter_by_required(values):
    return all(bool(value) for b,value in zip(required,values) if b)

  # do the work
  return filter(filter_by_required,list(map(list,zip(
    repeat(get_year(fname)),
    repeat(get_cell('Country').capitalize()),
    repeat(get_cell('Hospital')),
    get_repair_col('Manufacturer'),
    get_repair_col('Model'),
    get_repair_col('Serial Number'),
    get_repair_col_map('Fix Type'),
    get_repair_col_map('Repair Result'),
    get_repair_col('Notes'),
  ))))

# main
repairs = [list(meta.keys())]
for (base,dirs,files) in os.walk(path['raw']):
  for file in files:
    repairs.extend(get_wsf_repairs(os.path.join(base,file)))

with open(path['csv'],'w') as f:
  w = csv.writer(f,delimiter=',',quotechar='"')
  w.writerows(repairs)
