
from flask import Flask, url_for, request, render_template, session, redirect, make_response
from scipy.optimize import curve_fit
from scipy import stats
import numpy as np
import os
from bokeh.plotting import figure, output_file, save
from bokeh.resources import CDN
from bokeh.embed import file_html, components

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def landing():  
    return render_template('landing.html')

@app.route('/help')
def help():
    # TODO: use module markdown2 to convert README to html fragment
    with open('README.md', 'r') as file:
        readme = ''
        for line in file:
            readme+=line
    return render_template('help.html', readme=readme.decode('utf-8'))

@app.route('/contacts')
def contacts():  
    return render_template('contacts.html')


@app.route('/front', methods=['POST', 'GET'])
def front_page():
    if request.method == 'POST':
        data = str(request.form['timevsconc'])
        aux = data[:] # TODO is this copy really necessary ?
        bad_input=False
        
        xy=[]

        messages=[]

        #chaeck if input is empty
        if len(aux.replace('\n', '').split()) == 0:
            bad_input = True
            messages.append('Please provide a two column input')

        for line in aux.splitlines():
            line = line.strip()
            if len(line) == 0 or line.startswith('#'):
                continue
            if len(line.split()) != 2:
                messages.append('Please provide a two column input')
                bad_input = True
                break
            try:
                x0 = float(line.split()[0])
                x1 = float(line.split()[1])
            except:
                messages.append('Please comment text lines with a # symbol')
                bad_input = True
                break
            
            # TODO: handle this better: (0,0) should be a legal input point
            if x0 == 0 or x1 == 0:
                messages.append('Please remove zero values from data')
                bad_input = True
                break
            
            xy.append([x0,x1])

        if not bad_input:
            messages.append('xy'+ str(xy))
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

            # ISSUE: if hyp_reg or cornish_bowden fail, they become strings
            # and the code below fails or reports chars, because of indexing
            
            results=[]
            results.append(('Hanes', hanes[0], hanes[1], hanes[2]))
            results.append(('Eddie-Hofstee', hofstee[0], hofstee[1], hofstee[2]))
            results.append(('Lineweaver-Burk', burk[0], burk[1], burk[2]))
            results.append(('Hyperbolic regression', round(hyp_reg[0],6), round(hyp_reg[1],6), [round(float(i), 6) for i in hyp_reg[2]]))
            results.append(('Cornish-Bowden', cornish_bowden[0], cornish_bowden[1], cornish_bowden[2], cornish_bowden[3] ))

            #bokeh_script, = graphs(hanes[3] ,'test')
            
            return render_template('test.html', data=data, results=results, bokeh_script=hanes[3][0], bokeh_div=hanes[3][1])
        else:
            return render_template('test.html', messages=messages, data=data)
    else:
        return render_template('test.html')

# TODO: discuss the need for these early application of round on the regression
def Hanes(xy):
    hanes=[]
    for i in xy:
        hanes.append([float(i[1]),float(i[1])/float(i[0])])
    slope, intercept, r_value, p_value, std_error = stats.linregress([i[0] for i in hanes], [i[1] for i in hanes])

    # Vmax, Km, error, lin_reg, points
    return (round(slope**-1, 6),
            round(intercept*(slope**-1),6),
            round(std_error,6),
            graphs(hanes, 'Hanes'))

def Hofstee(xy):
    hofstee=[]
    for i in xy:
        hofstee.append([float(i[0])/float(i[1]),float(i[0])])
    slope, intercept, r_value, p_value, std_error = stats.linregress([i[0] for i in hofstee], [i[1] for i in hofstee])

    # Vmax, Km, error, lin_reg, points
    return (round(intercept,6),
            round(slope*-1,6),
            round(std_error,6),
            hofstee)
    
def Burk(xy):
    burk=[]
    for i in xy:
        burk.append([1/float(i[1]),1/float(i[0])])
    slope, intercept, r_value, p_value, std_error = stats.linregress([i[0] for i in burk], [i[1] for i in burk])

    # Vmax, Km, error, lin_reg, points 
    return (round(intercept**-1,6),
            round(slope*(intercept)**-1,6),
            round(std_error,6),
            burk)

def menten(s, V, Km):
    return V * s / (Km + s)

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
    return  [popt[0], popt[1], str(np.sqrt(np.diag(pcov))).replace('[', '').replace(']', '').split(), hyp_reg, xy]


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
    return [round(np.median(intersects_y),6), round(np.median(intersects_x),6), str(round(min(intersects_y),6))+';'+str(round(max(intersects_y),6)),str(round(min(intersects_x),6))+';'+str(round(max(intersects_x),6)),straights]

def graphs(points, name):
    
    #output_file('static/my_plot.html')
    p = figure(plot_width=300, plot_height=300)
    
    xpoints = []
    ypoints = []
    
    for i in points:
        xpoints.append(i[0])
        ypoints.append(i[1])
    
    p.square(xpoints, ypoints, legend=name, fill_color=None, line_color="black")
    p.line(xpoints, ypoints, legend=name, line_color="black")

    script, div = components(p)
    html = file_html(p, CDN, "my_plot")
    #save(p)
    return script, div

if __name__ == '__main__':
    app.run(debug=True)
'''
# testing data
0.00858 0.05
0.01688 0.1
0.02489 0.25
0.03032 0.5
0.03543 1
0.03447 2.5
0.03993 5   
'''
#alterar formato de input ? [s] vs v
# TODO: yes, it is better!
