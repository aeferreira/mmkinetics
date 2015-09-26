
from flask import Flask, url_for, request, render_template, session, redirect, make_response
from scipy.optimize import curve_fit
from scipy import stats
import numpy as np
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/', methods=['POST', 'GET'])
def front_page():
    if request.method == 'POST':
        data = str(request.form['timevsconc'])
        aux=''
        saida=0
        xy=[]

        for i in data:
            aux+=i

        messages=[]
        for line in aux.splitlines():
            line = line.strip()
            if '#' in line:
                continue
            elif len(line.replace(' ','')) == 0:
                continue
            elif len(line.split()) != 2:
                messages.append('Please provide a two column input')
                saida = 1
                break
            elif float(line.split()[0]) == 0 or float(line.split()[1]) == 0:
                messages.append('Please remove zero values from data')
                saida = 1
                break
            xy.append([line.split()[0],line.split()[1]])

        if saida != 1:
            messages.append('xy'+str(xy))        
            hanes = Hanes(xy)
            hofstee = Hofstee(xy)
            burk = Burk(xy)
            try:
                hyp_reg = Hyp_Reg(xy)
            except:
                hyp_reg = "Could not estimate kinect constants from the hyperbolic regression method"
            try:
                cornish_bowden = Cornish_Bowden(xy)
            except:
                cornish_bowden = "Could not estimate kinect constants from the Cornish-Bowden method"
            return render_template('test.html', results=[hanes,hofstee,burk,hyp_reg,cornish_bowden])
        else:
            return render_template('test.html', messages=messages)
    else:
        return render_template('test.html')
    
def Hanes(xy):
    hanes=[]
    for i in xy:
        hanes.append([float(i[1]),float(i[1])/float(i[0])])
    slope, intercept, r_value, p_value, std_error = stats.linregress([i[0] for i in hanes], [i[1] for i in hanes])

    # Vmax, Km, error, lin_reg, points
    return [slope**-1, intercept*(slope**-1), std_error, hanes]

def Hofstee(xy):
    hofstee=[]
    for i in xy:
        hofstee.append([float(i[0])/float(i[1]),float(i[0])])
    slope, intercept, r_value, p_value, std_error = stats.linregress([i[0] for i in hofstee], [i[1] for i in hofstee])

    # Vmax, Km, error, lin_reg, points
    return [intercept, slope*-1, std_error, hofstee]
    
def Burk(xy):
    burk=[]
    for i in xy:
        burk.append([1/float(i[1]),1/float(i[0])])
    slope, intercept, r_value, p_value, std_error = stats.linregress([i[0] for i in burk], [i[1] for i in burk])

    # Vmax, Km, error, lin_reg, points 
    return [intercept**-1, slope*(intercept)**-1, std_error, burk]


def menten(s, vmax, km):
    return vmax * s / (km + s)

def Hyp_Reg(xy):
    s = []
    v = []

    for i in xy:
        s.append(float(i[1]))
        v.append(float(i[0]))

    estimated_vmax = max(v)
    for i in range(len(s)):
        if v[i] < estimated_vmax / 2:
            estimated_km = s[i]
    
    s = np.array(s)
    v = np.array(v)

    initial_guess = [estimated_vmax,estimated_km]
    popt, pcov = curve_fit(menten, s, v, p0=initial_guess)
    
    sfit = np.linspace(0,max(s)*1.1)
    vfit = menten(sfit, popt[0], popt[1])
    
    hyp_reg = [] 
    for i in range(len(sfit)):
        hyp_reg.append([sfit[i],vfit[i]])

    # Vmax, Km, error(Vmax,Km), hyp_reg, points
    return  [popt[0], popt[1], np.sqrt(np.diag(pcov)), hyp_reg, xy]

def Cornish_Bowden(xy):
    cornish_bowden = []
    straights      = []
    intersects     = []
    done           = []
    for i in xy:

        m = (float(i[0]) / float(i[1]))
        b = float(i[0])

        straights.append([m,b])
    for s in range(0,len(straights)):
        for ss in range(0,len(straights)):
            done.append([s,ss])
            if [ss,s] in done:
                continue
            if s == ss:
                continue
            else:
                x = ( straights[ss][1] - straights[s][1] ) / ( straights[s][0] - straights[ss][0] )
                y = ( straights[s][1]*straights[ss][0] - straights[ss][1]*straights[s][0] ) / ( straights[ss][0] - straights[s][0] )
                intersects.append([x,y])

    intersects_x = [i[0] for i in intersects]
    intersects_y = [i[1] for i in intersects]
    
    # Vmax, Km, error interval Vmax, error interval Km, straights
    return [np.median(intersects_y),np.median(intersects_x),str(min(intersects_y))+'-'+str(max(intersects_y)),str(min(intersects_x))+'-'+str(max(intersects_x)),straights]

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

#testing
#0.00858 0.05
#0.01688 0.1
#0.02489 0.25
#0.03032 0.5
#0.03543 1
#0.03447 2.5
#0.03993 5

#alterar formato de input ? [s] vs v
