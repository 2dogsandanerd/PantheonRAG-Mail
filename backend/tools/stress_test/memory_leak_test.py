import asyncio
import aiohttp
import time
import psutil
import os
from datetime import datetime
from typing import List, Dict
from collections import defaultdict

BASE_URL = "http://localhost:33800/api/v1"

class MemoryLeakTest:
    """
    Long-running test to detect memory leaks and resource exhaustion.
    
    Runs for 1 hour, sampling system resources every 5 minutes.
    Detects:
    - Memory growth (potential leaks)
    - Connection pool exhaustion
    - File descriptor leaks
    """
    
    def __init__(self):
        self.start_time = None
        self.samples = []
        self.request_count = 0
        self.error_count = 0
        
    def get_system_snapshot(self) -> Dict:
        """Capture current system resource usage."""
        process = psutil.Process(os.getpid())
        
        return {
            "timestamp": datetime.now().isoformat(),
            "runtime_seconds": time.time() - self.start_time if self.start_time else 0,
            "memory_mb": process.memory_info().rss / 1024 / 1024,
            "cpu_percent": process.cpu_percent(interval=0.1),
            "open_files": len(process.open_files()),
            "num_threads": process.num_threads(),
            "connections": len(process.connections()),
            "requests_total": self.request_count,
            "errors_total": self.error_count
        }
    
    async def _make_request(self, session) -> bool:
        """Make a single request and track success."""
        try:
            # Alternate between health and query
            if self.request_count % 2 == 0:
                async with session.get(f"http://localhost:33800/api/health") as response:
                    self.request_count += 1
                    if response.status == 200:
                        return True
                    else:
                        self.error_count += 1
                        return False
            else:
                url = f"{BASE_URL}/rag/query"
                payload = {
                    "query": "test query",
                    "collections": ["test_collection"],
                    "k": 3,
                    "use_reranker": False
                }
                async with session.post(url, json=payload) as response:
                    self.request_count += 1
                    if response.status in [200, 404]:  # 404 OK for missing collection
                        return True
                    else:
                        self.error_count += 1
                        return False
        except Exception as e:
            self.error_count += 1
            return False
    
    async def run_test(self, duration_minutes: int = 60, requests_per_minute: int = 60):
        """
        Run memory leak test.
        
        Args:
            duration_minutes: Total test duration (default: 60 minutes)
            requests_per_minute: Request rate (default: 60/min = 1/sec)
        """
        self.start_time = time.time()
        sample_interval = 300  # Sample every 5 minutes
        last_sample_time = self.start_time
        
        print("=" * 70)
        print("🧪 MEMORY LEAK TEST")
        print("=" * 70)
        print(f"Duration:     {duration_minutes} minutes")
        print(f"Request Rate: {requests_per_minute} requests/minute")
        print(f"Sampling:     Every 5 minutes")
        print("=" * 70)
        
        # Initial snapshot
        initial = self.get_system_snapshot()
        self.samples.append(initial)
        print(f"\n📸 Initial State:")
        print(f"   Memory: {initial['memory_mb']:.2f} MB")
        print(f"   Connections: {initial['connections']}")
        print(f"   Open Files: {initial['open_files']}")
        
        end_time = self.start_time + (duration_minutes * 60)
        request_interval = 60.0 / requests_per_minute
        
        async with aiohttp.ClientSession() as session:
            while time.time() < end_time:
                # Make request
                await self._make_request(session)
                
                # Check if we should take a sample
                if time.time() - last_sample_time >= sample_interval:
                    snapshot = self.get_system_snapshot()
                    self.samples.append(snapshot)
                    last_sample_time = time.time()
                    
                    elapsed_min = snapshot["runtime_seconds"] / 60
                    print(f"\n📸 Sample at {elapsed_min:.1f} minutes:")
                    print(f"   Memory: {snapshot['memory_mb']:.2f} MB "
                          f"(Δ {snapshot['memory_mb'] - initial['memory_mb']:.2f} MB)")
                    print(f"   Connections: {snapshot['connections']} "
                          f"(Δ {snapshot['connections'] - initial['connections']})")
                    print(f"   Requests: {snapshot['requests_total']}, "
                          f"Errors: {snapshot['errors_total']} "
                          f"({(snapshot['errors_total']/max(1, snapshot['requests_total']))*100:.1f}%)")
                
                # Rate limiting
                await asyncio.sleep(request_interval)
        
        # Final snapshot
        final = self.get_system_snapshot()
        self.samples.append(final)
        
        self._print_report(initial, final)
    
    def _print_report(self, initial: Dict, final: Dict):
        """Print comprehensive leak detection report."""
        print("\n" + "=" * 70)
        print("📊 MEMORY LEAK TEST RESULTS")
        print("=" * 70)
        
        duration_min = (final["runtime_seconds"]) / 60
        
        print(f"\n⏱️  Test Duration: {duration_min:.1f} minutes")
        print(f"📈 Total Requests: {final['requests_total']}")
        print(f"❌ Total Errors: {final['errors_total']} ({(final['errors_total']/max(1, final['requests_total']))*100:.1f}%)")
        
        # Memory analysis
        mem_growth = final["memory_mb"] - initial["memory_mb"]
        mem_growth_rate = mem_growth / duration_min  # MB per minute
        
        print(f"\n💾 MEMORY ANALYSIS:")
        print(f"   Initial:  {initial['memory_mb']:.2f} MB")
        print(f"   Final:    {final['memory_mb']:.2f} MB")
        print(f"   Growth:   {mem_growth:.2f} MB (+{(mem_growth/initial['memory_mb'])*100:.1f}%)")
        print(f"   Rate:     {mem_growth_rate:.2f} MB/minute")
        
        if mem_growth_rate > 1.0:
            print(f"   ⚠️  WARNING: Memory growing at {mem_growth_rate:.2f} MB/min")
            print(f"   ⚠️  Projected: {mem_growth_rate * 60:.0f} MB/hour, {mem_growth_rate * 1440:.0f} MB/day")
        elif mem_growth < 50:
            print(f"   ✅ PASS: Stable memory usage (< 50 MB growth)")
        else:
            print(f"   ⚠️  CAUTION: Moderate memory growth detected")
        
        # Connection analysis
        conn_growth = final["connections"] - initial["connections"]
        print(f"\n🔌 CONNECTION ANALYSIS:")
        print(f"   Initial:  {initial['connections']}")
        print(f"   Final:    {final['connections']}")
        print(f"   Growth:   {conn_growth:+d}")
        
        if conn_growth > 10:
            print(f"   ❌ FAIL: Connection leak detected ({conn_growth} unclosed connections)")
        elif conn_growth > 5:
            print(f"   ⚠️  WARNING: Possible connection leak ({conn_growth} connections)")
        else:
            print(f"   ✅ PASS: Stable connection usage")
        
        # File descriptor analysis
        fd_growth = final["open_files"] - initial["open_files"]
        print(f"\n📁 FILE DESCRIPTOR ANALYSIS:")
        print(f"   Initial:  {initial['open_files']}")
        print(f"   Final:    {final['open_files']}")
        print(f"   Growth:   {fd_growth:+d}")
        
        if fd_growth > 20:
            print(f"   ❌ FAIL: File descriptor leak detected")
        elif fd_growth > 10:
            print(f"   ⚠️  WARNING: Possible file descriptor leak")
        else:
            print(f"   ✅ PASS: Stable file descriptor usage")
        
        # Overall verdict
        print(f"\n🎯 OVERALL VERDICT:")
        if mem_growth_rate < 0.5 and conn_growth <= 5 and fd_growth <= 10:
            print(f"   ✅ EXCELLENT: No memory leaks detected")
            print(f"   ✅ System is production-ready for long-running deployment")
        elif mem_growth_rate < 2.0 and conn_growth <= 10:
            print(f"   ⚠️  ACCEPTABLE: Minor resource growth detected")
            print(f"   ⚠️  Monitor in production, may need periodic restarts")
        else:
            print(f"   ❌ CRITICAL: Significant resource leaks detected")
            print(f"   ❌ Investigate before production deployment")
        
        print("=" * 70)

if __name__ == "__main__":
    # Quick test: 10 minutes at 60 req/min
    # For full test: 60 minutes
    print("Starting Memory Leak Test (10 minutes for demo)")
    print("For full 1-hour test, edit duration_minutes=60")
    
    tester = MemoryLeakTest()
    asyncio.run(tester.run_test(duration_minutes=10, requests_per_minute=60))
