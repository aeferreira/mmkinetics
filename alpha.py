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
        bad_input=False
        
        x=[]
        y=[]

        messages=[]

        #check if input is empty
        if len(data.replace('\n', '').split()) == 0:
            bad_input = True
            messages.append('Please provide a two column input')

        for line in data.splitlines():
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
                
        results=[]
        results.append(methods.hanes_woolf(v0, a))
        results.append(methods.eadie_hofstee(v0, a))
        results.append(methods.lineweaver_burk(v0, a))
        results.append(methods.hyperbolic(v0, a))
        results.append(methods.cornish_bowden(v0, a))

        #bokeh_script, = graphs(hanes[3] ,'test')
        script, div = graphs(results[0].x, results[0].y, 'Hanes')
        return render_template('test.html', 
                               data=data, 
                               results=results, 
                               bokeh_script=script, 
                               bokeh_div=div)
    else:
        return render_template('test.html')

def graphs(x, y, name):
    
    #output_file('static/my_plot.html')
    p = figure(plot_width=300, plot_height=300)
        
    p.line(x, y, legend=name,
           line_color="black",
           line_width=2)
    p.circle(x, y, legend=name, 
            fill_color='blue', 
            fill_alpha=0.2,
            color='blue',
            size=8)

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
