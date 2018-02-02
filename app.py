import os
import re
import sys
import csv
import xlrd
import shutil
import traceback
import dateparser

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output
from flask import send_from_directory
from collections import OrderedDict

# Config -----------------------------------------------------------------------

verbose = True
lut = {}
lut['year']      = os.path.join('static','list-year.csv')
lut['fix']       = os.path.join('static','list-fix.csv')
lut['result']    = os.path.join('static','list-result.csv')
lut['country']   = os.path.join('static','list-country.csv')
lut['equipment'] = os.path.join('static','list-equipment.csv')
lut['table']     = os.path.join('static','def-table.csv')
wsf = {}
wsf['root']   = os.path.join('data')
wsf['output'] = os.path.join('static','repairs.csv')
idx = {}
idx['sheet']     = 0
idx['date']      = 'C6'
idx['country']   = 'C7'
idx['engineers'] = 'K6'
idx['hospital']  = 'K7'
idx['repair'] = {}
idx['repair']['row0']   = '11'
idx['repair']['equip']  = 'B'
idx['repair']['oem']    = 'C'
idx['repair']['model']  = 'D'
idx['repair']['sn']     = 'E'
idx['repair']['fix']    = 'FGHIJKL'
idx['repair']['notes']  = 'M'
idx['repair']['result'] = 'NO'
sql = {}
sql['connect'] = {}
sql['connect']['user'] = 'ewh'
sql['connect']['password'] = 'repairs'
sql['connect']['host'] = '127.0.0.1'
sql['database'] = 'repairs'
sql['schema'] = {}
sql['schema']['repair'] = os.path.join('repair-schema.csv')

# Classes & Workers ------------------------------------------------------------

class ExcelFile:
  def __init__(self,filename,sheet):
    self.filename = filename
    self.sheet = sheet

  def open(self):
    if os.path.exists(self.filename):
      return xlrd.open_workbook(filename=self.filename).sheet_by_index(self.sheet)

  def col(self,colStr):
    idxs = [match for match in re.compile('(\D+?)').findall(colStr)]
    return reduceList([ord(c.upper())-65 for c in [idx for idx in idxs]])

  def row(self,rowStr):
    idxs = [match for match in re.compile('(\d+)').findall(rowStr)]
    return reduceList([int(r)-1 for r in [idx for idx in idxs]])

  def row_col(self,idxStr):
    idxs = [match for match in re.compile('(\D+?)(\d+)').findall(idxStr)]
    return reduceList([(int(r)-1,ord(c.upper())-65) for (c,r) in [idx for idx in idxs]])

  def date(self,rawDate,datemode=0,defaultyear=''):
    if rawDate:
      try:
        date = xlrd.xldate.xldate_as_datetime(rawDate,datemode)
      except:
        date = dateparser.parse(rawDate)
      return date
    else:
      return dateparser.parse(defaultyear)

class WorkSummaryForm(ExcelFile):

  def __init__(self,filename):
    ExcelFile.__init__(self,filename,idx['sheet'])
    self.filename = filename
    self.lut      = self.load_luts()
    self.meta     = self.load_meta()
    self.repairs  = self.load_repairs()

  def load_luts(self):
    return {
      'result' : csv_to_list(lut['result']),
      'fix'    : csv_to_list(lut['fix'])
    }

  def load_meta(self):
    get = self.open().cell_value
    return {
      'country'  : string(get(*self.row_col(idx['country']))),
      'engineers': string(get(*self.row_col(idx['engineers']))),
      'hospital' : string(get(*self.row_col(idx['hospital']))),
      'year'     : string(self.date('',defaultyear=self.defaultyear()).year)
      #'year'     : string(self.date(get(*self.row_col(idx['date']))))
    }

  def load_repairs(self):
    sheet = self.open()
    get   = sheet.cell_value
    repairs = []
    for row in range(self.row(idx['repair']['row0']),sheet.nrows):
      if get(row,self.col(idx['repair']['equip'])):
        repairs.append(dict({
          'equipment': string(get(row,self.col(idx['repair']['equip']))),
          'oem'      : string(get(row,self.col(idx['repair']['oem']))),
          'model'    : string(get(row,self.col(idx['repair']['model']))),
          'sn'       : string(get(row,self.col(idx['repair']['sn']))),
          'notes'    : string(get(row,self.col(idx['repair']['notes']))),
          'fix'      : self.switch_to_str(
                         [get(row,self.col(c)) for c in idx['repair']['fix']],
                         self.lut['fix']),
          'result'   : self.switch_to_str(
                         [get(row,self.col(c)) for c in idx['repair']['result']],
                         self.lut['result'])
        },**self.meta))

    return repairs

  def switch_to_str(self,index_list,lut):
    res = [s for (s,b) in zip(lut,index_list) if bool(b)]
    if res:
      return res[0]
    else:
      return None

  def defaultyear(self):
    yr = str(int(re.compile('/(.*) Work Summary Forms/').findall(self.filename)[0]))
    return yr

