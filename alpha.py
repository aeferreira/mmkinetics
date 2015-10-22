import os
from math import atan
from flask import (Flask,
                   request,
                   render_template,
                   session,
                   redirect,
                   make_response,
                   jsonify)
from bokeh.plotting import figure  # not used: , output_file, save
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
            readme += line
    return render_template('help.html', readme=readme.decode('utf-8'))


@app.route('/contacts')
def contacts():
    return render_template('contacts.html')


wilkinson = """# Wilkinson demo data
#a     v
0.138 0.148
0.220 0.171
0.291 0.234
0.560 0.324
0.766 0.390
1.460 0.493
"""


@app.route('/_demodata')
def demo_data():
    return jsonify(result=wilkinson)


@app.route('/front', methods=['POST', 'GET'])
def front_page():
    if request.method != 'POST':
        return render_template('test.html')

    data = str(request.form['timevsconc'])
    bad_input = False

    x = []
    y = []

    messages = []

    # check if input is empty
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

        x.append(x0)
        y.append(x1)

    if bad_input:
        return render_template('test.html', messages=messages, data=data)

    a, v0 = methods.lists2arrays(x, y)

    results = []
    for m in (methods.hanes_woolf,
              methods.eadie_hofstee,
              methods.lineweaver_burk,
              methods.hyperbolic,
              methods.cornish_bowden):
        results.append(m(a, v0))

    plots = [lin_plot(results[i], results[i].name) for i in (0,1,2)]
    script, divs = components(plots)

    return render_template('test.html',
                           data=data,
                           results=results,
                           bokeh_script=script,
                           bokeh_divs=divs)


def lin_plot(results, name):

    x = results.x
    y = results.y

    xmax = max(x * 1.1)
    ymax = max(y * 1.1)
    x_range = (0, xmax)
    y_range = (0, ymax)

    p = figure(plot_width=300, plot_height=300, title=name,
               x_range=x_range,
               y_range=y_range)

    ymax = xmax * results.m + results.b

    p.line(x=[0, xmax], y=[results.b, ymax],
           line_color="blue",
           line_width=2)

    p.circle(x, y,
             fill_color='white',
             color='blue',
             size=6)

    p.title_text_font_size = '12pt'

    return p

if __name__ == '__main__':
    app.run(debug=True)
# '''
# # testing data
# 0.00858 0.05
# 0.01688 0.1
# 0.02489 0.25
# 0.03032 0.5
# 0.03543 1
# 0.03447 2.5
# 0.03993 5
# '''
