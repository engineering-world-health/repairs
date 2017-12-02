import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output
from flask import send_from_directory
from collections import OrderedDict
from ewhdata import *
from config import *
from utils import *

# Initializations & Data -------------------------------------------------------
app = dash.Dash(__name__)
app.css.append_css({'external_url':'static/custom.css'})
server = app.server
# lookup tables
LUT  = {}
LUTA = {}
for (key,value) in lut.iteritems():
  LUT[key]  = csv_LUT(value)
  LUTA[key] = ['All']+LUT[key]
# get all repair entries from forms
forms = get_all_work_summary_forms(wsf['root'])
repairs = get_attr_from_obj_list(forms,'repairs',merge=True)

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
    ],
    className='dropdown-container'
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
      autosize=True
    )
  }

def make_hbar(labels,values):
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
    ],className='panel-inner')
  ],className='panel-outer full-width'),
  html.Div([
    html.Div([
      make_dropdown('year','select-year'),
      make_dropdown('country','select-country'),
      make_dropdown('equipment','select-equipment'),
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
], style={'width':'80%','margin':'0% 8% 8% 8%'}
)

# Callback Functions -----------------------------------------------------------

@app.callback(
  Output('pie-result','figure'),
 [Input('select-year','value'),
  Input('select-country','value'),
  Input('select-equipment','value')])
def update_pie_result(year_idx,country_idx,equip_idx):
  filters = {'year':     LUTA['year'][year_idx],
             'country':  LUTA['country'][country_idx],
             'equipment':LUTA['equipment'][equip_idx]}
  repairs_filtered = filter_obj_list_multi(repairs,filters,asType=str)
  results = count_obj_list_by_attr(repairs_filtered,'result',LUT['result'],asType=str)
  return make_pie(LUT['result'],results)

@app.callback(
  Output('pie-fix','figure'),
 [Input('select-year','value'),
  Input('select-country','value'),
  Input('select-equipment','value')])
def update_pie_fix(year_idx,country_idx,equip_idx):
  filters = {'year':     LUTA['year'][year_idx],
             'country':  LUTA['country'][country_idx],
             'equipment':LUTA['equipment'][equip_idx]}
  repairs_filtered = filter_obj_list_multi(repairs,filters,asType=str)
  results = count_obj_list_by_attr(repairs_filtered,'fix',LUT['fix'],asType=str)
  return make_pie(LUT['fix'],results)

@app.callback(
  Output('bar-equipment','figure'),
 [Input('select-year','value'),
  Input('select-country','value'),
  Input('select-equipment','value')])
def update_bar(year_idx,country_idx,equip_idx):
  filters = {'year':     LUTA['year'][year_idx],
             'country':  LUTA['country'][country_idx],
             'equipment':LUTA['equipment'][equip_idx]}
  repairs_filtered = filter_obj_list_multi(repairs,filters,asType=str)
  if repairs_filtered:
    bar_year = count_obj_list_by_attr(repairs_filtered,'equipment',LUT['equipment'])
    bar_year_nonzero,equipment_nonzero = \
      zip(*((b,e) for b,e in zip(bar_year,LUT['equipment']) if b is not 0))
  else:
    equipment_nonzero = []
    bar_year_nonzero = []
  return make_hbar(equipment_nonzero,bar_year_nonzero)

@app.callback(
  Output('repair-table','children'),
 [Input('select-year','value'),
  Input('select-country','value'),
  Input('select-equipment','value'),
  Input('table-toggles','values')])
def update_notes(year_idx,country_idx,equip_idx,table_cols):
  # print table_cols
  filters = {'year':     LUTA['year'][year_idx],
             'country':  LUTA['country'][country_idx],
             'equipment':LUTA['equipment'][equip_idx]}
  repairs_filtered = filter_obj_list_multi(repairs,filters,asType=str)
  tablecols = OrderedDict([row for row in LUT['table'] if row[1] in table_cols])
  table     = make_table_row(tablecols.keys(),header=True)
  colData   = OrderedDict()
  for colAttr in tablecols.values():
    colData[colAttr] = get_attr_from_obj_list(repairs_filtered,colAttr)
  for rowData in zip(*colData.itervalues()):
    table += make_table_row(list(rowData))
  return table

if __name__ == '__main__':
  app.run_server(debug=True)
  #app.run()
