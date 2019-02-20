import os
import methods
from flask import (Flask,
                   request,
                   render_template,
                   session,
                   redirect,
                   make_response,
                   jsonify)

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
    return render_template('help.html', readme=readme)


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


# AJAX calls
@app.route('/_demodata')
def demo_data():
    return jsonify(result=wilkinson)


# main page
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

    plots = methods.generate_plots(a, v0, results)

    script, divs = methods.components(plots)
    print(script, divs)
    
    return render_template('test.html',
                           data=data,
                           results=results,
                           bokeh_script=script,
                           bokeh_divs=divs)


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
