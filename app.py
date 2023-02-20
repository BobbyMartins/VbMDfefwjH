from datetime import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

# Initialize Flask app
app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sensors.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Database and Marshmallow
db = SQLAlchemy(app)
ma = Marshmallow(app)


# Define Data Models
class Sensor(db.Model):
    __tablename__ = 'sensors'
    id = db.Column(db.Integer, primary_key=True)
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    windspeed = db.Column(db.Float)
    country_name = db.Column(db.String(64))
    city_name = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"sensorID: {self.id} - {self.city_name}"

    def toJSON(self):
        return {'id': self.id, "temperature": self.temperature, "humidity": self.humidity,
                "windspeed": self.windspeed, 'country_name': self.country_name, 'city_name': self.city_name,
                "created_at": self.created_at}


# API Endpoints
@app.route('/sensors', methods=['POST'])
def create_sensor():
    data = request.json
    if not data or not isinstance(data, dict):
        return jsonify({'message': 'Invalid payload.'}), 400

    sensor = Sensor(id=request.json["id"], temperature=request.json["temperature"], humidity=request.json["humidity"],
                    windspeed=request.json["windspeed"])

    if 'country_name' in data:
        sensor.country_name = request.json["country_name"]

    if 'city_name' in data:
        sensor.city_name = request.json["city_name"]

    print(sensor)
    try:
        db.session.add(sensor)
        db.session.commit()
        return jsonify(sensor.toJSON()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500


@app.route('/sensors', methods=['GET'])
def get_sensors():
    query_params = request.args
    filters = []
    if 'from' in query_params and 'to' in query_params:
        try:
            from_date = datetime.fromisoformat(query_params['from'])
            to_date = datetime.fromisoformat(query_params['to'])
            filters.append(Sensor.created_at.between(from_date, to_date))

        except ValueError:
            return jsonify({'message': 'Invalid date format.'}), 400

    if 'sensor_id' in query_params:
        sensor_id = query_params['sensor_id']
        if isinstance(sensor_id, str):
            filters.append(Sensor.id == int(sensor_id))
        elif isinstance(sensor_id, list):
            filters.append(Sensor.id.in_([int(id) for id in sensor_id]))

    if 'humidity' in query_params:
        filters.append(Sensor.humidity == float(query_params['humidity']))

    if 'temperature' in query_params:
        filters.append(Sensor.temperature == float(query_params['temperature']))

    if 'windspeed' in query_params:
        filters.append(Sensor.windspeed == float(query_params['windspeed']))

    sensors = Sensor.query.filter(*filters).all()
    output = []
    for sensor in sensors:
        sensor_data = sensor.toJSON()
        output.append(sensor_data)

    return jsonify(output)


@app.route('/sensors/<id>', methods=['PUT'])
def update_sensor(id):
    sensor = Sensor.query.get(id)

    if not sensor:
        return jsonify({'message': 'Sensor not found.'}), 404

    data = request.json
    if not data or not isinstance(data, dict):
        return jsonify({'message': 'Invalid payload.'}), 400

    if 'humidity' in data:
        sensor.humidity = data.get('humidity', sensor.humidity)

    if 'temperature' in data:
        sensor.temperature = data.get('temperature', sensor.temperature)

    if 'windspeed' in data:
        sensor.windspeed = data.get('windspeed', sensor.windspeed)

    if 'country_name' in data:
        sensor.country_name = request.json["country_name"]

    if 'city_name' in data:
        sensor.city_name = request.json["city_name"]

    try:
        db.session.commit()
        return jsonify(sensor.toJSON()), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500


@app.route('/')
def index():
    return "It works lol"


# Run the App
if __name__ == '__main__':
    app.run(debug=True)