def string(s):
  try:
    return str(s).encode('utf-8')
  except:
    return s.encode('utf-8')

def csv_to_list(lutname):
  lut = []
  with open(lutname,'r') as csvfile:
    for row in csv.reader(csvfile):
      if len(row) == 1:
        lut += [cell.lstrip() for cell in row]
      else:
        lut.append([cell.lstrip() for cell in row])
  return lut

def reduceList(L):
  if len(L) == 0:
    return []
  elif len(L) == 1:
    return L[0]
  else:
    return L

def make_luts():
  LUT  = {}
  LUTA = {}
  for (key,value) in lut.iteritems():
    LUT[key]  = csv_to_list(value)
    LUTA[key] = ['All']+LUT[key]
  return LUT,LUTA

def parse_all_work_summary_forms(root,outFile):
  repairs = []
  i = 0
  for (paths,dirs,files) in os.walk(root):
    for f in files:
      filename = os.path.join(paths,f)
      if verbose:
        i += 1
        print('> ['+str(i).zfill(3)+']: '+filename)
      # form = WorkSummaryForm(filename)
      # repairs += form.repairs
      try:
        form = WorkSummaryForm(filename)
        repairs += form.repairs
      except Exception as e:
        print('\033[F> [ ! ]: ')
        exc_type, exc_obj, exc_tb = sys.exc_info()
        traceback.print_tb(exc_tb)

  with open(outFile,'w') as csvOutFile:
    writer = csv.writer(csvOutFile)
    writer.writerow(repairs[0].keys())
    for value in repairs:
      writer.writerow(value.values())

def load_all_repairs(inFile):
  repairs = []
  with open(inFile,'r') as csvInFile:
    reader = csv.reader(csvInFile)
    header = next(reader)
    for row in reader:
      repairs.append({key:str(value) for key,value in zip(header,row)})
  return repairs

def make_filters(year_idx,country_idx,equip_idx):
  return {'year':     LUTA['year'][year_idx],
          'country':  LUTA['country'][country_idx],
          'equipment':LUTA['equipment'][equip_idx]}

def filter_dict_list_by_dict(dictList,dictFilter,asType=str):
  return [d for d in dictList if
          all((asType(d[key]) in value) or (value in [None,'*','All','all'])
          for key,value in dictFilter.iteritems())]

def count_dict_list_value(dictList,key,values,asType=str):
  return [[asType(d[key]) for d in dictList].count(value) for value in values]

def remove_zeros(values,labels):
  if values.count(0) is not len(values):
    return zip(*((v,l) for v,l in zip(values,labels) if v is not 0))
  else:
    return [],[]

# Initializations & Data -------------------------------------------------------
parse_all_work_summary_forms(wsf['root'],wsf['output']) # need only once
app = dash.Dash(__name__)
app.css.append_css({'external_url':'static/custom.css'})
server = app.server
LUT,LUTA = make_luts()
repairs = load_all_repairs(wsf['output'])

# Misc Functions ---------------------------------------------------------------

@app.server.route('/static/<path:path>')
def static_file(path):
    static_folder = os.path.join(os.getcwd(), 'static')
    return send_from_directory(static_folder, path)

# Layout Functions -------------------------------------------------------------

def make_dropdown(lutName,dropdownID):
  return html.Div([
    html.Div([lutName.title()+':'],style={'padding':'10px 10px 5px 10px'}),
    dcc.Dropdown(
      id=dropdownID,
      options=[{'label': [item], 'value': i} for (i,item) in enumerate(LUTA[lutName])],
      value=0)
    ],className='dropdown-container'
  )

def make_text_output(title,textid):
  return html.Div([
    html.Div([title+':'],style={'padding':'10px 10px 5px 10px'}),
      html.Div([
        html.Div(['51'],id=textid,style={'padding':'7px 10px 7px 10px'},
        className='Select-control output'),
      ],className='Select'),
    ],className='dropdown-container',style={'vertical-align':'bottom'},
  )

def make_pie(labels,values):
  return {
    'data': [go.Pie(
      labels=labels,
      values=values,
      hole=0.4,
      sort=False,
    )],
    'layout': go.Layout(
      margin={'l': 0, 'b': 120, 't': 0, 'r': 0, 'pad': 0},
      legend={'orientation':'h'},
      autosize=True,
    )
  }

def make_hbar(labels,values,nonZero=True):
  if nonZero:
    values,labels=remove_zeros(values,labels)
  return {
    'data': [go.Bar(
      x=values,
      y=labels,
      orientation='h'
    )],
    'layout': go.Layout(
      height=100+20*len(labels),
      margin=go.Margin(l=200, r=50, b=50, t=50, pad=0)
    )
  }

def make_table_row(row,header=False):
  if header:
    cellfun = html.Th
  else:
    cellfun = html.Td
  return [html.Tr([cellfun(h) for h in row])]

