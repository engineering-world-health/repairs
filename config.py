import os

lut = {}
lut['year']      = os.path.join('static','year.csv')
lut['fix']       = os.path.join('static','fix.csv')
lut['result']    = os.path.join('static','result.csv')
lut['country']   = os.path.join('static','country.csv')
lut['equipment'] = os.path.join('static','equipment.csv')
lut['table']     = os.path.join('static','table.csv')
wsf = {}
wsf['root']   = os.path.join('data')
wsf['output'] = os.path.join('data','database.csv')
idx = {}
idx['date']      = [ 5, 2] # C6
idx['country']   = [ 6, 2] # C7
idx['engineers'] = [ 5,10] # K6
idx['hospital']  = [ 6,10] # K7
idx['equip'] = {}
idx['equip']['type']  =  1 # B*
idx['equip']['oem']   =  2 # C*
idx['equip']['model'] =  3 # D*
idx['equip']['sn']    =  4 # E*
idx['equip']['0']     =  9 # *10
idx['repair'] = {}
idx['repair']['type']   = [5,6,7,8,9,10,11] # FGHIJKL*
idx['repair']['notes']  = 12      # M*
idx['repair']['result'] = [13,14] # NO*
