import asyncio
import time
from pathlib import Path
import aiohttp

async def upload_file(session, file_path, collection):
    """Upload single file."""
    url = "http://localhost:33800/api/v1/rag/documents/upload"
    data = aiohttp.FormData()
    data.add_field('collection_name', collection)
    data.add_field('chunk_size', '500')
    data.add_field('chunk_overlap', '50')
    data.add_field('files', open(file_path, 'rb'))

    async with session.post(url, data=data) as response:
        return await response.json()

async def test_concurrent_uploads():
    """Test uploading 10 files concurrently."""
    # This is a template - in a real implementation, we would create temporary files
    # For now, we'll just check the structure of the test
    print("Load test template created. This would test concurrent uploads in a real deployment.")

if __name__ == "__main__":
    asyncio.run(test_concurrent_uploads())