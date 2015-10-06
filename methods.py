from __future__ import print_function
from scipy.optimize import curve_fit
from scipy import stats
import numpy as np

class kin_results(object):
    """Object that holds data from a computation, supporting dot access.
       
       Mandatory data set is:

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
    
    def __init__(self):
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

# TODO: discuss the need for these early application of round on the regression
def Hanes(v0, a):
    x = a
    y = a/v0
    slope, intercept, r_value, p_value, std_error = stats.linregress(x, y)
    xy = zip(x,y)
    V = 1.0/slope
    Km = intercept * V

    # Vmax, Km, error, lin_reg, points
    return (round(V, 6), round(Km,6), round(std_error,6), xy)

def Hofstee(v0, a):
    x = v0/a
    y = v0
    slope, intercept, r_value, p_value, std_error = stats.linregress(x, y)
    xy = zip(x,y)
    Km = -slope
    V = intercept

    # Vmax, Km, error, lin_reg, points
    return (round(V, 6), round(Km,6), round(std_error,6), xy)
    
def Burk(v0, a):
    x = 1.0/a
    y = 1.0/v0
    slope, intercept, r_value, p_value, std_error = stats.linregress(x, y)
    xy = zip(x,y)
    V = 1.0/intercept
    Km = slope * V

    # Vmax, Km, error, lin_reg, points
    return (round(V, 6), round(Km,6), round(std_error,6), xy)

def Hyp_Reg(v0, a):

    estimated_V = max(v0)
    estimated_Km = 1
    for v in v0:
        if v < estimated_V / 2.0:
            estimated_Km = v
            break
    initial_guess = [estimated_V, estimated_Km]
    
    popt, pcov = curve_fit(menten, a, v0, p0=initial_guess)
    errors = np.sqrt(np.diag(pcov))
    V = popt[0]
    Km = popt[1]
    SV = errors[0]
    SKm = errors[1]
    
    xy = zip(a,v0)
        
    # Vmax, Km, error(Vmax,Km), hyp_reg
    return (str(round(V, 6)), str(round(Km, 6)), str(round(SV, 6)), str(round(Km, 6)), xy)


def Cornish_Bowden(v0, a):

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

    # Vmax, Km, error interval Vmax, error interval Km, straights
    return [round(np.median(intersects_y),6), round(np.median(intersects_x),6), str(round(min(intersects_y),6))+';'+str(round(max(intersects_y),6)),str(round(min(intersects_x),6))+';'+str(round(max(intersects_x),6)),straights]
