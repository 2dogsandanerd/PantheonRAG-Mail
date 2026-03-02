import subprocess
import platform
import psutil
from datetime import datetime

class AcceptanceTestReport:
    """Generates professional Acceptance Test Protocol (ATP) for customer handover."""
    
    def __init__(self):
        self.timestamp = datetime.now()
        self.system_info = self._gather_system_info()
        
    def _gather_system_info(self) -> dict:
        """Collect system specifications."""
        return {
            "hostname": platform.node(),
            "os": f"{platform.system()} {platform.release()}",
            "cpu": platform.processor(),
            "cpu_cores": psutil.cpu_count(logical=False),
            "cpu_threads": psutil.cpu_count(logical=True),
            "ram_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "ram_available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
            "disk_total_gb": round(psutil.disk_usage('/').total / (1024**3), 2),
            "disk_free_gb": round(psutil.disk_usage('/').free / (1024**3), 2),
        }
    
    def _parse_test_results(self, log_file: str) -> dict:
        """Parse test results from log file."""
        try:
            with open(log_file, 'r') as f:
                content = f.read()
                
            results = {
                "load_test": "PASSED" if "Load Test PASSED" in content else "FAILED",
                "endurance_test": "PASSED" if "Endurance Test PASSED" in content else "FAILED",
                "memory_test": "PASSED" if "Memory Leak Test PASSED" in content else "FAILED",
                "chaos_test": "PASSED" if "Chaos Test PASSED" in content else "FAILED",
            }
            
            all_passed = all(v == "PASSED" for v in results.values())
            results["overall"] = "PRODUCTION READY" if all_passed else "ISSUES DETECTED"
            
            return results
        except Exception as e:
            return {"error": str(e)}
    
    def generate_protocol(self, customer_name: str, test_log_file: str, output_file: str):
        """Generate Markdown ATP document."""
        
        test_results = self._parse_test_results(test_log_file)
        
        md = f"""# ACCEPTANCE TEST PROTOCOL (ATP)
## RAG System - Production Deployment

---

**Document Information:**
- **Customer:** {customer_name}
- **Date:** {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
- **Test Executor:** [Your Company Name]
- **System:** RAG Knowledge Base System

---

## 1. SYSTEM SPECIFICATIONS

| Component | Specification |
|-----------|---------------|
| **Hostname** | {self.system_info['hostname']} |
| **Operating System** | {self.system_info['os']} |
| **CPU** | {self.system_info['cpu']} |
| **CPU Cores/Threads** | {self.system_info['cpu_cores']} cores / {self.system_info['cpu_threads']} threads |
| **RAM Total** | {self.system_info['ram_total_gb']} GB |
| **RAM Available** | {self.system_info['ram_available_gb']} GB |
| **Disk Total** | {self.system_info['disk_total_gb']} GB |
| **Disk Free** | {self.system_info['disk_free_gb']} GB |

---

## 2. ACCEPTANCE TEST RESULTS

### 2.1 Load Test
**Result:** {'✅ PASSED' if test_results.get('load_test') == 'PASSED' else '❌ FAILED'}

- Purpose: Validate system under burst load
- Duration: 5 seconds, 20 concurrent users

### 2.2 Endurance Test
**Result:** {'✅ PASSED' if test_results.get('endurance_test') == 'PASSED' else '❌ FAILED'}

- Purpose: Long-running stability validation
- Duration: 500 requests over ~1 minute

### 2.3 Memory Leak Test
**Result:** {'✅ PASSED' if test_results.get('memory_test') == 'PASSED' else '❌ FAILED'}

- Purpose: Detect resource leaks
- Duration: 10 minutes continuous operation

### 2.4 Chaos Test
**Result:** {'✅ PASSED' if test_results.get('chaos_test') == 'PASSED' else '❌ FAILED'}

- Purpose: Resilience validation
- Scenario: Circuit breaker recovery

---

## 3. OVERALL ASSESSMENT

### System Status: **{test_results.get('overall', 'UNKNOWN')}**

{'✅ **System certified for production deployment.**' if test_results.get('overall') == 'PRODUCTION READY' else '⚠️ **Issues detected. Review required.**'}

---

## 4. SIGN-OFF

### Customer Acceptance

**Customer Representative:**

Name: ________________________________

Signature: ____________________________

Date: _________________________________

---

### Service Provider Confirmation

**Service Provider:**

Name: ________________________________

Signature: ____________________________

Date: _________________________________

---

**Detailed Logs:** `{test_log_file}`  
**Generated:** {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        with open(output_file, 'w') as f:
            f.write(md)
        
        print(f"✅ ATP generated: {output_file}")
        return output_file

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python3 generate_atp.py <customer_name> <test_log_file>")
        print("Example: python3 generate_atp.py 'ACME Corp' test_reports/test_report_*.log")
        sys.exit(1)
    
    customer_name = sys.argv[1]
    test_log_file = sys.argv[2]
    output_file = f"test_reports/ATP_{customer_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    atp = AcceptanceTestReport()
    atp.generate_protocol(customer_name, test_log_file, output_file)
    
    print(f"\n📄 Protocol ready for printing/signing!")
    print(f"   Convert to PDF: pandoc {output_file} -o {output_file.replace('.md', '.pdf')}")
