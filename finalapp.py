# Import the dependencies.
#Import Dependencies
from flask import Flask
app = Flask('climateapp')
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import pandas as pd

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
# Reflect the existing database into a new model
Base = automap_base()
Base.prepare(autoload_with=engine)
# reflect the tables
print(Base.classes.keys())
Base()
# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
# Create an instance of Flask
app = Flask('climateapp')




#################################################
# Flask Routes
#################################################
# Define the homepage route
@app.route('/')
def home():
    return (
        f"Welcome to the Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/stats"
    )

# Define the precipitation route
@app.route('/api/v1.0/precipitation')
def precipitation():
    # Find the most recent date in the dataset
    most_recent_date_str = session.query(func.max(Measurement.date)).scalar()
    most_recent_date_dt = datetime.strptime(most_recent_date_str, '%Y-%m-%d')

    # Calculate the date one year before the most recent date
    one_year_before = most_recent_date_dt - timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores for the last year
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_before).all()

    # Convert to a dictionary
    precipitation_data = {date: prcp for date, prcp in results}

    return jsonify(precipitation_data)

# Define the stations route
@app.route('/api/v1.0/stations')
def stations():
    # Perform a query to retrieve the stations
    results = session.query(Station.station, Station.name).all()

    # Convert to a dictionary
    stations_data = [{"station": station, "name": name} for station, name in results]

    return jsonify(stations_data)

# Define the tobs route for the most active station
@app.route('/api/v1.0/tobs')
def tobs():
    # Query to find the most active stations and their counts
    active_stations = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()

    # Get the most active station ID
    most_active_station_id = active_stations[0][0]

    # Calculate the date one year before the most recent date
    most_recent_date_str = session.query(func.max(Measurement.date)).scalar()
    most_recent_date_dt = datetime.strptime(most_recent_date_str, '%Y-%m-%d')
    one_year_before = most_recent_date_dt - timedelta(days=365)

    # Query the last 12 months of temperature observation data for the most active station
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active_station_id).filter(Measurement.date >= one_year_before).all()

    # Convert to a dictionary
    tobs_data = [{"date": date, "temperature": tobs} for date, tobs in results]

    return jsonify(tobs_data)

# Define the stats route for temperature statistics of the most active station
@app.route('/api/v1.0/<start>')
@app.route('/api/v1.0/<start>/<end>')
def stats(start, end=None):
    # Convert start and end dates to datetime objects
    start_date = datetime.strptime(start, '%Y-%m-%d')
    if end:
        end_date = datetime.strptime(end, '%Y-%m-%d')
    else:
        end_date = session.query(func.max(Measurement.date)).scalar()
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

# Query to calculate the lowest, highest, and average temperature for the date range
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    # Convert to a dictionary
    stats_data = {
        "start_date": start,
        "end_date": end if end else "latest",
        "min_temp": results[0][0],
        "max_temp": results[0][1],
        "avg_temp": results[0][2]
    }

    return jsonify(stats_data)

if __name__ == 'climateapp':
    app.run(debug=True)