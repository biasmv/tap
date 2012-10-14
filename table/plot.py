"""
Plotting related functionality
"""

from extension import Extension
import typeutil
try:
  import matplotlib.pyplot as plt
  HAS_MATPLOTLIB = True
except ImportError:
  HAS_MATPLOTLIB = False

def make_title(col_name):
  return col_name.replace('_', ' ')

def plot_enrichment(self, score_col, class_col, score_dir='-', 
                    class_dir='-', class_cutoff=2.0,
                    style='-', title=None, x_title=None, y_title=None,
                    clear=True, save=None):
  '''
  Plot an enrichment curve using matplotlib of column *score_col* classified
  according to *class_col*.
  
  For more information about parameters of the enrichment, see
  :meth:`compute_enrichment`, and for plotting see :meth:`Plot`.
  
  :warning: The function depends on *matplotlib*
  '''
  if not HAS_MATPLOTLIB:
    raise ImportError('Matplotlib is required')
  
  enrx, enry = self.compute_enrichment(score_col, class_col, score_dir,
                                      class_dir, class_cutoff)
  
  if not title:
    title = 'Enrichment of %s'%score_col
    
  if not x_title:
    x_title = '% database'
    
  if not y_title:
    y_title = '% positives'
    
  if clear:
    plt.clf()
    
  plt.plot(enrx, enry, style)
  
  plt.title(title, size='x-large', fontweight='bold')     
  plt.ylabel(y_title, size='x-large')
  plt.xlabel(x_title, size='x-large')
  
  if save:
    plt.savefig(save)
  
  return plt
  
