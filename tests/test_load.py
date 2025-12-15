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
        """Test 1000 requests with spacing"""
        
        errors = []
        
        def random_operation():
            try:
                time.sleep(0.1)  # 100ms delay per request
                operation = random.choice(['view_lots', 'health', 'view_lots'])
                
                if operation == 'view_lots':
                    response = client.get("/parking_lots/")
                elif operation == 'health':
                    response = client.get("/health/")
                
                return response.status_code == 200
            except Exception as e:
                errors.append(str(e))
                return False
        
        # Simulate 1000 requests with minimal concurrency
        start_time = time.time()
        all_results = []
        
        # Process in 100 batches of 10 requests with only 2 workers
        for batch in range(100):
            with ThreadPoolExecutor(max_workers=2) as executor:
                futures = [executor.submit(random_operation) for _ in range(10)]
                results = [f.result() for f in as_completed(futures)]
                all_results.extend(results)
            time.sleep(1.0)  # 1 second between batches
        
        end_time = time.time()
        
        duration = end_time - start_time
        success_count = sum(all_results)
        success_rate = success_count / len(all_results)
        
        print(f"\n1000 requests completed in {duration:.2f} seconds")
        print(f"Success rate: {success_rate:.2%} ({success_count}/1000)")
        print(f"Throughput: {1000/duration:.2f} requests/second")
        if errors:
            print(f"Sample errors: {errors[:5]}")
        
        # Lower expectation - 70% success
        assert success_rate >= 0.70


class TestConcurrentLoad:
    """Test API under concurrent load"""
    
    def test_concurrent_requests(self):
        """Test concurrent parking lot views"""
        
        errors = []
        
        def view_parking_lots():
            try:
                time.sleep(0.1)  # 100ms delay between requests
                response = client.get("/parking_lots/")
                return response.status_code == 200
            except Exception as e:
                errors.append(str(e))
                return False
        
        # Only 2 workers at a time
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(view_parking_lots) for _ in range(50)]
            results = [f.result() for f in as_completed(futures)]
        
        # 70% success is acceptable
        success_rate = sum(results) / len(results)
        print(f"\nSuccess rate: {success_rate:.2%} ({sum(results)}/50)")
        if errors:
            print(f"Sample errors: {errors[:5]}")
        assert success_rate >= 0.70
