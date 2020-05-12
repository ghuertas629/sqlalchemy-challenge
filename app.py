# import modules
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
import datetime as dt

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect = True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Setup
app = Flask(__name__)

# Define available flask routes
@app.route("/")
def welcome():
    return (
        f'Available Routes:<br/>'
        f'/api/v1.0/precipitation<br/>'
        f'/api/v1.0/stations<br/>'
        f'/api/v1.0/tobs<br/>'
        f'/api/v1.0/[start]<br/>'
        f'/api/v1.0/[start]/[end]'
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Perform a query to retrieve the data and precipitation scores
    prcp_data = session.query(Measurement.date, Measurement.prcp).\
                order_by(Measurement.date).all()

    # Convert to list of dictionaries for jsonify
    prcp_data_list = {}

    for date, prcp in prcp_data:
        prcp_data_list[date] = prcp

    # Close session and return jsonify object
    session.close()

    return jsonify(prcp_data_list)

@app.route("/api/v1.0/stations")
def stations():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Create dictionary to hold data for jsonify
    stations = {}

    # Query all stations
    station_results = session.query(Station.station, Station.name).all()

    for station, name in station_results:
        stations[station] = name

    # Close session and return jsonify object
    session.close()

    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Design a query to retrieve the last 12 months of precipitation data and plot the results
    # Obtain last date in dataset
    last_date = session.query(Measurement.date).\
        order_by(Measurement.date.desc()).first()

    # Calculate the date 1 year ago from the last data point in the database
    last_year_date = (dt.datetime.strptime(last_date[0], '%Y-%m-%d')) - dt.timedelta(days=366)

    # Query data
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
                filter(Measurement.date >= last_year_date, Measurement.station == 'USC00519281').\
                order_by(Measurement.date).all()

    # Convert to list of dictionaries for jsonify
    tobs_data_list = {}

    for date, tobs in tobs_data:
        tobs_data_list[date] = tobs

    # Close session and return jsonify object
    session.close()

    return jsonify(tobs_data_list)

@app.route("/api/v1.0/<start>")
def temp_range_start(start):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query data
    start_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).all()

    # Convert to list of dictionaries for jsonify
    final_data = {}
    final_data['Start Date'] = start
    for min, avg, max in start_data:
        final_data['TMIN'] = min
        final_data['TAVG'] = avg
        final_data['TMAX'] = max

    # Close session and return jsonify object
    session.close()

    return jsonify(final_data)

@app.route("/api/v1.0/<start>/<end>")
def temp_range_start_end(start, end):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query data
    start_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    # Convert to list of dictionaries for jsonify
    final_data = {}
    final_data['Start Date'] = start
    final_data['End Date'] = end
    for min, avg, max in start_data:
        final_data['TMIN'] = min
        final_data['TAVG'] = avg
        final_data['TMAX'] = max

    # Close session and return jsonify object
    session.close()

    return jsonify(final_data)

if __name__ == "__main__":
    app.run(debug=True)