def plot(self, x, y=None, z=None, style='.', x_title=None, y_title=None,
         z_title=None, x_range=None, y_range=None, z_range=None,
         color=None, plot_if=None, legend=None,
         num_z_levels=10, z_contour=True, z_interpol='nn', diag_line=False,
         labels=None, max_num_labels=None, title=None, clear=True, save=False,
         **kwargs):
  """
  Function to plot values from your table in 1, 2 or 3 dimensions using
  `Matplotlib <http://matplotlib.sourceforge.net>`__

  :param x: column name for first dimension
  :type x: :class:`str`

  :param y: column name for second dimension
  :type y: :class:`str`

  :param z: column name for third dimension
  :type z: :class:`str`

  :param style: symbol style (e.g. *.*, *-*, *x*, *o*, *+*, *\**). For a
                complete list check (`matplotlib docu <http://matplotlib.sourceforge.net/api/pyplot_api.html#matplotlib.pyplot.plot>`__).
  :type style: :class:`str`

  :param x_title: title for first dimension, if not specified it is
                  automatically derived from column name
  :type x_title: :class:`str`

  :param y_title: title for second dimension, if not specified it is
                  automatically derived from column name
  :type y_title: :class:`str`

  :param z_title: title for third dimension, if not specified it is
                  automatically derived from column name
  :type z_title: :class:`str`

  :param x_range: start and end value for first dimension (e.g. [start_x, end_x])
  :type x_range: :class:`list` of length two

  :param y_range: start and end value for second dimension (e.g. [start_y, end_y])
  :type y_range: :class:`list` of length two

  :param z_range: start and end value for third dimension (e.g. [start_z, end_z])
  :type z_range: :class:`list` of length two

  :param color: color for data (e.g. *b*, *g*, *r*). For a complete list check
                (`matplotlib docu <http://matplotlib.sourceforge.net/api/pyplot_api.html#matplotlib.pyplot.plot>`__).
  :type color: :class:`str`

  :param plot_if: callable which returnes *True* if row should be plotted. Is
                  invoked like ``plot_if(self, row)``
  :type plot_if: callable

  :param legend: legend label for data series
  :type legend: :class:`str`

  :param num_z_levels: number of levels for third dimension
  :type num_z_levels: :class:`int`

  :param diag_line: draw diagonal line
  :type diag_line: :class:`bool`

  :param labels: column name containing labels to put on x-axis for one
                  dimensional plot
  :type labels: :class:`str`

  :param max_num_labels: limit maximum number of labels
  :type max_num_labels: :class:`int`

  :param title: plot title, if not specified it is automatically derived from
                plotted column names
  :type title: :class:`str`

  :param clear: clear old data from plot
  :type clear: :class:`bool`

  :param save: filename for saving plot
  :type save: :class:`str`

  :param z_contour: draw contour lines
  :type z_contour: :class:`bool`

  :param z_interpol: interpolation method for 3-dimensional plot (one of 'nn',
                      'linear')
  :type z_interpol: :class:`str`

  :param \*\*kwargs: additional arguments passed to matplotlib
  
  :returns: the ``matplotlib.pyplot`` module 

  **Examples:** simple plotting functions

  .. code-block:: python

    tab=Table(['a','b','c','d'],'iffi', a=range(5,0,-1),
                                        b=[x/2.0 for x in range(1,6)],
                                        c=[math.cos(x) for x in range(0,5)],
                                        d=range(3,8))

    # one dimensional plot of column 'd' vs. index
    plt=tab.Plot('d')
    plt.show()

    # two dimensional plot of 'a' vs. 'c'
    plt=tab.Plot('a', y='c', style='o-')
    plt.show()

    # three dimensional plot of 'a' vs. 'c' with values 'b'
    plt=tab.Plot('a', y='c', z='b')
    # manually save plot to file
    plt.savefig("plot.png")
  """
  try:
    import matplotlib.pyplot as plt
    import matplotlib.mlab as mlab
    import numpy as np
    idx1 = self.col_index(x)
    xs = []
    ys = []
    zs = []

    if clear:
      plt.figure(figsize=[8, 6])
    
    if x_title!=None:
      nice_x=x_title
    else:
      nice_x=make_title(x)
    
    if y_title!=None:
      nice_y=y_title
    else:
      if y:
        nice_y=make_title(y)
      else:
        nice_y=None
    
    if z_title!=None:
      nice_z = z_title
    else:
      if z:
        nice_z = make_title(z)
      else:
        nice_z = None

    if x_range and (typeutil.is_scalar(x_range) or len(x_range)!=2):
      raise ValueError('parameter x_range must contain exactly two elements')
    if y_range and (typeutil.is_scalar(y_range) or len(y_range)!=2):
      raise ValueError('parameter y_range must contain exactly two elements')
    if z_range and (typeutil.is_scalar(z_range) or len(z_range)!=2):
      raise ValueError('parameter z_range must contain exactly two elements')

    if color:
      kwargs['color']=color
    if legend:
      kwargs['label']=legend
    if y and z:
      idx3 = self.col_index(z)
      idx2 = self.col_index(y)
      for row in self.rows:
        if row[idx1]!=None and row[idx2]!=None and row[idx3]!=None:
          if plot_if and not plot_if(self, row):
            continue
          xs.append(row[idx1])
          ys.append(row[idx2])
          zs.append(row[idx3])
      levels = []
      if z_range:
        z_spacing = (z_range[1] - z_range[0]) / num_z_levels
        l = z_range[0]
      else:
        l = self.min(z)
        z_spacing = (self.max(z) - l) / num_z_levels
      
      for i in range(0,num_z_levels+1):
        levels.append(l)
        l += z_spacing

      xi = np.linspace(min(xs),max(xs),len(xs)*10)
      yi = np.linspace(min(ys),max(ys),len(ys)*10)
      zi = mlab.griddata(xs, ys, zs, xi, yi, interp=z_interpol)

      if z_contour:
        plt.contour(xi,yi,zi,levels,linewidths=0.5,colors='k')

      plt.contourf(xi,yi,zi,levels,cmap=plt.cm.jet)
      plt.colorbar(ticks=levels)
          
    elif y:
      idx2=self.col_index(y)
      for row in self.rows:
        if row[idx1]!=None and row[idx2]!=None:
          if plot_if and not plot_if(self, row):
            continue
          xs.append(row[idx1])
          ys.append(row[idx2])
      plt.plot(xs, ys, style, **kwargs)
      
    else:
      label_vals=[]
      
      if labels:
        label_idx=self.col_index(labels)
      for row in self.rows:
        if row[idx1]!=None:
          if plot_if and not plot_if(self, row):
            continue
          xs.append(row[idx1])
          if labels:
            label_vals.append(row[label_idx])
      plt.plot(xs, style, **kwargs)
      if labels:
        interval = 1
        if max_num_labels:
          if len(label_vals)>max_num_labels:
            interval = int(math.ceil(float(len(label_vals))/max_num_labels))
            label_vals = label_vals[::interval]
        plt.xticks(np.arange(0, len(xs), interval), label_vals, rotation=45,
                    size='x-small')
    
    if title==None:
      if nice_z:
        title = '%s of %s vs. %s' % (nice_z, nice_x, nice_y)
      elif nice_y:
        title = '%s vs. %s' % (nice_x, nice_y)
      else:
        title = nice_x

    plt.title(title, size='x-large', fontweight='bold',
              verticalalignment='bottom')
    
    if legend:
      plt.legend(loc=0)
    
    if x and y:
      plt.xlabel(nice_x, size='x-large')
      if x_range:
        plt.xlim(x_range[0], x_range[1])
      if y_range:
        plt.ylim(y_range[0], y_range[1])
      if diag_line:
        plt.plot(x_range, y_range, '-')
      
      plt.ylabel(nice_y, size='x-large')
    else:
      if y_range:
        plt.ylim(y_range[0], y_range[1])
      if x_title:
        plt.xlabel(x_title, size='x-large')
      plt.ylabel(nice_y, size='x-large')
    if save:
      plt.savefig(save)
    return plt
  except ImportError:
    print "Function needs numpy and matplotlib, but I could not import it."
    raise
  
