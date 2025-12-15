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
        
        # Simulate 1000 requests in batches to spread the load
        start_time = time.time()
        all_results = []
        
        # Process in 10 batches of 100 requests each
        for batch in range(10):
            with ThreadPoolExecutor(max_workers=25) as executor:
                futures = [executor.submit(random_operation) for _ in range(100)]
                results = [f.result() for f in as_completed(futures)]
                all_results.extend(results)
            time.sleep(0.1)  # Small delay between batches
        
        end_time = time.time()
        
        duration = end_time - start_time
        success_count = sum(all_results)
        success_rate = success_count / len(all_results)
        
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
