# Import the dependencies.
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


#################################################
# Database Setup
#################################################
database_path = "C:/Users/aaron/OneDrive/Desktop/sqlalchemy-challenge/Resources/hawaii.sqlite"
engine = create_engine(f"sqlite:///{database_path}")


# reflect an existing database into a new model
Base = automap_base()
Base.prepare(autoload_with=engine)

# reflect the tables
print(Base.classes.keys())

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    """List all available API routes."""
    return (
        f"Welcome to the Hawaii Climate API!<br/><br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation - Last 12 months of precipitation data<br/>"
        f"/api/v1.0/stations - List of weather stations<br/>"
        f"/api/v1.0/tobs - Temperature observations for the most active station over the past year<br/>"
        f"/api/v1.0/&lt;start&gt; - Min, Avg, Max temp from start date<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt; Min, Avg, Max temp between start and end dates"
    )

# Precipitation Route
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = dt.datetime.strptime(most_recent_date, "%Y-%m-%d")
    one_year_ago = most_recent_date - dt.timedelta(days=365)

    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()
    session.close()

    precip_dict = {date: prcp for date, prcp in precipitation_data}
    return jsonify(precip_dict)

# Stations Route
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station).all()
    session.close()

    stations_list = list(np.ravel(results))
    return jsonify(stations_list)

# Temperature observations route
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()[0]
    
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = dt.datetime.strptime(most_recent_date, "%Y-%m-%d")
    one_year_ago = most_recent_date - dt.timedelta(days=365)

    temperature_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= one_year_ago).all()
    session.close()

    temps_list = [{"date": date, "temperature": temp} for date, temp in temperature_data]
    return jsonify(temps_list)

# Start date route
@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine)
    results = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start).all()
    session.close()

    temp_data = list(np.ravel(results))
    return jsonify({"TMIN": temp_data[0], "TAVG": temp_data[1], "TMAX": temp_data[2]})

# Start and end date route
@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start,end):
    session = Session(engine)
    results = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    session.close()

    temp_data = list(np.ravel(results))
    return jsonify({"TMIN": temp_data[0], "TAVG": temp_data[1], "TMAX": temp_data[2]})

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)