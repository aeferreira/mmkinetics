from __future__ import print_function
from scipy.optimize import curve_fit
from scipy import stats
import numpy as np

class Kin_results(object):
    """Object that holds data from a computation, supporting dot access.
       
       Mandatory data set is:
       
       name - Name of the method used.
       error - None by default, str describing error in computation
       V - limiting rate
       Km - Michaelis constant
       S - sum of squares of residuals to the Michelis-Menten equation

       v_hat - estimated rate values (iterable of floats)
       
       Optional for linearizations:
       x - x-values of linearization (iterable of floats)
       y - y-values of linearization (iterable of floats)

       Optional, depending on the method:
       SD_V - standard error of the limiting rate
       SD_Km - standard error of the Michelis constant"""
    
    def __init__(self, name):
        self.name = name
        self.error = None
        self.V = 0.0
        self.Km = 0.0
        self.S = 0.0
        self.v_hat = None

# some util function
def lists2arrays(x, y):
    return (np.array(x), np.array(y))

def menten(a, V, Km):
    return V * a / (Km + a)

def hanes_woolf(v0, a):
    x = a
    y = a/v0
    slope, intercept, r_value, p_value, std_error = stats.linregress(x, y)
    
    r = Kin_results('Hanes or Woolf')
    r.x = x
    r.y = y
    r.V = 1.0/slope
    r.Km = intercept * r.V
    r.Sm_lin = std_error
    return r
    
def eadie_hofstee(v0, a):
    x = v0/a
    y = v0
    slope, intercept, r_value, p_value, std_error = stats.linregress(x, y)
    Km = -slope
    V = intercept

    r = Kin_results('Eadie-Hofstee')
    r.x = x
    r.y = y
    r.V = intercept
    r.Km = -slope
    r.Sm_lin = std_error
    return r
    
def lineweaver_burk(v0, a):
    x = 1.0/a
    y = 1.0/v0
    slope, intercept, r_value, p_value, std_error = stats.linregress(x, y)
    xy = zip(x,y)

    r = Kin_results('Lineweaver-Burk')
    r.x = x
    r.y = y
    r.V = 1.0/intercept
    r.Km = slope * r.V
    r.Sm_lin = std_error
    return r

def hyperbolic(v0, a):

    estimated_V = max(v0)
    estimated_Km = 1
    for v in v0:
        if v < estimated_V / 2.0:
            estimated_Km = v
            break
    initial_guess = [estimated_V, estimated_Km]
    
    popt, pcov = curve_fit(menten, a, v0, p0=initial_guess)
    errors = np.sqrt(np.diag(pcov))
    r = Kin_results('Hyperbolic regression')
    r.x = a
    r.y = v0
    r.V = popt[0]
    r.Km = popt[1]
    r.SV = errors[0]
    r.SKm = errors[1]
    return r

def cornish_bowden(v0, a):

    cornish_bowden = []
    straights      = []
    intersects     = []

    for v, s in zip(v0, a):
        m = v / s
        b = v
        straights.append([m,b])

    n = len(straights)
    for i in range(0,n-1):
        for j in range(i+1, n):
            x = ( straights[j][1] - straights[i][1] ) / ( straights[i][0] - straights[j][0] )
            y = ( straights[i][1]*straights[j][0] - straights[j][1]*straights[i][0] ) / ( straights[j][0] - straights[i][0] )
            intersects.append([x,y])

    intersects_x = [i[0] for i in intersects]
    intersects_y = [i[1] for i in intersects]
    r = Kin_results('Cornish-Bowden')
    r.x = a
    r.y = v0
    r.V = np.median(intersects_y)
    r.Km = np.median(intersects_x)
    r.CI_V = (0,0)
    r.CI_Km = (0,0)
    #TODO: compute CIs: it was over estimated. Leave it at zero, for now.
    return r
