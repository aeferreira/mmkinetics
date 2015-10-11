from __future__ import print_function
import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import linregress as lreg
import matplotlib.pyplot as pl

"""Methods to determine Michaelis-Menten equation parameters and statistics.

   Wilkinson [TODO: insert reference] data is used to test the methods."""

class Kin_results(object):
    """Object that holds data from a computation, supporting dot access.
       
       Mandatory members are:
       
       name - Name of the method used (str).
       error - None by default, str describing error in computation
       V - limiting rate (float)
       Km - Michaelis constant (float)
       SS - sum of squares of residuals to the Michelis-Menten equation (float)

       v_hat - estimated rate values (iterable of floats)
       
       Optional, depending on the method:
       SE_V - standard error of the limiting rate
       SE_Km - standard error of the Michelis constant
       
       Optional for linearizations:
       x - x-values during linearization (iterable of floats)
       y - y-values during linearization (iterable of floats)"""

    def __init__(self, name):
        self.name = name
        self.error = None
        self.V = 0.0
        self.Km = 0.0
        self.SS = 0.0
        self.v_hat = None

#------------ util functions --------------------------

def lists2arrays(x, y):
    return (np.array(x), np.array(y))

def lin_regression(x, y):
    """Simple linear regression (y = m * x + b + error)."""
    m, b, R, p, SEm = lreg(x, y)
    
    # need to compute SEb, linregress only computes SEm
    n = len(x)
    SSx = np.var(x,ddof=1) * (n-1) # this is sum( (x - mean(x))**2 )
    SEb2 = SEm**2 * (SSx/n + np.mean(x)**2)
    SEb = SEb2**0.5
    
    return m, b, SEm, SEb, R, p

def MM(a, V, Km):
    return V * a / (Km + a)


def MM_line(V, Km, xmax=1.0):
    x0 = 0
    x = np.linspace(x0, xmax, 100)
    return x, MM(x, V, Km)


def res_tuple(method, V, Km, SV=None, SKm=None):
    sV = "{:6.4f}".format(V)
    sKm = "{:6.4f}".format(Km)
    if SV is None:
        sSV = 'n/a'
    else:
        sSV = "{:6.4f}".format(SV)
    if SKm is None:
        sSKm = 'n/a'
    else:
        sSKm = "{:6.4f}".format(SKm)
    return method, sV, sSV, sKm, sSKm

def res_object(method, V, Km, SE_V=None, SE_Km=None, error=None, x=None, y=None):
    r = Kin_results(method)
    r.V = V
    r.Km = Km
    r.SE_V = SE_V
    r.SE_Km = SE_Km
    r.error = error
    r.x = x
    r.y = y
    return r

#------------ methods --------------------------
# all methods accept numpy arrays as input

def lineweaver_burk(a, v0):
    while 0 in a:
        index = np.where(a==0)
        a = np.delete(a,index)
        v0 = np.delete(v0,index)
    while 0 in v0:
        index = np.where(v0==0)
        a = np.delete(a,index)
        v0 = np.delete(v0,index)
    x, y = 1/a, 1/v0
    m, b, Sm, Sb, R, p = lin_regression(x, y)
    V = 1.0 / b
    Km = m / b
    SV = V * Sb / b
    SKm = Km * np.sqrt((Sm/m)**2 + (Sb/b)**2)
    return res_object('Lineweaver-Burk', V, Km, SE_V=SV, SE_Km=SKm, x=x, y=y)

def hanes_woolf(a, v0):
    while 0 in a:
        index = np.where(a==0)
        a = np.delete(a,index)
        v0 = np.delete(v0,index)
    while 0 in v0:
        index = np.where(v0==0)
        a = np.delete(a,index)
        v0 = np.delete(v0,index)
    x = a
    y = a/v0
    m, b, Sm, Sb, R, p = lin_regression(x, y)
    V = 1.0 / m
    Km = b / m
    SV = V * Sm / m
    SKm = Km * np.sqrt((Sm/m)**2 + (Sb/b)**2)
    return res_object('Hanes or Woolf', V, Km, SE_V=SV, SE_Km=SKm, x=x, y=y)


