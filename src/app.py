import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from ewhdata import *
from config import *
from utils import *

# Initializations & Data -------------------------------------------------------
app = dash.Dash()
# lookup tables
LUT  = {}
LUTA = {}
for (key,value) in lut.iteritems():
  LUT[key]  = csv_LUT(value)
  LUTA[key] = ['All']+LUT[key]
# get all repair entries from forms
forms = get_all_work_summary_forms(wsf['root'])
repairs = get_attr_from_obj_list(forms,'repairs',merge=True)
repairs_year = filter_obj_list_by_attr(repairs,'year',LUTA['year'],asType=str)
repairs_equip = filter_obj_list_by_attr(repairs,'equipment',LUTA['equipment'],asType=str)

# Layout -----------------------------------------------------------------------
app.layout = html.Div([
  html.H1(['EWH Repair Database']),
  html.Div([
      html.H3(['Repair Outcome']),
      html.Div([dcc.Dropdown(
          id='select-year-pie-result',
          options=[{'label': [year], 'value': i} for (i,year) in enumerate(LUTA['year'])],
          value=0 )],style={'width':'200px','display':'inline-block'}),
      html.Div([dcc.Dropdown(
          id='select-equip-pie-result',
          options=[{'label': [equip], 'value': i} for (i,equip) in enumerate(LUTA['equipment'])],
          value=0 )],style={'width':'200px','display':'inline-block'}),
      dcc.Graph(id='pie-result')
    ], style={'width':'49%','display': 'inline-block'}
  ),
  html.Div([
      html.H3(['Repair Type']),
      html.Div([dcc.Dropdown(
          id='select-year-pie-fix',
          options=[{'label': [year], 'value': i} for (i,year) in enumerate(LUTA['year'])],
          value=0 )],style={'width':'200px','display':'inline-block'}),
      html.Div([dcc.Dropdown(
          id='select-equip-pie-fix',
          options=[{'label': [equip], 'value': i} for (i,equip) in enumerate(LUTA['equipment'])],
          value=0 )],style={'width':'200px','display':'inline-block'}),
      dcc.Graph(id='pie-fix')
    ], style={'width':'49%','display': 'inline-block'}
  ),
  html.Div([
      html.H3(['Equipment Type']),
      html.Div([dcc.Dropdown(
        id='select-year-bar-equipment',
        options=[{'label': [year], 'value': i} for (i,year) in enumerate(LUTA['year'])],
        value=0 )],style={'width':'200px'}),
      dcc.Graph(id='bar-equipment')
    ], style={'width':'98%','display': 'inline-block'}
  ),
], style={'width':'80%','margin':'0% 8% 8% 8%'}
)

# Functions --------------------------------------------------------------------
@app.callback(
  dash.dependencies.Output('pie-result','figure'),
 [dash.dependencies.Input('select-year-pie-result','value'),
 dash.dependencies.Input('select-equip-pie-result','value')])
def update_pie_result(year_idx,equip_idx):
  repairs_equip_year = filter_obj_list_by_attr(
    repairs_equip[equip_idx],'year',[LUTA['year'][year_idx]],asType=str)
  results_equip_year = count_obj_list_by_attr(
    repairs_equip_year[0],'result',LUT['result'],asType=str)
  return {
    'data': [go.Pie(
      labels=LUT['result'],
      values=results_equip_year
    )],
  }
@app.callback(
  dash.dependencies.Output('pie-fix','figure'),
 [dash.dependencies.Input('select-year-pie-fix','value'),
 dash.dependencies.Input('select-equip-pie-fix','value')])
def update_pie_fix(year_idx,equip_idx):
  # make list of fixes for this equipment & year
  repairs_equip_year = filter_obj_list_by_attr(
    repairs_equip[equip_idx],'year',[LUTA['year'][year_idx]],asType=str)
  # count repairs by result
  results_equip_year = count_obj_list_by_attr(
    repairs_equip_year[0],'fix',LUT['fix'],asType=str)
  return {
    'data': [go.Pie(
      labels=LUT['fix'],
      values=results_equip_year
    )],
  }
@app.callback(
  dash.dependencies.Output('bar-equipment','figure'),
 [dash.dependencies.Input('select-year-bar-equipment','value')])
def update_bar(year_idx):
  # count repairs by equipment
  bar_year = count_obj_list_by_attr(
    repairs_year[year_idx],'equipment',LUT['equipment'])
  # remove zero elements
  bar_year_nonzero,equipment_nonzero = \
    zip(*((b,e) for b,e in zip(bar_year,LUT['equipment']) if b is not 0))
  print
  return {
    'data': [go.Bar(
      x=equipment_nonzero,
      y=bar_year_nonzero,
      orientation='v'
    )],
  }

if __name__ == '__main__':
  #app.run_server(debug=True)
  app.run()
app
