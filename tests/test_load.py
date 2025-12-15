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
        
        
        def random_operation():
            operation = random.choice(['view_lots', 'health', 'view_lots'])
            
            if operation == 'view_lots':
                response = client.get("/parking_lots/")
            elif operation == 'health':
                response = client.get("/health/")
            
            return response.status_code == 200

        
        # Sequential requests - SQLite locks prevent concurrent database access
        start_time = time.time()
        all_results = []
        
        for i in range(1000):
            result = random_operation()
            all_results.append(result)
            if i % 100 == 0:
                print(f"Progress: {i}/1000")
        
        end_time = time.time()

        duration = end_time - start_time
        success_count = sum(all_results)
        success_rate = success_count / len(all_results)
        print(f"Total Duration: {duration:.2f} seconds")
        assert success_rate >= 0.95


class TestThroughput:
    """Test API throughput with sequential requests"""
    
    def test_sequential_throughput(self):
        """Test sequential request throughput (100 requests)"""
        
        def view_parking_lots():
            response = client.get("/parking_lots/")
            return response.status_code == 200
        
        start_time = time.time()
        results = [view_parking_lots() for _ in range(100)]
        end_time = time.time()
        
        duration = end_time - start_time
        success_rate = sum(results) / len(results)
        print(f"Total Duration: {duration:.2f} seconds")
        assert success_rate >= 0.95
