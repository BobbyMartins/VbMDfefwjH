import unittest

from app import app, db, Sensor


class SensorApiTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_sensor(self):
        data = {
            'id': 1,
            'temperature': 25.0,
            'humidity': 60.0,
            'windspeed': 10.0,
            'country_name': 'USA',
            'city_name': 'New York'
        }
        response = app.test_client().post('/sensors', json=data)
        print(response.json)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['id'], 1)
        self.assertEqual(response.json['temperature'], 25.0)
        self.assertEqual(response.json['humidity'], 60.0)
        self.assertEqual(response.json['windspeed'], 10.0)
        self.assertEqual(response.json['country_name'], 'USA')
        self.assertEqual(response.json['city_name'], 'New York')

    def test_get_sensors(self):
        s1 = Sensor(id=1, temperature=25.0, humidity=60.0, windspeed=10.0, country_name='USA', city_name='New York')
        s2 = Sensor(id=2, temperature=20.0, humidity=50.0, windspeed=5.0, country_name='USA', city_name='Boston')
        with app.app_context():
            db.session.add(s1)
            db.session.add(s2)
            db.session.commit()

        response = app.test_client().get('/sensors?temperature=25.0')
        print(response.json)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]['id'], 1)
        self.assertEqual(response.json[0]['temperature'], 25.0)
        self.assertEqual(response.json[0]['humidity'], 60.0)
        self.assertEqual(response.json[0]['windspeed'], 10.0)
        self.assertEqual(response.json[0]['country_name'], 'USA')
        self.assertEqual(response.json[0]['city_name'], 'New York')

    def test_update_sensor(self):
        s = Sensor(id=1, temperature=25.0, humidity=60.0, windspeed=10.0, country_name='USA', city_name='New York')
        with app.app_context():
            db.session.add(s)
            db.session.commit()

        data = {
            'humidity': 70.0,
            'city_name': 'San Francisco'
        }
        response = app.test_client().put('/sensors/1', json=data)
        print(response.json)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['id'], 1)
        self.assertEqual(response.json['temperature'], 25.0)
        self.assertEqual(response.json['humidity'], 70.0)
        self.assertEqual(response.json['windspeed'], 10.0)
        self.assertEqual(response.json['country_name'], 'USA')
        self.assertEqual(response.json['city_name'], 'San Francisco')