def plot_histogram(self, col, x_range=None, num_bins=10, normed=False,
                  histtype='stepfilled', align='mid', x_title=None,
                  y_title=None, title=None, clear=True, save=False,
                  color=None, y_range=None):
  """
  Create a histogram of the data in col for the range *x_range*, split into
  *num_bins* bins and plot it using Matplotlib.

  :param col: column name with data
  :type col: :class:`str`

  :param x_range: start and end value for first dimension (e.g. [start_x, end_x])
  :type x_range: :class:`list` of length two

  :param y_range: start and end value for second dimension (e.g. [start_y, end_y])
  :type y_range: :class:`list` of length two

  :param num_bins: number of bins in range
  :type num_bins: :class:`int`

  :param color: Color to be used for the histogram. If not set, color will be 
      determined by matplotlib
  :type color: :class:`str`

  :param normed: normalize histogram
  :type normed: :class:`bool`

  :param histtype: type of histogram (i.e. *bar*, *barstacked*, *step*,
                    *stepfilled*). See (`matplotlib docu <http://matplotlib.sourceforge.net/api/pyplot_api.html#matplotlib.pyplot.hist>`__).
  :type histtype: :class:`str`

  :param align: style of histogram (*left*, *mid*, *right*). See
                (`matplotlib docu <http://matplotlib.sourceforge.net/api/pyplot_api.html#matplotlib.pyplot.hist>`__).
  :type align: :class:`str`

  :param x_title: title for first dimension, if not specified it is
                  automatically derived from column name
  :type x_title: :class:`str`

  :param y_title: title for second dimension, if not specified it is
                  automatically derived from column name
  :type y_title: :class:`str`

  :param title: plot title, if not specified it is automatically derived from
                plotted column names
  :type title: :class:`str`

  :param clear: clear old data from plot
  :type clear: :class:`bool`

  :param save: filename for saving plot
  :type save: :class:`str`

  **Examples:** simple plotting functions

  .. code-block:: python

    tab=Table(['a'],'f', a=[math.cos(x*0.01) for x in range(100)])

    # one dimensional plot of column 'd' vs. index
    plt=tab.plot_histogram('a')
    plt.show()

  """
  try:
    import matplotlib.pyplot as plt
    import numpy as np
    
    if len(self.rows)==0:
      return None
    kwargs={}
    if color:
      kwargs['color']=color
    idx = self.col_index(col)
    data = []
    for r in self.rows:
      if r[idx]!=None:
        data.append(r[idx])
      
    if clear:
      plt.clf()
      
    n, bins, patches = plt.hist(data, bins=num_bins, range=x_range,
                                normed=normed, histtype=histtype, align=align,
                                **kwargs)
    
    if x_title!=None:
      nice_x=x_title
    else:
      nice_x=make_title(col)
    plt.xlabel(nice_x, size='x-large')
    if y_range:
      plt.ylim(y_range) 
    if y_title!=None:
      nice_y=y_title
    else:
      nice_y="bin count"  
    plt.ylabel(nice_y, size='x-large')
    
    if title!=None:
      nice_title=title
    else:
      nice_title="Histogram of %s"%nice_x
    plt.title(nice_title, size='x-large', fontweight='bold')
    
    if save:
      plt.savefig(save)
    return plt
  except ImportError:
    print "Function needs numpy and matplotlib, but I could not import it."
    raise

