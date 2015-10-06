from flask import Flask, url_for, request, render_template, session, redirect, make_response
import os
from bokeh.plotting import figure, output_file, save
from bokeh.resources import CDN
from bokeh.embed import file_html, components
import methods

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
        
        x=[]
        y=[]

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
            
            x.append(x0)
            y.append(x1)

        if bad_input:
            return render_template('test.html', messages=messages, data=data)

        v0, a = methods.lists2arrays(x, y)
        
        messages.append('xy ' + str([(x,y) for (x,y) in zip(v0,a)]))
        
        hanes = methods.Hanes(v0, a)
        hofstee = methods.Hofstee(v0, a)
        burk = methods.Burk(v0, a)
        try:
            hyp_reg = methods.Hyp_Reg(v0, a)
        except:
            hyp_reg = "Could not estimate kinect constants from the hyperbolic regression method"
        try:
            cornish_bowden = methods.Cornish_Bowden(v0, a)
        except:
            cornish_bowden = "Could not estimate kinect constants from the Cornish-Bowden method"

        # ISSUE: if hyp_reg or cornish_bowden fail, they become strings
        # and the code below fails or reports chars, because of indexing
        
        results=[]
        results.append(('Hanes', hanes[0], hanes[1], hanes[2]))
        results.append(('Eddie-Hofstee', hofstee[0], hofstee[1], hofstee[2]))
        results.append(('Lineweaver-Burk', burk[0], burk[1], burk[2]))
        results.append(('Hyperbolic regression', hyp_reg[0], hyp_reg[1], hyp_reg[2], hyp_reg[3]))
        results.append(('Cornish-Bowden', cornish_bowden[0], cornish_bowden[1], cornish_bowden[2], cornish_bowden[3] ))

        #bokeh_script, = graphs(hanes[3] ,'test')
        script, div = graphs(hanes[3], 'Hanes')
        return render_template('test.html', data=data, results=results, 
                               bokeh_script=script, bokeh_div=div)
    else:
        return render_template('test.html')

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