def eadie_hofstee(a, v0):
    while 0 in a:
        index = np.where(a==0)
        a = np.delete(a,index)
        v0 = np.delete(v0,index)
    while 0 in v0:
        index = np.where(v0==0)
        a = np.delete(a,index)
        v0 = np.delete(v0,index)
    x = v0/a
    y = v0
    m, b, Sm, Sb, R, p = lin_regression(x, y)
    V = b
    Km = -m
    SV = Sb
    SKm = Sm
    return res_object('Eadie-Hofstee', V, Km, SE_V=SV, SE_Km=SKm, x=x, y=y)


def hyperbolic(a, v0):
    popt, pcov = curve_fit(MM, a, v0, p0=(max(v0), np.median(a)))
    errors = np.sqrt(np.diag(pcov))
    V, Km = popt[0:2]
    SV, SKm = errors[0:2]
    return res_object('Hyperbolic', V, Km, SE_V=SV, SE_Km=SKm, x=a, y=v0)
    
def cornish_bowden(a, v0):
    straights      = [(v/s, v) for v,s in zip(v0, a)]
    intersects_x   = []
    intersects_y   = []

    n = len(straights)
    for i in range(0, n-1):
        for j in range(i+1, n):
            x = ( straights[j][1] - straights[i][1] ) / ( straights[i][0] - straights[j][0] )
            y = ( straights[i][1]*straights[j][0] - straights[j][1]*straights[i][0] ) / ( straights[j][0] - straights[i][0] )
            intersects_x.append(x)
            intersects_y.append(y)

    V = np.median(intersects_y)
    Km = np.median(intersects_x)
    # TODO: compute CIs
    return res_object('Cornish-Bowden', V, Km, x=a, y=v0)


def read_data(wilkinson): # used just for testing
    wdata = [w.strip() for w in wilkinson.splitlines()]
    a = []
    v0 = []
    for i in wdata:
        if len(i) == 0:
            continue
        x1,x2 = i.split(None, 2)
        try:
            x1 = float(x1)
            x2 = float(x2)
        except:
            continue
        a.append(x1)
        v0.append(x2)
    a = np.array(a)
    v0 = np.array(v0)
    return a,v0


if __name__ == '__main__':
    wilkinson = """
    a     v
    0.138 0.148
    0.220 0.171
    0.291 0.234
    0.560 0.324
    0.766 0.390
    1.460 0.493
    """
    a, v0 = read_data(wilkinson)

    print ('a  =', a)
    print ('v0 =', v0)

    res_values = []

    m_table = ( {'name': 'L.-Burk',
                 'method': lineweaver_burk,
                 'color' : 'g'},
                {'name': 'Hanes',
                 'method': hanes_woolf,
                 'color' : 'c'}, 
                {'name': 'E.-Hofstee',
                 'method': eadie_hofstee,
                 'color' : 'y'}, 
                {'name': 'Hyperbolic',
                 'method': hyperbolic,
                 'color' : 'r'}, 
                {'name': 'C.-Bowden',
                 'method': cornish_bowden,
                 'color' : 'k'} )

    # compute and plot lines
    for m in m_table:
        r = m['method'](a, v0)
        x, y = MM_line(r.V, r.Km, xmax = 2)
        res_values.append(res_tuple(m['name'], r.V, r.Km, r.SE_V, r.SE_Km))
        pl.plot(x, y, linestyle='-', 
                      color=m['color'], 
                      label=m['name'], 
                      linewidth=2)

    pl.ylim(0, 0.8)    

    # plot data
    pl.plot(a, v0, 'bo', ms=6, alpha=0.8, mec='navy', mew=2)
    pl.legend(loc='lower right')

    # draw table
    col_labels = 'Method', 'V', 'SE_V', 'Km', 'SE_Km'
    the_table = pl.table(cellText=res_values,
                         colWidths=[0.08, 0.05, 0.05, 0.05, 0.05],
                         colLabels=col_labels,
                         loc='upper left')
    the_table.set_fontsize(16)
    the_table.scale(2, 1.8)

    pl.show()
