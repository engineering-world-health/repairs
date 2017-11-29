import dash
import dash_core_components as dcc
import dash_html_components as html
from database import *
from config import *
from utils import *



@app.callback(
  dash.dependencies.Output('pie-result'),
  #dash.dependencies.Input('')
)
def update_pie():
  return {
    'data': [go.Pie(
      labels=['1','2','3'],
      values=[1,2,3]
    )]
}

def make_dash(repairs):
  # EQUIPMENTS = csv_LUT(lut['equipment'])
  RESUlTS = csv_LUT(lut['result'])
  YEARS = ['2016','2017']

  # repairs_year = {}
  # n_equipment_year = []
  # for year in YEARS:
  #   repairs_year.update({year:filter_obj_list_by_attr(repairs,'year',[int(year)])})
  #   n_equipment_year

  n_result = count_obj_list_by_attr(repairs,'result',RESUlTS)

  app = dash.Dash()
  app.layout = html.Div([
    html.H1(['EWH Repair Database']),
    html.Div([
      dcc.Dropdown(
        id='pie-result-year',
        options=[{'label': year, 'value': year} for year in YEARS],
      )
    ]),
    dcc.Graph(
      id='pie-result'
    ),
  ])
  return app

if __name__ == '__main__':
  forms = get_all_work_summary_forms(wsf['root'])
  repairs = get_attr_from_obj_list(forms,'repairs',merge=True)
  app = make_dash(repairs)
  app.run_server(debug=True)


def get_sub_attr_from_obj_list(objList,subName,attrName,merge=False):
  attr = []
  for obj in objList:
    if merge:
      attr += getattr(getattr(obj,subName),attrName)
    else:
      attr.append(getattr(getattr(obj,subName),attrName))
  return attr

class Equipment:
  def __init__(self,etype=None,oem=None,model=None,sn=None):
    self.type  = etype
    self.oem   = oem
    self.model = model
    self.sn    = sn
  def dir(self):
    return ['type','oem','model','sn']
  def __str__(self):
    return print_obj(self)
  def __repr__(self):
    return self.type

equip = Equipment(etype = etype,
                  oem   = oem,
                  model = model,
                  sn    = sn)

class Hospital:
  def __init__(self,name=None,country=None):
    self.name    = name
    self.country = country
  def dir(self):
    return ['name','country']
  def __str__(self):
    return printObj(self)

def makeRepairsCSV(repairs):
  def makeRow(repair):
    return {'year'          :repair.year,
            'country'       :repair.country,
            'hospital'      :repair.hospital,
            'engineers'     :repair.engineers,
            'equipment type':repair.equipment.type,
            'manufacturer'  :repair.equipment.oem,
            'model'         :repair.equipment.model,
            'serial number' :repair.equipment.sn,
            'repair type'   :repair.type,
            'result'        :repair.result}
  header = makeRow(Repair()).keys()
  with open(wsf['output'],'w') as csvfile:
    csvwriter = csv.DictWriter(csvfile,fieldnames=header,quoting=csv.QUOTE_ALL)
    csvwriter.writeheader()
    for repair in repairs:
      csvwriter.writerow(makeRow(repair))


import plotly.plotly as py
import plotly.graph_objs as go
import ipywidgets as widgets

from plotly.widgets import GraphWidget as graphwidget
from config import *
from utils import *
#
# def repaired_pie(repairs):
#   results = get_attr_from_obj_list(repairs,'result')
#   labels = csv_LUT(lut['result'])
#   values = []
#   for label in labels:
#     values.append(sum([result == label for result in results]))
#   return go.Pie(values=values,labels=labels)
#
# def attr_year_bar(repairs,attrName):
#   attrs    = get_attr_from_obj_list(repairs,attrName)
#   years    = get_attr_from_obj_list(repairs,'year')
#   attrList = csv_LUT(lut[attrName])
#   data     = []
#   for (i,iyear) in enumerate(list(set(years))):
#     values = []
#     for (j,jattr) in enumerate(attrList):
#       values.append(sum([(attr == jattr) and (year == iyear)\
#                          for (attr,year) in zip(attrs,years)]))
#     data.append(go.Bar(x=attrList,y=values,name=str(iyear)))
#   layout = go.Layout(barmode='stack')
#   return (data,layout)

def make_plotly(repairs):
  w_year = widgets.Dropdown(
    options = ['1','2','3'],
    value = 0,
    description = 'Number: ',
    disabled = False
  )
  gw = graphwidget('https://plot.ly/dashboard/jessexknight:8/')


  # (data,layout) = attr_year_bar(repairs,'equipment')
  # (data,layout) = attr_year_bar(repairs,'type')
  # (data,layout) = repaired_pie(repairs)
  # fig = go.Figure(data=data,layout=layout)
  # py.iplot(fig,filename='EWH-repair-database')