# Layout -----------------------------------------------------------------------

app.layout = html.Div([
  html.Div([
    html.Div([
      html.H1(['EWH Repair Database']),
      html.Div([
        html.A('Engineering World Health',href='http://www.ewh.org',target='_blank'),
        ' is a global organization which supports medical technology in the developing world. ',
        'Every year, as part of the EWH Summer Institute, students from around the world travel to low-resource countries to work alongside local technicians repairing medical equipment. ',
        'Each repair is logged and classified to help understand common challenges in these contexts.',
        html.Br(),html.Br(),
        'Below is an interactive summary of the repairs from Nicaragua, Rwanda, and Tanzania, from 2011 to 2015.'
      ]),
    ],className='panel-inner')
  ],className='panel-outer full-width'),
  html.Div([
    html.Div([
      make_dropdown('year','select-year'),
      make_dropdown('country','select-country'),
      make_dropdown('equipment','select-equipment'),
      make_text_output('Matching Repairs','match-count')
    ],className='panel-inner')
  ],className='panel-outer full-width'),
  html.Div([
    html.Div([
      html.H3(['Repair Result']),
      dcc.Graph(id='pie-result',style={'display':'inline-block','width':'100%'})
    ],className='panel-inner')
  ],className='panel-outer half-width'),
  html.Div([
    html.Div([
      html.H3(['Repair Type']),
      dcc.Graph(id='pie-fix',style={'display':'inline-block','width':'100%'})
    ],className='panel-inner')
  ],className='panel-outer half-width'),
  html.Div([
    html.Div([
      html.H3(['Equipment Type']),
      dcc.Graph(id='bar-equipment')
    ],className='panel-inner')
  ],className='panel-outer full-width'),
  html.Div([
    html.Div([
      html.H3(['Repair Notes']),
      dcc.Checklist(id='table-toggles',
        options=[{'label':label,'value':value,'class':'test'} \
                 for label,value in LUT['table']],
        values=['equipment','model','notes']),
      html.Table(id='repair-table',
               style={'display':'inline-block','margin':'10px 0px 10px 0px'})
    ],className='panel-inner')
  ],className='panel-outer full-width'),
],style={'width':'80%','margin':'0% 8% 8% 8%'})

# Callback Functions -----------------------------------------------------------

@app.callback(
  Output('match-count','children'),
 [Input('select-year','value'),
  Input('select-country','value'),
  Input('select-equipment','value')])
def update_total_repairs(year_idx,country_idx,equip_idx):
  return len(filter_dict_list_by_dict(
    repairs,make_filters(year_idx,country_idx,equip_idx),asType=str))

@app.callback(
  Output('pie-result','figure'),
 [Input('select-year','value'),
  Input('select-country','value'),
  Input('select-equipment','value')])
def update_pie_result(year_idx,country_idx,equip_idx):
  repairs_filtered = filter_dict_list_by_dict(
    repairs,make_filters(year_idx,country_idx,equip_idx),asType=str)
  results = count_dict_list_value(repairs_filtered,'result',LUT['result'],asType=str)
  return make_pie(LUT['result'],results)

@app.callback(
  Output('pie-fix','figure'),
 [Input('select-year','value'),
  Input('select-country','value'),
  Input('select-equipment','value')])
def update_pie_fix(year_idx,country_idx,equip_idx):
  repairs_filtered = filter_dict_list_by_dict(
    repairs,make_filters(year_idx,country_idx,equip_idx),asType=str)
  results = count_dict_list_value(repairs_filtered,'fix',LUT['fix'],asType=str)
  return make_pie(LUT['fix'],results)

@app.callback(
  Output('bar-equipment','figure'),
 [Input('select-year','value'),
  Input('select-country','value'),
  Input('select-equipment','value')])
def update_bar(year_idx,country_idx,equip_idx):
  repairs_filtered = filter_dict_list_by_dict(
    repairs,make_filters(year_idx,country_idx,equip_idx),asType=str)
  bar = count_dict_list_value(repairs_filtered,'equipment',LUT['equipment'])
  return make_hbar(LUT['equipment'],bar)

@app.callback(
  Output('repair-table','children'),
 [Input('select-year','value'),
  Input('select-country','value'),
  Input('select-equipment','value'),
  Input('table-toggles','values')])
def update_notes(year_idx,country_idx,equip_idx,table_cols):
  filters = {'year':     LUTA['year'][year_idx],
             'country':  LUTA['country'][country_idx],
             'equipment':LUTA['equipment'][equip_idx]}
  repairs_filtered = filter_dict_list_by_dict(repairs,filters,asType=str)
  header,keys = zip(*[row for row in LUT['table'] if row[1] in table_cols])
  table = make_table_row(header,header=True)
  for row in zip(*[[repair[key] for repair in repairs_filtered] for key in keys]):
    table += make_table_row(list(row))
  return table

if __name__ == '__main__':
  app.run_server(debug=True)
  #app.run()
