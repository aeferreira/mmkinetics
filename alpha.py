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


wilkinson = [["# Wilkinson", "demo data"],
             ["#a", "v"],
             ["0.138", "0.148"],
             ["0.220", "0.171"],
             ["0.291", "0.234"],
             ["0.560", "0.324"],
             ["0.766", "0.390"],
             ["1.460", "0.493"]]



# AJAX calls
@app.route('/_demodata')
def demo_data():
    return jsonify(result=wilkinson)


# main page
@app.route('/front', methods=['POST', 'GET'])
def front_page():
    if request.method != 'POST':
        return render_template('test.html')

    data = str(request.form['data_values'])

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
        if len(line.split(',')) != 2:
            messages.append('Please provide a two column input')
            bad_input = True
            break
        try:
            x0 = float(line.split(',')[0])
            x1 = float(line.split(',')[1])
        except:
            messages.append('Please comment text lines with a # symbol')
            bad_input = True
            break

        x.append(x0)
        y.append(x1)

    if bad_input:
        return jsonify({"status": "error", "messages": messages})

    a, v0 = methods.lists2arrays(x, y)

    results_table = ''
    results = []
    for m in (methods.hanes_woolf,
              methods.eadie_hofstee,
              methods.lineweaver_burk,
              methods.hyperbolic,
              methods.cornish_bowden):
        r = m(a, v0)
        results.append(r)
        results_table += """
        <tr>
            <td>{0}</td>
            <td>{1}</td>
            <td>{2}</td>
        """.format(r.name, round(r.V, 4), round(r.Km, 4))
        if r.SE_V:
            results_table += """<td>{0}</td>
            <td>{1}</td></tr>""".format(round(r.SE_V, 4),
                                        round(r.SE_Km, 4))
        else:
            results_table += "<td></td><td></td></tr>"

    results_table = """
    <div class="table-responsive">
        <table class="table table-striped table-bordered table-hover">
            <thead>
                <tr>
                    <th><strong>Method</strong></th>
                    <th><i>V</i></th>
                    <th><i>K<sub>m</sub></i></th>
                    <th>SE (<i>V</i>)</th>
                    <th>SE (<i>K<sub>m</sub></i>)</th>
                </tr>
            </thead>
            <tbody>
    {0}
            </tbody>
        </table>
    </div>
    """.format(results_table)

    plots = methods.generate_plots(a, v0, results)

    script, divs = methods.components(plots)

    plots_div = """
<div class="row">
    <div class="col-md-5">
        {0}
    </div>
    <div class="col-md-7">
        <div class="row">
            <div class="col-md-6">
                {1}
            </div>
            <div class="col-md-6">
                {2}
            </div>
        </div>
        <div class="row">
            <div class="col-md-6">
                {3}
            </div>
            <div class="col-md-6">
                {4}
            </div>
        </div>
    </div>
</div>
    """.format(divs[0], divs[1], divs[2], divs[3], divs[4])

    return jsonify({'bokeh_divs': plots_div,
                    'bokeh_script': script,
                    'results_table': results_table})


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
