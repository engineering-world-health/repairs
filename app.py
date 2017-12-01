import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from flask import send_from_directory
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
    #style={'max-width':'100%','min-width':'50%'},
    className='dropdown-container'
  )

def make_pie(labels,values):
  return {
    'data': [go.Pie(
      labels=labels,
      values=values
    )],
    'layout': go.Layout(
      width='100%'
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
      width=800,
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
    html.H1(['EWH Repair Database']),
  ],className='h1-container'),
  html.Div([
  html.Div([
      html.H3(['Repair Outcome']),
      make_dropdown('year','select-year-pie-result'),
      make_dropdown('country','select-country-pie-result'),
      make_dropdown('equipment','select-equip-pie-result'),
      dcc.Graph(id='pie-result',style={'display':'inline-block'})
    ], className='panel-container'
  ),
  html.Div([
      html.H3(['Repair Type']),
      make_dropdown('year','select-year-pie-fix'),
      make_dropdown('country','select-country-pie-fix'),
      make_dropdown('equipment','select-equip-pie-fix'),
      dcc.Graph(id='pie-fix',style={'display':'inline-block'})
    ], className='panel-container'
  )]),
  html.Div([
  html.Div([
      html.H3(['Equipment Type']),
      make_dropdown('year','select-year-bar-equipment'),
      make_dropdown('country','select-country-bar-equipment'),
      dcc.Graph(id='bar-equipment')
    ], className='panel-container'
  )]),
  html.Div([
  html.Div([
    html.H3(['Repair Notes']),
    make_dropdown('year','select-year-notes'),
    make_dropdown('country','select-country-notes'),
    make_dropdown('equipment','select-equip-notes'),
    html.Table(id='repair-notes',
               style={'display':'inline-block','margin':'10px 0px 10px 0px'})
  ], className='panel-container'
  )])
], style={'width':'80%','margin':'0% 8% 8% 8%'}
)

# Callback Functions -----------------------------------------------------------

@app.callback(
  dash.dependencies.Output('pie-result','figure'),
 [dash.dependencies.Input('select-year-pie-result','value'),
  dash.dependencies.Input('select-country-pie-result','value'),
  dash.dependencies.Input('select-equip-pie-result','value')])
def update_pie_result(year_idx,country_idx,equip_idx):
  filters = {'year':     LUTA['year'][year_idx],
             'country':  LUTA['country'][country_idx],
             'equipment':LUTA['equipment'][equip_idx]}
  repairs_filtered = filter_obj_list_multi(repairs,filters,asType=str)
  results = count_obj_list_by_attr(repairs_filtered,'result',LUT['result'],asType=str)
  return make_pie(LUT['result'],results)

@app.callback(
  dash.dependencies.Output('pie-fix','figure'),
 [dash.dependencies.Input('select-year-pie-fix','value'),
  dash.dependencies.Input('select-country-pie-fix','value'),
  dash.dependencies.Input('select-equip-pie-fix','value')])
def update_pie_fix(year_idx,country_idx,equip_idx):
  filters = {'year':     LUTA['year'][year_idx],
             'country':  LUTA['country'][country_idx],
             'equipment':LUTA['equipment'][equip_idx]}
  repairs_filtered = filter_obj_list_multi(repairs,filters,asType=str)
  results = count_obj_list_by_attr(repairs_filtered,'fix',LUT['fix'],asType=str)
  return make_pie(LUT['fix'],results)

@app.callback(
  dash.dependencies.Output('bar-equipment','figure'),
 [dash.dependencies.Input('select-year-bar-equipment','value'),
  dash.dependencies.Input('select-country-bar-equipment','value')])
def update_bar(year_idx,country_idx):
  filters = {'year':   LUTA['year'][year_idx],
             'country':LUTA['country'][country_idx]}
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
  dash.dependencies.Output('repair-notes','children'),
 [dash.dependencies.Input('select-year-notes','value'),
  dash.dependencies.Input('select-country-notes','value'),
  dash.dependencies.Input('select-equip-notes','value')])
def update_notes(year_idx,country_idx,equip_idx):
  filters = {'year':     LUTA['year'][year_idx],
             'country':  LUTA['country'][country_idx],
             'equipment':LUTA['equipment'][equip_idx]}
  repairs_filtered = filter_obj_list_multi(repairs,filters,asType=str)
  equips = get_attr_from_obj_list(repairs_filtered,'equipment')
  models = get_attr_from_obj_list(repairs_filtered,'model')
  notes  = get_attr_from_obj_list(repairs_filtered,'notes')
  table = make_table_row(['Equipment','Model','Notes'],header=True)
  for equip,model,note in zip(equips,models,notes):
    table += make_table_row([equip,model,note])
  return table

if __name__ == '__main__':
  app.run_server(debug=True)
  #app.run()
