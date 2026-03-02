# RAG System Test Suite

**Professional testing toolkit for production deployment validation.**

This test suite validates the stability, performance, and resilience of the RAG system under various load conditions and failure scenarios.

---

## 📋 Test Overview

| Test Type | File | Purpose | Duration |
|-----------|------|---------|----------|
| **Load Test** | `load_test.py` | High-concurrency burst testing | 5-10s |
| **Endurance Test** | `endurance_test.py` | Long-running stability validation | 1-5 min |
| **System Health Check** | `system_check.py` | Pre-deployment validation | < 1s |

---

## 🚀 Quick Start

### Run Complete Test Suite (Recommended)

```bash
# Run all tests and generate report
./run_all_tests.sh
```

This will:
- ✅ Run all 4 tests sequentially
- ✅ Generate timestamped report (`test_reports/test_report_YYYYMMDD_HHMMSS.log`)
- ✅ Create summary file with pass/fail status
- ✅ Display final verdict (Production Ready / Not Ready)

**Expected Runtime:** ~15 minutes (10 min for memory test)

---

### Run Individual Tests

```bash
# Install dependencies first
pip install aiohttp fpdf psutil

# Quick load test (5 seconds)
python3 load_test.py

# Endurance test (recommended for production validation)
python3 endurance_test.py

# Memory leak test (10 minutes)
python3 memory_leak_test.py

# Chaos test (Circuit Breaker validation)
python3 chaos_test.py
```

---

## 📊 Test Details

### 1. Load Test (`load_test.py`)

**Purpose:** Validate system behavior under high-concurrency bursts.

**What it does:**
- Fires 20 concurrent users for 5 seconds
- Mix of `/api/health` and `/rag/query` requests
- Tests Circuit Breaker activation under stress

**Expected Results:**
- ✅ **Good:** 0-10% error rate, avg latency < 100ms
- ⚠️ **Warning:** 10-30% error rate, latency spikes to 500ms
- ❌ **Critical:** 50%+ error rate (Circuit Breaker open)

**Interpretation:**
```
Total Requests: 780
Successful:     780
Failed:         0
Error Rate:     0.00%
Avg Latency:    56.85 ms
```
→ **System is stable** under burst load.

If you see `Status 503` errors:
- Circuit Breaker activated (normal safety mechanism)
- Underlying service (ChromaDB/Ollama) may be overloaded
- Check backend logs for root cause

---

### 2. Endurance Test (`endurance_test.py`)

**Purpose:** Validate long-running stability and Circuit Breaker recovery.

**What it does:**
- Runs 10 batches of 50 requests each (500 total)
- 5-second pause between batches (allows Circuit Breaker recovery)
- Captures detailed error messages

**Expected Results:**
- ✅ **Excellent:** 0% error rate across all batches
- ✅ **Good:** < 5% error rate, consistent across batches
- ⚠️ **Warning:** 10-20% error rate, degrading over time
- ❌ **Critical:** Error rate increases with each batch (memory leak suspected)

**What to watch for:**

1. **Consistent errors across batches:**
   ```
   Batch 1: 0 errors ✅
   Batch 2: 0 errors ✅
   Batch 3: 0 errors ✅
   ```
   → System is stable over time

2. **Increasing errors (Memory leak warning):**
   ```
   Batch 1: 2 errors
   Batch 5: 15 errors
   Batch 10: 45 errors ⚠️
   ```
   → Investigate memory usage, connection pool leaks

3. **Error Details:**
   The test shows first error samples:
   ```
   🔍 FIRST ERROR SAMPLES:
   Status 500:
   {"detail": "Collection 'test_collection' not found"}
   ```
   → Missing test collection (expected for demo)

---

### 3. System Health Check (`system_check.py`)

**Purpose:** Pre-deployment validation of infrastructure.

**What it checks:**
- ✅ Disk space (minimum 2 GB required)
- ✅ Ollama availability and loaded models
- ✅ Write permissions for `./data` directory

**Example output:**
```python
from system_check import SystemHealthCheck

# Check disk space
disk_status = SystemHealthCheck.check_disk_space()
# {"status": "ok", "free_gb": 450.5, "message": "Free space: 450.5 GB"}

# Check Ollama
ollama_status = await SystemHealthCheck.check_ollama()
# {"status": "ok", "available": True, "models": ["llama3", "mistral"], "count": 2}

# Check permissions
perm_status = SystemHealthCheck.check_permissions(["./data"])
# {"status": "ok", "details": {"./data": "ok"}}
```

---

## 🔧 Integration with `/api/health`

The system health checks are integrated into the main API health endpoint:

```bash
curl http://localhost:33800/api/health
```

**Response:**
```json
{
  "status": "healthy",
  "checks": {
    "api": "ok",
    "disk": {
      "status": "ok",
      "free_gb": 450.5,
      "message": "Free space: 450.5 GB"
    },
    "ollama": {
      "status": "ok",
      "available": true,
      "models": ["llama3", "nomic-embed-text"],
      "count": 2
    },
    "permissions": {
      "status": "ok",
      "details": {"./data": "ok"}
    }
  }
}
```

---

## 🎯 Production Deployment Checklist

Before deploying to production, ensure:

- [ ] **Endurance test passes** with 0% error rate
- [ ] **Health check** returns `"status": "healthy"`
- [ ] **Disk space** > 10 GB free (for vector storage growth)
- [ ] **Ollama models** loaded and accessible
- [ ] **Circuit Breaker** tested and functional (run load test)
- [ ] **Backend logs** clean (no recurring errors)

---

## 🐛 Troubleshooting

### Common Issues

**1. `Status 404` errors**
- **Cause:** API endpoint mismatch
- **Fix:** Check `BASE_URL` in test scripts

**2. `Status 503` (Circuit Breaker Open)**
- **Cause:** Underlying service failing repeatedly
- **Check:** Backend logs for root cause (ChromaDB/Ollama)
- **Fix:** Ensure services are running and healthy

**3. `TypeError: unexpected keyword argument`**
- **Cause:** API/Service interface mismatch
- **Fix:** Restart backend after code changes

**4. High latency (> 500ms)**
- **Cause:** Cold start, slow embeddings, or overloaded ChromaDB
- **Check:** Ollama model loaded, ChromaDB responsive
- **Optimize:** Enable query caching, use faster embedding models

---

## 📈 Advanced: Chaos Testing

### Simulate Service Failures

Test Circuit Breaker recovery by stopping services mid-test:

```bash
# Terminal 1: Run endurance test
python3 endurance_test.py

# Terminal 2: Kill Ollama during test
pkill -f ollama
# Wait 10 seconds
ollama serve
```

**Expected behavior:**
- Circuit Breaker opens (503 errors)
- After 30s recovery timeout → Circuit Breaker attempts recovery
- Once Ollama back → System recovers

---

## 📝 Test Results Archive

For auditing and compliance, save test results:

```bash
# Run test and save output
python3 endurance_test.py > test_results_$(date +%Y%m%d_%H%M%S).log
```

---

## 🤝 Support

For questions or issues, contact the development team.

**Test Suite Version:** 1.0  
**Last Updated:** 2024-11-24
