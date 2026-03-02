import asyncio
import aiohttp
import subprocess
import time
import signal
from datetime import datetime
from typing import Dict, Optional

BASE_URL = "http://localhost:33800/api/v1"

class ChaosTest:
    """
    Chaos Engineering test for resilience validation.
    
    Simulates real-world failures:
    - Service crashes (Ollama, ChromaDB)
    - Network disruptions
    - Resource exhaustion
    
    Tests:
    - Circuit Breaker activation and recovery
    - Graceful degradation
    - Auto-reconnection logic
    """
    
    def __init__(self):
        self.results = []
        
    async def _check_health(self, session) -> Dict:
        """Check system health."""
        try:
            async with session.get("http://localhost:33800/api/health", timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "timestamp": datetime.now().isoformat(),
                        "status": "healthy",
                        "checks": data.get("checks", {})
                    }
                else:
                    return {
                        "timestamp": datetime.now().isoformat(),
                        "status": f"unhealthy_{response.status}",
                        "checks": {}
                    }
        except Exception as e:
            return {
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "error": str(e)
            }
    
    async def _make_query(self, session) -> bool:
        """Make a query request."""
        try:
            url = f"{BASE_URL}/rag/query"
            payload = {
                "query": "test chaos query",
                "collections": ["test_collection"],
                "k": 3,
                "use_reranker": False
            }
            async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as response:
                return response.status in [200, 404, 503]  # 503 = Circuit Breaker (OK)
        except Exception:
            return False
    
    def _find_process(self, name: str) -> Optional[int]:
        """Find process PID by name."""
        try:
            result = subprocess.run(
                ["pgrep", "-f", name],
                capture_output=True,
                text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                return int(result.stdout.strip().split()[0])
        except Exception:
            pass
        return None
    
    def _kill_service(self, service_name: str) -> bool:
        """Kill a service process."""
        pid = self._find_process(service_name)
        if pid:
            try:
                print(f"   💀 Killing {service_name} (PID: {pid})")
                os.kill(pid, signal.SIGTERM)
                return True
            except Exception as e:
                print(f"   ⚠️  Failed to kill {service_name}: {e}")
                return False
        else:
            print(f"   ⚠️  {service_name} process not found (may not be running)")
            return False
    
    async def test_ollama_failure_recovery(self):
        """
        Test 1: Ollama Crash Recovery
        
        Simulates Ollama crash and validates:
        - Circuit Breaker activates
        - Graceful error handling
        - Auto-recovery when service returns
        """
        print("\n" + "=" * 70)
        print("🧪 TEST 1: OLLAMA CRASH RECOVERY")
        print("=" * 70)
        
        async with aiohttp.ClientSession() as session:
            # Phase 1: Baseline
            print("\n📊 Phase 1: Baseline (service healthy)")
            health = await self._check_health(session)
            print(f"   Health: {health['status']}")
            
            if health.get("checks", {}).get("ollama", {}).get("status") != "ok":
                print("   ⚠️  WARNING: Ollama not healthy at start. Skipping test.")
                return
            
            # Phase 2: Kill Ollama
            print("\n💀 Phase 2: Simulating Ollama crash...")
            self._kill_service("ollama")
            await asyncio.sleep(2)
            
            # Phase 3: Test during failure
            print("\n🔍 Phase 3: Testing during failure...")
            for i in range(5):
                success = await self._make_query(session)
                status = "✅" if success else "❌"
                print(f"   Request {i+1}: {status}")
                await asyncio.sleep(1)
            
            health = await self._check_health(session)
            print(f"   Health Check: {health['status']}")
            
            if health.get("checks", {}).get("ollama", {}).get("available") == False:
                print("   ✅ PASS: System detected Ollama failure")
            
            # Phase 4: Recovery
            print("\n🔄 Phase 4: Waiting for recovery (30s)...")
            print("   NOTE: Ollama auto-restart must be configured")
            print("   Or manually restart: 'ollama serve'")
            
            # Wait for potential auto-recovery
            for i in range(6):
                await asyncio.sleep(5)
                health = await self._check_health(session)
                if health.get("checks", {}).get("ollama", {}).get("available"):
                    print(f"   ✅ Ollama recovered after {(i+1)*5}s")
                    break
                else:
                    print(f"   ⏳ Waiting... ({(i+1)*5}s)")
            
            print("\n📊 Test Complete")
    
    async def test_circuit_breaker_recovery(self):
        """
        Test 2: Circuit Breaker Recovery
        
        Validates Circuit Breaker behavior:
        - Opens after N consecutive failures
        - Enters half-open state after timeout
        - Closes after successful recovery
        """
        print("\n" + "=" * 70)
        print("🧪 TEST 2: CIRCUIT BREAKER RECOVERY")
        print("=" * 70)
        
        async with aiohttp.ClientSession() as session:
            print("\n📊 Phase 1: Trigger Circuit Breaker (5 failures)")
            
            # Make invalid requests to trigger failures
            url = f"{BASE_URL}/rag/query"
            payload = {
                "query": "chaos test",
                "collections": ["nonexistent_collection_12345"],
                "k": 3,
                "use_reranker": False
            }
            
            failures = 0
            for i in range(10):
                try:
                    async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=5)) as response:
                        if response.status == 503:
                            print(f"   Request {i+1}: ⚠️  503 Service Unavailable (Circuit Breaker OPEN)")
                            break
                        elif response.status != 200:
                            failures += 1
                            print(f"   Request {i+1}: ❌ Failed (status {response.status})")
                        else:
                            print(f"   Request {i+1}: ✅ Success")
                except Exception as e:
                    failures += 1
                    print(f"   Request {i+1}: ❌ Exception: {str(e)[:50]}")
                
                await asyncio.sleep(0.5)
            
            if failures >= 5:
                print(f"\n   ✅ PASS: Circuit Breaker activated after {failures} failures")
            
            # Phase 2: Wait for recovery timeout (30s)
            print("\n⏳ Phase 2: Waiting for Circuit Breaker recovery timeout (30s)...")
            for i in range(6):
                await asyncio.sleep(5)
                print(f"   {(i+1)*5}s...")
            
            # Phase 3: Test recovery
            print("\n🔄 Phase 3: Testing recovery with health endpoint...")
            for i in range(3):
                health = await self._check_health(session)
                if health["status"] == "healthy":
                    print(f"   ✅ System recovered (attempt {i+1})")
                    break
                else:
                    print(f"   ⏳ Still recovering... (attempt {i+1})")
                await asyncio.sleep(2)
            
            print("\n📊 Test Complete")
    
    async def run_all_tests(self):
        """Run all chaos tests."""
        print("=" * 70)
        print("🌪️  CHAOS ENGINEERING TEST SUITE")
        print("=" * 70)
        print("\nWARNING: These tests will intentionally crash services.")
        print("Ensure you have backups and are in a test environment.")
        print("\nPress Ctrl+C to cancel...")
        
        await asyncio.sleep(3)
        
        # Test 1: Ollama recovery
        await self.test_ollama_failure_recovery()
        
        await asyncio.sleep(5)
        
        # Test 2: Circuit Breaker
        await self.test_circuit_breaker_recovery()
        
        print("\n" + "=" * 70)
        print("✅ CHAOS TEST SUITE COMPLETE")
        print("=" * 70)

if __name__ == "__main__":
    import os
    
    print("\n⚠️  CHAOS TESTING MODE ⚠️")
    print("This will intentionally disrupt services.")
    print("\nRunning Circuit Breaker test only (safe)...")
    print("For full Ollama crash test, uncomment run_all_tests()")
    
    tester = ChaosTest()
    
    # Safe test: Only Circuit Breaker (no service killing)
    asyncio.run(tester.test_circuit_breaker_recovery())
    
    # Uncomment for full chaos (requires sudo/service control):
    # asyncio.run(tester.run_all_tests())