def plot_bar(self, cols, x_labels=None, x_labels_rotation='horizontal', y_title=None, title=None, 
            colors=None, yerr_cols=None, width=0.8, bottom=0, 
            legend=True, save=False):

  """
  Create a barplot of the data in cols. Every element of a column will be represented
  as a single bar. If there are several columns, each row will be grouped together.

  :param cols: Column names with data. If cols is a string, every element of that column
                will be represented as a single bar. If cols is a list, every row resulting
                of these columns will be grouped together. Every value of the table still
                is represented by a single bar.

  :param x_labels: Label for every row on x-axis.
  :type x_labels: :class:`list`
  
  :param x_labels_rotation: Can either be 'horizontal', 'vertical' or a number that 
                            describes the rotation in degrees.

  :param y_title: Y-axis description
  :type y_title: :class:`str`

  :title: Title
  :type title: :class:`str`

  :param colors: Colors of the different bars in each group. Must be a list of valid
                  colornames in matplotlib. Length of color and cols must be consistent.
  :type colors: :class:`list`

  :param yerr_cols: Columns containing the y-error information. Can either be a string
                    if only one column is plotted or a list otherwise. Length of
                    yerr_cols and cols must be consistent.

  :param width: The available space for the groups on the x-axis is divided by the exact
                number of groups. The parameters width is the fraction of what is actually
                used. If it would be 1.0 the bars of the different groups would touch each other.
  :type width: :class:`float`

  :param bottom: Bottom
  :type bottom: :class:`float`

  :param legend: Legend for color explanation, the corresponding column respectively.
  :type legend: :class:`bool`

  :param save: If set, a png image with name $save in the current working directory will be saved.
  :type save: :class:`str`

  """
  try:
    import numpy as np
    import matplotlib.pyplot as plt
  except:
    raise ImportError('plot_bar relies on numpy and matplotlib, but I could not import it!')
  
  if len(cols)>7:
    raise ValueError('More than seven bars at one position looks rather meaningless...')
    
  standard_colors=['b','g','y','c','m','r','k']
  data=[]
  yerr_data=[]

  if not isinstance(cols, list):
    cols=[cols]
    
  if yerr_cols:
    if not isinstance(yerr_cols, list):
      yerr_cols=[yerr_cols]
    if len(yerr_cols)!=len(cols):
      raise RuntimeError ('Number of cols and number of error columns must be consistent!')
    
  for c in cols:
    cid=self.col_index(c)
    temp=list()
    for r in self.rows:
      temp.append(r[cid])
    data.append(temp)  
    
  if yerr_cols:
    for c in yerr_cols:
      cid=self.col_index(c)
      temp=list()
      for r in self.rows:
        temp.append(r[cid])
      yerr_data.append(temp)
  else:
    for i in range(len(cols)):
      yerr_data.append(None)

  if not colors:
    colors=standard_colors[:len(cols)]

  if len(cols)!=len(colors):
    raise RuntimeError("Number of columns and number of colors must be consistent!")

  ind=np.arange(len(data[0]))
  single_bar_width=float(width)/len(data)
  
  fig=plt.figure()
  ax=fig.add_subplot(111)
  legend_data=[]
  for i in range(len(data)):
    legend_data.append(ax.bar(ind+i*single_bar_width,data[i],single_bar_width,bottom=bottom,color=colors[i],yerr=yerr_data[i], ecolor='black')[0])
    
  if title!=None:
    nice_title=title
  else:
    nice_title="coolest barplot on earth"
  ax.set_title(nice_title, size='x-large', fontweight='bold')  
  
  if y_title!=None:
    nice_y=y_title
  else:
    nice_y="score" 
  ax.set_ylabel(nice_y)
  
  if x_labels:
    if len(data[0])!=len(x_labels):
      raise ValueError('Number of xlabels is not consistent with number of rows!')
  else:
    x_labels=list()
    for i in range(1,len(data[0])+1):
      x_labels.append('Row '+str(i))
    
  ax.set_xticks(ind+width*0.5)
  ax.set_xticklabels(x_labels, rotation = x_labels_rotation)
    
  if legend:
    ax.legend(legend_data, cols)   
    
  if save:
    plt.savefig(save)
  
  return plt
    
