import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from ewhdata import *
from config import *
from utils import *

# Initializations & Data -------------------------------------------------------
app = dash.Dash(__name__)
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
#repairs_year = filter_obj_list_by_attr(repairs,'year',LUTA['year'],asType=str)
#repairs_equip = filter_obj_list_by_attr(repairs,'equipment',LUTA['equipment'],asType=str)

# Layout Functions -------------------------------------------------------------

def make_dropdown(lutName,dropdownID,width=200):
  return html.Div([
    html.Div([lutName.title()+':'],style={'padding':'10px 10px 5px 10px'}),
    dcc.Dropdown(
      id=dropdownID,
      options=[{'label': [item], 'value': i} for (i,item) in enumerate(LUTA[lutName])],
      value=0)
    ],
    style={'width':str(width)+'px',
           'display':'inline-block',
           'margin':'0px 0px 0px 0px'})

def make_pie(labels,values):
  return {
    'data': [go.Pie(
      labels=labels,
      values=values
    )],
    'layout': go.Layout(
      width=400,
      height=300,
      margin=go.Margin(l=50, r=50, b=50, t=50, pad=0)
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

# Layout -----------------------------------------------------------------------

app.layout = html.Div([
  html.H1(['EWH Repair Database']),
  html.Div([
      html.H3(['Repair Outcome']),
      make_dropdown('year','select-year-pie-result',width=200),
      make_dropdown('country','select-country-pie-result',width=200),
      make_dropdown('equipment','select-equip-pie-result',width=400),
      dcc.Graph(id='pie-result')
    ], style={'width':'49%','display': 'inline-block'}
  ),
  html.Div([
      html.H3(['Repair Type']),
      make_dropdown('year','select-year-pie-fix',width=200),
      make_dropdown('country','select-country-pie-fix',width=200),
      make_dropdown('equipment','select-equip-pie-fix',width=400),
      dcc.Graph(id='pie-fix')
    ], style={'width':'49%','display': 'inline-block'}
  ),
  html.Div([
      html.H3(['Equipment Type']),
      make_dropdown('year','select-year-bar-equipment',width=200),
      make_dropdown('country','select-country-bar-equipment',width=200),
      dcc.Graph(id='bar-equipment')
    ], style={'width':'98%','display': 'inline-block'}
  ),
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

if __name__ == '__main__':
  app.run_server(debug=True)
  #app.run()
