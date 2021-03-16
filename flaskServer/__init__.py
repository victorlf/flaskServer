#!/usr/bin/env python

import sqlite3
import requests
from sqlite3 import Error
from flask import Flask, request, render_template, send_file, make_response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io
from datetime import datetime
#from flask import request


#DATABASE = '/var/www/flaskServer/flaskServer/database/measurements.db'
DATABASE = '/home/victor/Documents/CBPF/obras_raras/flaskServer/flaskServer/database/measurements.db'

app = Flask(__name__)


def makeCon():
    conn=sqlite3.connect(DATABASE)
    curs=conn.cursor()

    return curs

# Retrieve data from database
def getData():
    curs = makeCon()
    for row in curs.execute("SELECT * FROM temp_pres ORDER BY timestamp DESC LIMIT 1"):
        time = str(row[4])
        temp = row[2]
        pres = row[3]
    curs.close()

    return time, temp, pres


def getHistData (numSamples):
    curs = makeCon()
    curs.execute("SELECT * FROM temp_pres ORDER BY timestamp DESC LIMIT "+str(numSamples))
    data = curs.fetchall()
    dates = []
    temps = []
    press = []
    for row in reversed(data):
        dates.append(row[4])
        temps.append(row[2])
        press.append(row[3])
    curs.close()

    return dates, temps, press


def maxRowsTable():
    curs = makeCon()
    for row in curs.execute("select COUNT(temperature) from  temp_pres"):
        maxNumberRows=row[0]
    curs.close()

    return maxNumberRows

# Get sample frequency in minutes
def freqSample():
    times, temps, pres = getHistData (2)
    fmt = '%Y-%m-%d %H:%M:%S'
    tstamp0 = datetime.strptime(times[0], fmt)
    tstamp1 = datetime.strptime(times[1], fmt)
    freq = tstamp1-tstamp0
    freq = int(round(freq.total_seconds()))
    return (freq)

# Define and initialize global variables
global numSamples
numSamples = maxRowsTable()
if (numSamples > 101):
    numSamples = 100

global freqSamples
freqSamples = freqSample()
#freqSamples = 10

global rangeTime
rangeTime = 100


@app.route('/monitor')
def index():	
	time, temp, pres = getData()
	templateData = {
		'time': time,
		'temp': temp,
		'pres': pres,
	}

	return render_template('monitor.html', templateData=templateData)


@app.route('/monitor2', methods=['GET'])
def index2():	
	time, temp, pres = getData()
	templateData = {
		'time': time,
		'temp': temp,
		'pres': pres,
        #'numSamples' : numSamples
        'freq' : freqSamples,
        'rangeTime'	: rangeTime
	}

	return render_template('monitor2.html', templateData=templateData)


@app.route('/monitor2', methods=['POST'])
def my_form_post():
    global numSamples
    global freqSamples
    global rangeTime
    #numSamples = int (request.form['numSamples'])
    rangeTime = int (request.form['rangeTime'])
    if (rangeTime < freqSamples):
        rangeTime = freqSamples + 1
    numSamples = rangeTime//freqSamples
    numMaxSamples = maxRowsTable()
    if (numSamples > numMaxSamples):
        numSamples = (numMaxSamples-1)
    time, temp, pres = getData()
    templateData = {
        'time'	: time,
        'temp'	: temp,
        'pres'	: pres,
        'freq' : freqSamples,
        'rangeTime'	: rangeTime
	}

    return render_template('monitor2.html', templateData=templateData)

@app.route('/monitor3')
def index3():	
	time, temp, pres = getData()
	templateData = {
		'time': time,
		'temp': temp,
		'pres': pres,
        #'numSamples' : numSamples
        'freq' : freqSamples,
        'rangeTime'	: rangeTime
	}

	return render_template('monitor3.html', templateData=templateData)


@app.route('/plot/temp')
def plot_temp():
	times, temps, press = getHistData(numSamples)
	ys = temps
	fig = Figure()
	axis = fig.add_subplot(1, 1, 1)
	axis.set_title("Temperature [°C]")
	axis.set_xlabel("Samples")
	axis.grid(True)
	xs = range(numSamples)
	axis.plot(xs, ys)
	canvas = FigureCanvas(fig)
	output = io.BytesIO()
	canvas.print_png(output)
	response = make_response(output.getvalue())
	response.mimetype = 'image/png'

	return response


@app.route('/plot/pres')
def plot_pres():
	times, temps, press = getHistData(numSamples)
	ys = press
	fig = Figure()
	axis = fig.add_subplot(1, 1, 1)
	axis.set_title("Pressure [hPa]")
	axis.set_xlabel("Samples")
	axis.grid(True)
	xs = range(numSamples)
	axis.plot(xs, ys)
	canvas = FigureCanvas(fig)
	output = io.BytesIO()
	canvas.print_png(output)
	response = make_response(output.getvalue())
	response.mimetype = 'image/png'

	return response


@app.route('/postjson', methods = ['POST'])
def postJsonHandler():
    print (request.is_json)
    content = request.get_json()
    print (content)
    print('JSON posted')

    try:
        sensor = content['sensor']
        temp = content['temperature']
        pres = content['pressure']

        print(sensor)

        #con = sqlite3.connect('database/temperature.db')
        with sqlite3.connect(DATABASE) as con:
            cur = con.cursor()
            cur.execute("INSERT INTO temp_pres (sensor, temperature, pressure, timestamp) Values (?, ?, ?, datetime('now', 'localtime'))", (sensor, temp, pres))

            con.commit()
            con.close()
        return "Record successfully added"
    except:
        #con.rollback()
        return "error in insert operation"

    print(200)



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8090)
