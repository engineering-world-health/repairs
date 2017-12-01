import dash_core_components as dcc
import dash_html_components as html
import csv

def get_attr_from_obj_list(objList,attrName,merge=False):
  attr = []
  for obj in objList:
    if merge:
      attr += getattr(obj,attrName)
    else:
      attr.append(getattr(obj,attrName))
  return attr

def filter_obj_list_by_attr(objList,attrName,attrValues,asType=None):
  if asType is None:
    asType = type(attrValues[0])
  objFilterList = []
  for attrValue in attrValues:
    objAttrList = []
    if attrValue in [None,'*','All','all']:
      objAttrList = objList
    else:
      for obj in objList:
        if asType(getattr(obj,attrName)) == attrValue:
          objAttrList.append(obj)
    objFilterList.append(objAttrList)
  return objFilterList

def filter_obj_list_multi(objList,attrDict,asType=str):
  for attrName,attrValue in attrDict.iteritems():
    objList = filter_obj_list_by_attr(objList,attrName,[attrValue],asType=asType)[0]
  return objList

def count_obj_list_by_attr(objList,attrName,attrValues,asType=None):
  if asType is None:
    asType = type(attrValues[0])
  count = []
  for attrValue in attrValues:
    attrCount = 0
    if attrValue in [None,'*','All','all']:
      attrCount = len(objList)
    else:
      for obj in objList:
        if asType(getattr(obj,attrName)) == attrValue:
          attrCount += 1
    count.append(attrCount)
  return count

def csv_LUT(lutname):
  with open(lutname,'r') as csvfile:
    return [row[0] for row in csv.reader(csvfile)]

def print_obj(obj,sub=False):
  def xstr(s):
    if s is None:
      return '\n'
    elif isinstance(s,list) and isinstance(s[0],Repair):
      return str(len(s))+'\n'
    elif hasattr(s,'dir'):
      return print_obj(s,sub=True)
    else:
      return str(s)+'\n'
  if not sub:
    sx = ['[\n','  ',']']
  else:
    sx = ['\n','    ','']
  odir = obj.dir()
  s = sx[0]
  for attr in odir:
    s += sx[1]+attr+': '+xstr(getattr(obj,attr))
  s += sx[2]
  return s
