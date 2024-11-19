import pytest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

@pytest.fixture
def client():
    """
    Create a test client for the Flask application
    """
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_all_vehicles(client):
    """
    Test the GET /vehicles route
    """
    response = client.get('/vehicles')
    assert response.status_code == 200
    assert isinstance(response.json, dict)

def test_get_valid_vehicle(client):
    """
    Test the GET /vehicles/<vin> route
    """
    response = client.get('/vehicles/test1')
    assert response.status_code == 200

def test_get_invalid_vehicle(client):
    """
    Test the GET /vehicles/<vin> route with an invalid VIN
    """
    response = client.get('/vehicles/invalid')
    assert response.status_code == 400

def test_vin_trigger(client):
    """
    Test the GET /vehicles/<vin> route with a case-insensitive VIN
    """
    response = client.get('/vehicles/TEST1')
    assert response.status_code == 400

def test_create_vehicle(client):
    """
    Test the POST /create_vehicle route
    """
    response = client.post('/create_vehicle', json={
        'vin': 'mock_vin',
        'manufacturer_name': 'mock_manufacturer',
        'horse_power': 100,
        'model_name': 'mock_model',
        'model_year': 2021,
        'purchase_price': 10000,
        'fuel_type': 'Gasoline'
    })
    assert response.status_code == 200
    assert response.json['Vehicle'].get('vin') == 'mock_vin'

def test_create_vehicle_missing_fields(client):
    """
    Test the POST /create_vehicle route with missing required fields
    """
    response = client.post('/create_vehicle', json={
        'vin': 'mock_vin_2'
    })
    assert response.status_code == 422
    assert 'Missing required fields' in response.json['error']

def test_create_vehicle_invalid_fields(client):
    """
    Test the POST /create_vehicle route with invalid data types for specific fields
    """
    response = client.post('/create_vehicle', json={
        'vin': 'mock_vin_3',
        'manufacturer_name': 'mock_manufacturer',
        'horse_power': 100,
        'model_name': 'mock_model',
        'model_year': '2021',
        'purchase_price': 10000,
        'fuel_type': 'Gasoline'
    })
    assert response.status_code == 422
    assert 'Invalid data type for model_year' in response.json['error']

    response = client.post('/create_vehicle', json={
        'vin': 'mock_vin_4',
        'manufacturer_name': 'mock_manufacturer',
        'horse_power': '100',
        'model_name': 'mock_model',
        'model_year': 2021,
        'purchase_price': 10000,
        'fuel_type': 'Gasoline'
    })
    assert response.status_code == 422
    assert 'Invalid data type for horse_power' in response.json['error']

    response = client.post('/create_vehicle', json={
        'vin': 'mock_vin_5',
        'manufacturer_name': 'mock_manufacturer',
        'horse_power': 100,
        'model_name': 'mock_model',
        'model_year': 2021,
        'purchase_price': 'invalid_purchase_price',
        'fuel_type': 'Gasoline'
    })

    assert response.status_code == 422
    assert 'Invalid data type for purchase_price' in response.json['error']

def test_update_vehicle(client):
    """
    Test the PUT /update_vehicle/<vin> route
    """
    response = client.put('/update_vehicle/test1', json={
        'manufacturer_name': 'updated_manufacturer',
        'horse_power': 200,
        'model_name': 'updated_model',
        'model_year': 2022,
        'purchase_price': 20000,
        'fuel_type': 'Electric'
    })
    assert response.status_code == 200
    assert response.json['Vehicle'].get('manufacturer_name') == 'updated_manufacturer'

def test_invalid_update_vehicle(client):
    """
    Test the PUT /update_vehicle/<vin> route with an invalid VIN
    """
    response = client.put('/update_vehicle/invalid', json={
        'manufacturer_name': 'updated_manufacturer',
        'horse_power': 200,
        'model_name': 'updated_model',
        'model_year': 2022,
        'purchase_price': 20000,
        'fuel_type': 'Electric'
    })
    assert response.status_code == 404
    assert 'Vehicle not found' in response.json['error']

def test_invalid_update_parameters(client):
    """
    Test the PUT /update_vehicle/<vin> route with invalid data types for specific fields
    """
    response = client.put('/update_vehicle/test1', json={
        'manufacturer_name': 'updated_manufacturer',
        'horse_power': 'invalid_horse_power',
        'model_name': 'updated_model',
        'model_year': 2022,
        'purchase_price': 20000,
        'fuel_type': 'Electric'
    })

    assert response.status_code == 422
    assert 'Invalid data type for horse_power' in response.json['error']

def test_delete_vehicle(client):
    """
    Test the DELETE /delete_vehicle/<vin> route
    """
    response = client.delete('/delete_vehicle/test1')
    assert response.status_code == 204

def test_invalid_delete_vehicle(client):
    """
    Test the DELETE /delete_vehicle/<vin> route with an non-existent VIN
    """
    response = client.delete('/delete_vehicle/invalid')
    assert response.status_code == 404
    assert 'Vehicle not found' in response.json['error']
