import asyncio
import aiohttp
import time
import sys
import os
import random
from typing import List, Dict
from statistics import mean
from collections import defaultdict

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

BASE_URL = "http://localhost:33800/api/v1"

class EnduranceTest:
    """
    Long-running endurance test with detailed error tracking.
    
    Designed to:
    1. Capture real errors (before Circuit Breaker opens)
    2. Allow Circuit Breaker recovery between batches
    3. Test system stability over extended periods
    """
    
    def __init__(self, concurrent_users: int = 5, batch_size: int = 50):
        self.concurrent_users = concurrent_users
        self.batch_size = batch_size
        self.all_results = []
        self.error_details = defaultdict(list)  # Store full error responses
        
    async def _call_health(self, session) -> Dict:
        """Simple health check."""
        start = time.time()
        try:
            async with session.get(f"http://localhost:33800/api/health") as response:
                duration = time.time() - start
                body = await response.text()
                return {
                    "status": response.status,
                    "duration": duration,
                    "endpoint": "health",
                    "body": body if response.status != 200 else None
                }
        except Exception as e:
            return {
                "status": "error",
                "duration": time.time() - start,
                "error": str(e),
                "endpoint": "health"
            }
    
    async def _call_query(self, session, query: str) -> Dict:
        """Query endpoint with detailed error capture."""
        start = time.time()
        url = f"{BASE_URL}/rag/query"
        
        payload = {
            "query": query,
            "collections": ["test_collection"],
            "k": 3,
            "use_reranker": False
        }
        
        try:
            async with session.post(url, json=payload) as response:
                duration = time.time() - start
                body = await response.text()
                
                result = {
                    "status": response.status,
                    "duration": duration,
                    "endpoint": "query"
                }
                
                # Capture error details
                if response.status != 200:
                    result["body"] = body[:500]  # First 500 chars
                    
                return result
        except Exception as e:
            return {
                "status": "error",
                "duration": time.time() - start,
                "error": str(e),
                "endpoint": "query"
            }
    
    async def run_batch(self, session, batch_num: int) -> List[Dict]:
        """Run one batch of concurrent requests."""
        print(f"\n🔹 Batch {batch_num}: Firing {self.batch_size} requests...")
        
        tasks = []
        for _ in range(self.batch_size):
            if random.random() > 0.3:  # 70% health checks, 30% queries
                tasks.append(self._call_health(session))
            else:
                tasks.append(self._call_query(session, f"test query {random.randint(1, 100)}"))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        processed = []
        for res in results:
            if isinstance(res, dict):
                processed.append(res)
                
                # Store error details
                if res.get("status") != 200:
                    error_key = f"Status {res.get('status')}"
                    if "body" in res:
                        self.error_details[error_key].append(res["body"])
            else:
                processed.append({
                    "status": "exception",
                    "error": str(res),
                    "duration": 0
                })
        
        return processed
    
    async def run_endurance_test(self, num_batches: int = 10, pause_between_batches: int = 5):
        """
        Run endurance test with multiple batches.
        
        Args:
            num_batches: Number of batches to run
            pause_between_batches: Seconds to wait between batches (for Circuit Breaker recovery)
        """
        print(f"🚀 Starting Endurance Test")
        print(f"   Batches: {num_batches}")
        print(f"   Requests per batch: {self.batch_size}")
        print(f"   Pause between batches: {pause_between_batches}s")
        print(f"   Total requests: {num_batches * self.batch_size}")
        print("=" * 60)
        
        async with aiohttp.ClientSession() as session:
            for batch_num in range(1, num_batches + 1):
                # Run batch
                batch_results = await self.run_batch(session, batch_num)
                self.all_results.extend(batch_results)
                
                # Quick stats
                batch_errors = len([r for r in batch_results if r.get("status") != 200])
                print(f"   ✓ Completed: {len(batch_results)} requests, {batch_errors} errors")
                
                # Pause between batches (except after last one)
                if batch_num < num_batches:
                    print(f"   ⏸️  Pausing {pause_between_batches}s for Circuit Breaker recovery...")
                    await asyncio.sleep(pause_between_batches)
        
        self._print_report()
    
    def _print_report(self):
        """Print comprehensive test report."""
        total = len(self.all_results)
        errors = len([r for r in self.all_results if r.get("status") != 200])
        durations = [r["duration"] for r in self.all_results if "duration" in r and r["duration"] > 0]
        
        print("\n" + "=" * 60)
        print("📊 ENDURANCE TEST REPORT")
        print("=" * 60)
        print(f"Total Requests:  {total}")
        print(f"Successful:      {total - errors}")
        print(f"Failed:          {errors}")
        print(f"Error Rate:      {(errors/total)*100:.2f}%")
        
        if durations:
            print(f"\nLatency Stats:")
            print(f"  Avg:  {mean(durations)*1000:.2f} ms")
            print(f"  Min:  {min(durations)*1000:.2f} ms")
            print(f"  Max:  {max(durations)*1000:.2f} ms")
            print(f"  P95:  {sorted(durations)[int(len(durations)*0.95)]*1000:.2f} ms")
        
        # Error breakdown
        if errors > 0:
            print(f"\n⚠️  ERROR BREAKDOWN:")
            error_counts = defaultdict(int)
            for r in self.all_results:
                if r.get("status") != 200:
                    error_counts[str(r.get("status"))] += 1
            
            for error_type, count in sorted(error_counts.items(), key=lambda x: -x[1]):
                print(f"  - {error_type}: {count} times")
            
            # Show first unique error messages
            print(f"\n🔍 FIRST ERROR SAMPLES:")
            shown = set()
            for error_type, bodies in list(self.error_details.items())[:3]:
                if bodies and bodies[0] not in shown:
                    print(f"\n  {error_type}:")
                    print(f"  {bodies[0][:200]}")
                    shown.add(bodies[0])
        else:
            print("\n✅ PERFECT RUN - No errors detected!")
        
        print("=" * 60)

if __name__ == "__main__":
    # Run endurance test
    # 10 batches × 50 requests = 500 total requests
    # 5s pause between batches = Circuit Breaker has time to recover
    tester = EnduranceTest(concurrent_users=5, batch_size=50)
    asyncio.run(tester.run_endurance_test(num_batches=10, pause_between_batches=5))
