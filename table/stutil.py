import math

def mean(xs):
  """
  Calculate mean of dataset
  """
  if len(xs)==0:
    raise RuntimeError("Can't calculate mean of empty sequence")
  return float(sum(xs))/len(xs)

def median(xs):
  """
  Calculate median of dataset
  """
  if len(xs)==0:
    raise RuntimeError("Can't calculate median of empty sequence")
  sorted_xs=sorted(xs)
  if (len(xs) % 2)==0:
    return (sorted_xs[(len(xs)-1)/2]+sorted_xs[(len(xs)-1)/2+1])/2.0
  else:
    return sorted_xs[(len(xs)-1)/2]

def std_dev(xs):
  """
  Calculate standard-deviation of dataset
  
            | sum[xi-<x>]^2 |
  sigma=sqrt|---------------|
            |       n       |
  """
  mean_val=mean(xs)
  return math.sqrt(sum([(x-mean_val)**2 for x in xs])/len(xs))

def correl(xs, ys):
  """
  Calculates the correlation coefficient between xs and ys as
  
    sum[(xi-<x>)*(yi-<y>)]
  r=----------------------
          sx*sy
          
  where <x>, <y> are the mean of dataset xs and ys, and, sx and sy are the 
  standard deviations.
  """
  if len(xs)!=len(ys):
    raise RuntimeError("Can't calculate correl. Sequence lengths do not match.")
  if len(xs)==1:
    raise RuntimeError("Can't calculate correl of sequences with length 1.")
  mean_x=mean(xs)
  mean_y=mean(ys)
  sigma_x, sigma_y=(0.0, 0.0)
  cross_term=0.0
  for x, y in zip(xs, ys):
    cross_term+=(x-mean_x)*(y-mean_y)
    sigma_x+=(x-mean_x)**2
    sigma_y+=(y-mean_y)**2
  sigma_x=math.sqrt(sigma_x)
  sigma_y=math.sqrt(sigma_y)
  return cross_term/(sigma_x*sigma_y)

def Histogram(xs, bounds, num_bins):
  bins=[0 for i in range(num_bins)]
  d=1.0*num_bins/(bounds[1]-bounds[0])
  for x in xs:
    index=int((x-bounds[0])*d)
    if index>num_bins-1 or index<0:
      continue
    bins[index]+=1
  return bins