def plot_hexbin(self, x, y, title=None, x_title=None, y_title=None, x_range=None, y_range=None, binning='log',
                colormap='jet', show_scalebar=False, scalebar_label=None, clear=True, save=False, show=False):

  """
  Create a heatplot of the data in col x vs the data in col y using matplotlib

  :param x: column name with x data
  :type x: :class:`str`

  :param y: column name with y data
  :type y: :class:`str`

  :param title: title of the plot, will be generated automatically if set to None
  :type title: :class:`str`

  :param x_title: label of x-axis, will be generated automatically if set to None
  :type title: :class:`str`

  :param y_title: label of y-axis, will be generated automatically if set to None
  :type title: :class:`str`

  :param x_range: start and end value for first dimension (e.g. [start_x, end_x])
  :type x_range: :class:`list` of length two

  :param y_range: start and end value for second dimension (e.g. [start_y, end_y])
  :type y_range: :class:`list` of length two

  :param binning: type of binning. If set to None, the value of a hexbin will
                  correspond to the number of datapoints falling into it. If
                  set to 'log', the value will be the log with base 10 of the above
                  value (log(i+1)). If an integer is provided, the number of a 
                  hexbin is equal the number of datapoints falling into it divided 
                  by the integer. If a list of values is provided, these values
                  will be the lower bounds of the bins.
  
  :param colormap: colormap, that will be used. Value can be every colormap defined
                    in matplotlib or an own defined colormap. You can either pass a
                    string with the name of the matplotlib colormap or a colormap
                    object.

  :param show_scalebar: If set to True, a scalebar according to the chosen colormap is shown
  :type show_scalebar: :class:`bool`

  :param scalebar_label: Label of the scalebar
  :type scalebar_label: :class:`str`

  :param clear: clear old data from plot
  :type clear: :class:`bool`

  :param save: filename for saving plot
  :type save: :class:`str`

  :param show: directly show plot
  :type show: :class:`bool`
  
  """

  try:
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
  except:
    raise ImportError('plot_hexbin relies on matplotlib, but I could not import it')

  idx=self.col_index(x)
  idy=self.col_index(y)
  xdata=[]
  ydata=[]

  for r in self.rows:
    if r[idx]!=None and r[idy]!=None:
      xdata.append(r[idx])
      ydata.append(r[idy])

  if clear:
    plt.clf()
    
  if x_title!=None:
    nice_x=x_title
  else:
    nice_x=make_title(x)
    
  if y_title!=None:
    nice_y=y_title
  else:
    nice_y=make_title(y)

  if title==None:
    title = '%s vs. %s' % (nice_x, nice_y)

  if typeutil.is_string_like(colormap):
    colormap=getattr(cm, colormap)

  if x_range and (typeutil.is_scalar(x_range) or len(x_range)!=2):
    raise ValueError('parameter x_range must contain exactly two elements')
  if y_range and (typeutil.is_scalar(y_range) or len(y_range)!=2):
    raise ValueError('parameter y_range must contain exactly two elements')
  if x_range:
    plt.xlim((x_range[0], x_range[1]))
  if y_range:
    plt.ylim(y_range[0], y_range[1])
  extent = None
  if x_range and y_range:
    extent = [x_range[0], x_range[1], y_range[0], y_range[1]]
  plt.hexbin(xdata, ydata, bins=binning, cmap=colormap, extent=extent)

  plt.title(title, size='x-large', fontweight='bold',
            verticalalignment='bottom')

  plt.xlabel(nice_x)
  plt.ylabel(nice_y)
      
  if show_scalebar:
    cb=plt.colorbar()
    if scalebar_label:
      cb.set_label(scalebar_label)

  if save:
    plt.savefig(save)

  if show:
    plt.show()

  return plt

EXT = Extension('plotting', plot_enrichment,
                plot, plot_histogram, plot_bar, plot_hexbin)
