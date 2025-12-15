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
    """Test API under peak hour load (1000 requests)"""
    
    def test_peak_load(self):
        """Test 1000 concurrent mixed operations"""
        
        def random_operation():
            try:
                operation = random.choice(['view_lots', 'health', 'view_lots'])
                
                if operation == 'view_lots':
                    response = client.get("/parking_lots/")
                elif operation == 'health':
                    response = client.get("/health/")
                
                return response.status_code == 200
            except Exception:
                return False
        
        # Simulate 1000 concurrent requests
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = [executor.submit(random_operation) for _ in range(1000)]
            results = [f.result() for f in as_completed(futures)]
        end_time = time.time()
        
        duration = end_time - start_time
        success_count = sum(results)
        success_rate = success_count / len(results)
        
        print(f"\n1000 requests completed in {duration:.2f} seconds")
        print(f"Success rate: {success_rate:.2%} ({success_count}/1000)")
        print(f"Throughput: {1000/duration:.2f} requests/second")
        
        # At least 90% should succeed
        assert success_rate >= 0.90


class TestConcurrentLoad:
    """Test API under concurrent load"""
    
    def test_concurrent_requests(self):
        """Test concurrent parking lot views"""
        
        def view_parking_lots():
            response = client.get("/parking_lots/")
            return response.status_code == 200
        
        # Simulate 50 concurrent requests
        with ThreadPoolExecutor(max_workers=25) as executor:
            futures = [executor.submit(view_parking_lots) for _ in range(50)]
            results = [f.result() for f in as_completed(futures)]
        
        # All requests should succeed
        assert all(results)
