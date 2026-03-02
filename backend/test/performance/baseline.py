"""Baseline performance measurements before optimization."""

import pytest
import time
import psutil
import asyncio
from pathlib import Path
import tempfile
from memory_profiler import profile


def create_realistic_pdf(path: Path, size_kb: int):
    """
    Creates a realistic PDF with text to better simulate parsing load.
    Requires `pip install fpdf2`.
    """
    from fpdf import FPDF
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Add text until the desired size is approximated
    text = "This is a sample line for the performance test PDF. " * 10
    
    while True:
        pdf.multi_cell(0, 10, text)
        pdf.output(path) # Write to file
        if path.stat().st_size >= size_kb * 1024:
            break
            
    final_size = path.stat().st_size / 1024
    print(f"Created realistic PDF: {path} ({final_size:.2f} KB)")


@pytest.mark.benchmark
class TestIngestionBaseline:
    """Baseline for ingestion performance."""

    @pytest.mark.asyncio
    async def test_single_file_ingestion_baseline(self, async_test_client, benchmark):
        """Measure single file ingestion (1MB PDF)."""
        
        # Create a realistic 1MB test PDF to include parsing performance
        test_pdf = Path("test_data/test_1mb.pdf")
        if not test_pdf.exists() or test_pdf.stat().st_size < 1024 * 1024:
            test_pdf.parent.mkdir(exist_ok=True)
            create_realistic_pdf(test_pdf, 1024)
        
        def ingestion_test():
            """Sync function for benchmarking."""
            import requests
            import time
            start_time = time.time()
            
            with open(test_pdf, "rb") as f:
                response = requests.post(
                    "http://localhost:33800/api/v1/rag/documents/upload",
                    data={"collection": "test_baseline"},
                    files={"files": ("test_1mb.pdf", f)}
                )
            
            return time.time() - start_time, response.status_code
        
        duration, status = benchmark.pedantic(
            ingestion_test,
            rounds=3,
            iterations=1
        )
        
        print(f"Single file ingestion baseline: {duration:.2f}s, status: {status}")
        assert status == 200

    @pytest.mark.asyncio
    async def test_batch_ingestion_baseline(self, async_test_client, benchmark):
        """Measure batch ingestion (10 files)."""
        
        def batch_ingestion_test():
            """Sync function for benchmarking."""
            import requests
            import time
            import os
            from pathlib import Path
            
            start_time = time.time()
            
            # Create multiple realistic test files
            files_to_upload = []
            test_files = []
            for i in range(10):
                test_file = Path(f"test_data/test_file_{i}.pdf")
                if not test_file.exists() or test_file.stat().st_size < 500 * 1024:
                    test_file.parent.mkdir(exist_ok=True)
                    create_realistic_pdf(test_file, 500)
                
                test_files.append(test_file)
                files_to_upload.append(("files", open(test_file, "rb")))
            
            try:
                response = requests.post(
                    "http://localhost:33800/api/v1/rag/documents/upload",
                    data={"collection": "test_baseline", "async_mode": "true"},
                    files=files_to_upload
                )
                
                duration = time.time() - start_time
                return duration, response.status_code
            finally:
                # Close file handles
                for _, file_obj in files_to_upload:
                    file_obj.close()

        duration, status = benchmark.pedantic(
            batch_ingestion_test,
            rounds=3,
            iterations=1
        )
        
        print(f"Batch ingestion baseline (10 files): {duration:.2f}s, status: {status}")
        assert status == 200


@pytest.mark.benchmark
class TestQueryBaseline:
    """Baseline for query performance."""

    @pytest.mark.asyncio
    async def test_simple_query_baseline(self, async_test_client, benchmark):
        """Measure simple vector query (k=5)."""
        
        def query_test():
            import requests
            import time
            start_time = time.time()
            
            response = requests.post(
                "http://localhost:33800/api/v1/rag/query",
                json={"query": "test query for baseline", "collection": "test", "k": 5}
            )
            
            return time.time() - start_time, response.status_code
        
        duration, status = benchmark.pedantic(
            query_test,
            rounds=10,
            iterations=1
        )
        
        avg_duration = duration
        print(f"Simple query baseline: {avg_duration*1000:.0f}ms, status: {status}")

    @pytest.mark.asyncio
    async def test_batch_query_baseline(self, async_test_client, benchmark):
        """Measure multiple queries over time."""
        
        queries = ["query 1", "query 2", "query 3", "query 4", "query 5"]
        
        def batch_query_test():
            import requests
            import time
            start_time = time.time()
            
            for query in queries:
                response = requests.post(
                    "http://localhost:33800/api/v1/rag/query",
                    json={"query": query, "collection": "test", "k": 5}
                )
            
            return time.time() - start_time, len(queries)
        
        duration, query_count = benchmark.pedantic(
            batch_query_test,
            rounds=5,
            iterations=1
        )
        
        avg_per_query = (duration / query_count) * 1000
        print(f"Batch query baseline: {avg_per_query:.0f}ms per query")


@pytest.mark.benchmark
class TestResourceUsageBaseline:
    """Baseline for resource usage."""

    def test_memory_usage_baseline(self):
        """Measure current memory usage."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024
        
        print(f"Current memory usage baseline: {memory_mb:.2f} MB")
        return memory_mb

    def test_cpu_usage_baseline(self):
        """Measure current CPU usage."""
        import psutil
        import time
        
        cpu_percent = psutil.cpu_percent(interval=1)
        print(f"Current CPU usage baseline: {cpu_percent}%")
        return cpu_percent
