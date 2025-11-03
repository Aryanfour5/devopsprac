import pytest
import requests
import time
import os

# Get the app URL from environment or use default
BASE_URL = os.getenv('APP_URL', 'http://localhost:3000')

# Wait for app to be ready
def wait_for_app(max_retries=30, delay=1):
    for i in range(max_retries):
        try:
            response = requests.get(f'{BASE_URL}/health', timeout=5)
            if response.status_code == 200:
                print(f"App is ready after {i} attempts")
                return True
        except requests.ConnectionError:
            if i < max_retries - 1:
                time.sleep(delay)
    raise Exception(f"App not ready after {max_retries} attempts")

@pytest.fixture(scope="session", autouse=True)
def setup_app():
    """Wait for app to be ready before running tests"""
    wait_for_app()

class TestCalculatorAdd:
    def test_add_positive_numbers(self):
        payload = {"a": 5, "b": 3}
        response = requests.post(f'{BASE_URL}/api/add', json=payload)
        assert response.status_code == 200
        assert response.json()["result"] == 8

    def test_add_negative_numbers(self):
        payload = {"a": -5, "b": -3}
        response = requests.post(f'{BASE_URL}/api/add', json=payload)
        assert response.status_code == 200
        assert response.json()["result"] == -8

    def test_add_mixed_numbers(self):
        payload = {"a": 10, "b": -5}
        response = requests.post(f'{BASE_URL}/api/add', json=payload)
        assert response.status_code == 200
        assert response.json()["result"] == 5

    def test_add_invalid_input(self):
        payload = {"a": "five", "b": 3}
        response = requests.post(f'{BASE_URL}/api/add', json=payload)
        assert response.status_code == 400

class TestCalculatorSubtract:
    def test_subtract_positive_numbers(self):
        payload = {"a": 10, "b": 3}
        response = requests.post(f'{BASE_URL}/api/subtract', json=payload)
        assert response.status_code == 200
        assert response.json()["result"] == 7

    def test_subtract_result_negative(self):
        payload = {"a": 3, "b": 10}
        response = requests.post(f'{BASE_URL}/api/subtract', json=payload)
        assert response.status_code == 200
        assert response.json()["result"] == -7

class TestCalculatorMultiply:
    def test_multiply_positive_numbers(self):
        payload = {"a": 5, "b": 3}
        response = requests.post(f'{BASE_URL}/api/multiply', json=payload)
        assert response.status_code == 200
        assert response.json()["result"] == 15

    def test_multiply_by_zero(self):
        payload = {"a": 5, "b": 0}
        response = requests.post(f'{BASE_URL}/api/multiply', json=payload)
        assert response.status_code == 200
        assert response.json()["result"] == 0

    def test_multiply_negative_numbers(self):
        payload = {"a": -5, "b": -3}
        response = requests.post(f'{BASE_URL}/api/multiply', json=payload)
        assert response.status_code == 200
        assert response.json()["result"] == 15

class TestCalculatorDivide:
    def test_divide_positive_numbers(self):
        payload = {"a": 10, "b": 2}
        response = requests.post(f'{BASE_URL}/api/divide', json=payload)
        assert response.status_code == 200
        assert response.json()["result"] == 5

    def test_divide_with_remainder(self):
        payload = {"a": 10, "b": 3}
        response = requests.post(f'{BASE_URL}/api/divide', json=payload)
        assert response.status_code == 200
        assert abs(response.json()["result"] - 3.333) < 0.01

    def test_divide_by_zero(self):
        payload = {"a": 10, "b": 0}
        response = requests.post(f'{BASE_URL}/api/divide', json=payload)
        assert response.status_code == 400
        assert "Division by zero" in response.json()["error"]

class TestHealthcheck:
    def test_health_endpoint(self):
        response = requests.get(f'{BASE_URL}/health')
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
