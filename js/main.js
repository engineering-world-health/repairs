
function gen_dropdown(select,id,list){
  droplist = Array.from(Object.create(list))
  droplist.unshift(all)
  var options = select.selectAll('option').data(droplist).enter()
    .append('option').text(function(d){return d;});
  return select;
}

function gen_checkbox(parent,data){
  var wrap = parent.append('div').attr('float','left').attr('class','checkwrap');
  wrap.append('input').attr('type','checkbox')
    .attr('id','checkbox-'+data['col']).property('checked',Boolean(data['checked']));
  wrap.append('span').html(data['name']);
}

function gen_piechart(parent,names,values){
  parent.style('height','100%').style('max-width','300px')
  var r = 100;
  var svg  = parent.append('svg').attr('width','100%')
    .attr('viewBox','0 0 '+r*2+' '+(r*2))
    .attr('preserveAspectRatio','xMinYMin');
  var g    = svg.append('g').attr('transform','translate('+r+','+r+')');
  var pie  = d3.pie().sort(null).value(function(d){return d;}).padAngle(0.02);
  var path = d3.arc().outerRadius(r).innerRadius(r*0.7);
  var arc  = g.selectAll('.arc').data(pie(values)).enter()
    .append('g').attr('class','arc');
  arc.append('path')
    .attr('d',path).attr('fill',function(d,i){return meta['colors'][i];})
  var leg  = parent.append('div');
  var keys = leg.selectAll('legi').data(names).enter()
    .append('legi')
    .style('background',function(d,i){return meta['colors'][i]})
    .append('legl').text(function(d){return d;})
}

function gen_bar(parent,names,values){
  dy = 10;
  gy = 2;
  ox = 180;
  hy = names.length*(dy+gy)
  ht = hy+dy+(2*dy)
  wd = parent.node().getBoundingClientRect().width-ox;
  barnames = names.map(n => n.replace(/\s*\(.*?\)\s*/g,'x'))
  parent.style('height',ht.toString()).style('width','100%')
  var x = d3.scaleLinear().range([0,wd]).domain([0,d3.max(values)])
  var y = d3.scalePoint().range([hy,0]).domain(barnames.reverse())
  var svg = parent.append('svg').attr('width','100%').attr('height',ht)
  var grid = svg.append('g').attr('class','grid')
    .call(d3.axisBottom(x).tickSize(-ht-gy))
    .attr('transform','translate('+ox+','+(ht-2*dy+gy)+')');
  var bars = svg.append('g').selectAll('.bar').data(values.reverse()).enter()//
  bars.append('rect').attr('class','bar').style('fill',meta['colors'][0])
    .attr('y',function(d,i){return y(barnames[i]);}).attr('x',ox)
    .attr('height',dy).attr('width',function(d){return x(d);})
  var labs = svg.append('g').call(d3.axisLeft().scale(y))
    .attr('transform','translate('+ox+','+dy/2+')');
}

function gen_table(parent,cols,data){
  parent.style('height','100%').style('display','table')
  var table = parent.append('table').attr('class','tablesorter');
  var thead = table.append('thead');
  var tbody = table.append('tbody');
  thead.append('tr').selectAll('th').data(cols.map(x => x.name)).enter()
    .append('th').text(function(c){return c;});
  tbody.selectAll('tr').data(data).enter()
    .append('tr').selectAll('td').data(function(r){return d3.values(r);}).enter()
    .append('td').text(function(d) {return d;});
  $(document).ready(function(){$(".tablesorter").tablesorter()});
}

function get_checkboxes(){
  for (t in meta['table']){
    meta['table'][t]['checked'] = d3.select('#checkbox-'+meta['table'][t]['col'])
    .property('checked');
  }
}

function get_cols(cols,data){
  coldata = []
  for (d in data){coldata.push(cols.reduce((o,k)=>{o[k]=data[d][k];return o;},{}));}
  return coldata;
}

function get_col(col,data){
  coldata = []
  for (d in data){coldata.push(data[d][col]);}
  return coldata;
}

function count_match(labels,data){
  counts = [...Array(labels.length)]
  for (l in labels){ counts[l] = data.filter(d => d === labels[l]).length }
  return counts
}

function filter_repairs(repairs){
  year      = select['year'].node().value
  country   = select['country'].node().value
  equipment = select['equipment'].node().value
  var filtered = repairs.filter(function(r){
    return Boolean(
    (year      == all || year      == r.year) &&
    (country   == all || country   == r.country) &&
    (equipment == all || equipment == r.equipment));
  });
  return filtered;
}

function loading(toggle){
  if (toggle) {
    superdivs['render'].style('display','none');
    superdivs['loading'].style('display','block');
    superdivs['spinner']['spinner'] = new Spinner({
      lines: 12,length:12, radius:18, position:'relative',color:meta['colors'][0]})
      .spin(document.getElementById('spinner'))
  } else {
    superdivs['loading'].style('display','none');
    superdivs['render'].style('display','block');
    superdivs['spinner']['spinner'].stop()
  }
}

function gen_dropdowns(){
  keys =  ['year','country','equipment']
  for (k in keys){
    gen_dropdown(select[keys[k]],'select-'+keys[k],meta[keys[k]])
  }
}

function gen_checkboxes(){
  for (c in meta['table']){
    gen_checkbox(d3.select('#checkbox-table'),meta['table'][c])
  }
}

function init(metajson){
  meta = metajson;
  loading(true)
  gen_dropdowns();
  gen_checkboxes();
}

function render(repairsjson){
  // init
  loading(false)
  get_checkboxes()
  for (d in div){ div[d].html(''); };
  // filter repairs
  filtered = filter_repairs(repairsjson);
  d3.select('#num-matches').html(filtered.length)
  // table
  tcols = meta['table'].filter((t)=>{return t.checked;})
  rcols = get_cols(get_col('col',tcols),filtered)
  gen_table(div['table'],tcols,rcols)
  // bar chart
  if (select['equipment'].node().value == all) {
    div['equipment'].style('display','block')
    gen_bar(div['equipment'],meta['equipment'],count_match(meta['equipment'],filtered.map(f => f.equipment)));
  } else {
    div['equipment'].style('display','none');
  }
  // pie charts
  gen_piechart(div['result'],meta['result'],count_match(meta['result'],get_col('result',filtered)))
  gen_piechart(div['fix'],   meta['fix'],   count_match(meta['fix'],   get_col('fix',filtered)))
}

// -----------------------------------------------------------------------------
// MAIN
// -----------------------------------------------------------------------------
var div = {
  table:     d3.select('#repair-table'),
  result:    d3.select('#repair-result'),
  equipment: d3.select('#repair-equipment'),
  fix:       d3.select('#repair-fix')
};
var select = {
  year:      d3.select('#select-year'),
  country:   d3.select('#select-country'),
  equipment: d3.select('#select-equipment'),
}
var superdivs = {
  loading: d3.select('#loading'),
  spinner: d3.select('#spinner'),
  render:  d3.select('#render')
}
var all = 'All';
var meta;
var repairs;

d3.json('db/meta.json',init);
d3.json('db/cnx.php',function(e,repairs){
  render(repairs);
  window.addEventListener('resize',      function(){render(repairs);});
  $('#filters') .on('change',            function(){render(repairs);});
  $('#checkbox-table input').on('change',function(){render(repairs);});
});
