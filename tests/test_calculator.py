import pytest
import requests
import time
import os
import sys

# Get the app URL from environment or use default
BASE_URL = os.getenv('APP_URL', 'http://localhost:3000')

# Wait for app to be ready
def wait_for_app(max_retries=30, delay=1):
    """Wait for the application to be ready"""
    for i in range(max_retries):
        try:
            response = requests.get(f'{BASE_URL}/health', timeout=5)
            if response.status_code == 200:
                print(f"✓ App is ready after {i} attempts")
                return True
        except (requests.ConnectionError, requests.Timeout):
            if i < max_retries - 1:
                time.sleep(delay)
            continue
    
    raise Exception(f"✗ App not ready after {max_retries} attempts at {BASE_URL}")


@pytest.fixture(scope="session", autouse=True)
def setup_app():
    """Wait for app to be ready before running tests"""
    print(f"\n>>> Connecting to app at {BASE_URL}")
    wait_for_app()


class TestCalculatorAdd:
    """Test addition operations"""
    
    def test_add_positive_numbers(self):
        """Test adding two positive numbers"""
        payload = {"a": 5, "b": 3}
        response = requests.post(f'{BASE_URL}/api/add', json=payload)
        assert response.status_code == 200
        assert response.json()["result"] == 8

    def test_add_negative_numbers(self):
        """Test adding two negative numbers"""
        payload = {"a": -5, "b": -3}
        response = requests.post(f'{BASE_URL}/api/add', json=payload)
        assert response.status_code == 200
        assert response.json()["result"] == -8

    def test_add_mixed_numbers(self):
        """Test adding positive and negative numbers"""
        payload = {"a": 10, "b": -5}
        response = requests.post(f'{BASE_URL}/api/add', json=payload)
        assert response.status_code == 200
        assert response.json()["result"] == 5

    def test_add_invalid_input(self):
        """Test adding with invalid input"""
        payload = {"a": "five", "b": 3}
        response = requests.post(f'{BASE_URL}/api/add', json=payload)
        assert response.status_code == 400


class TestCalculatorSubtract:
    """Test subtraction operations"""
    
    def test_subtract_positive_numbers(self):
        """Test subtracting two positive numbers"""
        payload = {"a": 10, "b": 3}
        response = requests.post(f'{BASE_URL}/api/subtract', json=payload)
        assert response.status_code == 200
        assert response.json()["result"] == 7

    def test_subtract_result_negative(self):
        """Test subtraction resulting in negative number"""
        payload = {"a": 3, "b": 10}
        response = requests.post(f'{BASE_URL}/api/subtract', json=payload)
        assert response.status_code == 200
        assert response.json()["result"] == -7


class TestCalculatorMultiply:
    """Test multiplication operations"""
    
    def test_multiply_positive_numbers(self):
        """Test multiplying two positive numbers"""
        payload = {"a": 5, "b": 3}
        response = requests.post(f'{BASE_URL}/api/multiply', json=payload)
        assert response.status_code == 200
        assert response.json()["result"] == 15

    def test_multiply_by_zero(self):
        """Test multiplying by zero"""
        payload = {"a": 5, "b": 0}
        response = requests.post(f'{BASE_URL}/api/multiply', json=payload)
        assert response.status_code == 200
        assert response.json()["result"] == 0

    def test_multiply_negative_numbers(self):
        """Test multiplying two negative numbers"""
        payload = {"a": -5, "b": -3}
        response = requests.post(f'{BASE_URL}/api/multiply', json=payload)
        assert response.status_code == 200
        assert response.json()["result"] == 15


class TestCalculatorDivide:
    """Test division operations"""
    
    def test_divide_positive_numbers(self):
        """Test dividing two positive numbers"""
        payload = {"a": 10, "b": 2}
        response = requests.post(f'{BASE_URL}/api/divide', json=payload)
        assert response.status_code == 200
        assert response.json()["result"] == 5

    def test_divide_with_remainder(self):
        """Test division with remainder"""
        payload = {"a": 10, "b": 3}
        response = requests.post(f'{BASE_URL}/api/divide', json=payload)
        assert response.status_code == 200
        result = response.json()["result"]
        assert abs(result - 3.333) < 0.01, f"Expected ~3.333, got {result}"

    def test_divide_by_zero(self):
        """Test division by zero error handling"""
        payload = {"a": 10, "b": 0}
        response = requests.post(f'{BASE_URL}/api/divide', json=payload)
        assert response.status_code == 400
        assert "Division by zero" in response.json()["error"]


class TestHealthcheck:
    """Test health check endpoint"""
    
    def test_health_endpoint(self):
        """Test the health check endpoint"""
        response = requests.get(f'{BASE_URL}/health')
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
