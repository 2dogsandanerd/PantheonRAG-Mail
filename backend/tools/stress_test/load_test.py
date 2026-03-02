import asyncio
import aiohttp
import time
import sys
import os
import random
from typing import List
from statistics import mean, median

# Add parent dir to path to import generator
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from generator import DataGenerator

BASE_URL = "http://localhost:33800/api/v1"

class StressTester:
    """
    Runs load tests against the RAG API.
    """
    
    def __init__(self, concurrent_users: int = 10):
        self.concurrent_users = concurrent_users
        self.generator = DataGenerator()
        
    async def _ingest_file(self, session, file_path: str) -> dict:
        """Upload a single file."""
        start = time.time()
        # Correct path: /api/v1/rag/analyze-files (no 'ingestion' prefix in router)
        url = f"{BASE_URL}/rag/analyze-files" 
        
        # Mocking the multipart upload for simplicity in this script
        # In a real heavy test, we would use the full batch endpoint
        # Here we just check if the API responds under load
        
        try:
            # We use the health endpoint for pure throughput testing if auth is complex
            # Or the actual ingest if we have a token. 
            # For this 'quick' stress test, we hit the health check hard to test server concurrency
            # and the analyze endpoint with a small payload.
            
            # The analyze endpoint expects a list of FilePreview objects
            payload = {
                "files": [
                    {
                        "path": file_path,
                        "preview": "This is a dummy preview content for stress testing.",
                        "mime_type": "application/pdf"
                    }
                ]
            }
            
            # Note: This requires the backend to be running!
            async with session.post(url, json=payload) as response:
                duration = time.time() - start
                status = response.status
                return {"status": status, "duration": duration, "endpoint": "analyze"}
                
        except Exception as e:
            return {"status": "error", "duration": time.time() - start, "error": str(e)}

    async def _query_rag(self, session, query: str) -> dict:
        """Run a search query."""
        start = time.time()
        # Correct path: /api/v1/rag/query (not /search)
        url = f"{BASE_URL}/rag/query"
        
        payload = {
            "query": query,
            "collections": ["test_collection"], # Changed from collection_name to collections list
            "k": 3,
            "use_reranker": False # Disable reranker for speed in stress test
        }
        
        try:
            async with session.post(url, json=payload) as response:
                duration = time.time() - start
                return {"status": response.status, "duration": duration, "endpoint": "query"}
        except Exception as e:
            return {"status": "error", "duration": time.time() - start, "error": str(e)}

    async def run_load_test(self, duration_seconds: int = 10):
        """Run the stress test."""
        print(f"🚀 Starting Stress Test ({self.concurrent_users} users, {duration_seconds}s)...")
        
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            tasks = []
            results = []
            
            while time.time() - start_time < duration_seconds:
                # Create a batch of concurrent requests
                batch = []
                for _ in range(self.concurrent_users):
                    # Mix of queries and health checks
                    if random.random() > 0.5:
                        batch.append(self._query_rag(session, "test query " + str(random.randint(1,100))))
                    else:
                        # Simple health check spam to test server responsiveness
                        batch.append(session.get(f"http://localhost:33800/api/health"))
                
                # Fire!
                batch_results = await asyncio.gather(*batch, return_exceptions=True)
                
                # Process results
                for res in batch_results:
                    if isinstance(res, aiohttp.ClientResponse):
                        results.append({"status": res.status, "duration": 0.1, "endpoint": "health"})
                    elif isinstance(res, dict):
                        results.append(res)
                    else:
                        results.append({"status": "error", "duration": 0, "error": str(res)})
                
                # Small sleep to prevent total DOS of local machine
                await asyncio.sleep(0.1)
                
            self._print_report(results)

    def _print_report(self, results: List[dict]):
        """Print nice stats."""
        total = len(results)
        errors = len([r for r in results if r.get("status") != 200])
        durations = [r["duration"] for r in results if "duration" in r]
        
        print("\n📊 Stress Test Report")
        print("======================")
        print(f"Total Requests: {total}")
        print(f"Successful:     {total - errors}")
        print(f"Failed:         {errors}")
        print(f"Error Rate:     {(errors/total)*100:.2f}%")
        
        if durations:
            print(f"Avg Latency:    {mean(durations)*1000:.2f} ms")
            print(f"P95 Latency:    {sorted(durations)[int(len(durations)*0.95)]*1000:.2f} ms")
        
        if errors > 0:
            print("\n⚠️  System is sweating! (Errors detected)")
            
            # Analyze errors
            error_msgs = [r.get("error", f"Status {r.get('status')}") for r in results if r.get("status") != 200]
            from collections import Counter
            common_errors = Counter(error_msgs).most_common(5)
            
            print("\nTop Errors:")
            for err, count in common_errors:
                print(f"  - {err}: {count} times")
        else:
            print("\n✅ System is rock solid.")

if __name__ == "__main__":
    tester = StressTester(concurrent_users=20)
    asyncio.run(tester.run_load_test(duration_seconds=5))
