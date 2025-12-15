"""
Load tests for MobyPark API endpoints using concurrent requests.

Run with: pytest tests/load_tests.py -v
"""

from fastapi.testclient import TestClient
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.main import app

client = TestClient(app)


class TestPeakHourLoad:
    """Test API under peak hour load (1000 requests) - Sequential due to SQLite limitations"""
    
    def test_peak_load(self):
        """Test 1000 sequential requests (SQLite can't handle true concurrency)"""
        
        def health_check():
            response = client.get("/health/")
            return response.status_code == 200
        
        results = [health_check() for _ in range(1000)]
        success_rate = sum(results) / len(results)
        
        assert success_rate >= 0.95


class TestThroughput:
    """Test API throughput with sequential requests"""
    
    def test_sequential_throughput(self):
        """Test sequential request throughput (100 requests)"""
        
        def health_check():
            response = client.get("/health/")
            return response.status_code == 200
        
        results = [health_check() for _ in range(100)]
        success_rate = sum(results) / len(results)
        
        assert success_rate >= 0.95
