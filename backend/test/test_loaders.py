"""
Unit tests for JSON and XML loaders
"""
import tempfile
import json
from pathlib import Path
import xml.etree.ElementTree as ET

def test_json_loader():
    """Test the JSON loader functionality"""
    from src.services.loaders.json_loader import JSONLoader
    
    # Create a temporary JSON file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
        json_data = {
            "users": [
                {"id": 1, "name": "John", "email": "john@example.com"},
                {"id": 2, "name": "Jane", "email": "jane@example.com"}
            ],
            "settings": {
                "theme": "dark",
                "notifications": True
            }
        }
        json.dump(json_data, temp_file)
        temp_file.flush()
        
        # Test the loader
        loader = JSONLoader(temp_file.name)
        documents = loader.load()
        
        # Verify results
        assert len(documents) >= 2  # Should have at least 2 documents (users array items)
        assert documents[0].metadata['type'] in ['json_array_item', 'json_object_item']
        assert 'John' in documents[0].text or 'Jane' in documents[1].text
        
        print("✅ JSON Loader test passed")
    
    # Clean up
    Path(temp_file.name).unlink()

def test_xml_loader():
    """Test the XML loader functionality"""
    from src.services.loaders.xml_loader import XMLLoader
    
    # Create a temporary XML file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as temp_file:
        xml_content = """<?xml version="1.0"?>
        <catalog>
            <book id="1">
                <title>Python Guide</title>
                <author>John Doe</author>
                <price>29.99</price>
            </book>
            <book id="2">
                <title>JavaScript Basics</title>
                <author>Jane Smith</author>
                <price>24.99</price>
            </book>
        </catalog>"""
        temp_file.write(xml_content)
        temp_file.flush()
        
        # Test the loader
        loader = XMLLoader(temp_file.name)
        documents = loader.load()
        
        # Verify results
        assert len(documents) >= 2  # Should have documents for each book
        assert documents[0].metadata['type'] in ['xml_item', 'xml_document']
        assert 'Python Guide' in documents[0].text or 'JavaScript Basics' in documents[1].text
        
        print("✅ XML Loader test passed")
    
    # Clean up
    Path(temp_file.name).unlink()

def run_all_tests():
    """Run all loader tests"""
    print("Testing JSON and XML loaders...")
    test_json_loader()
    test_xml_loader()
    print("All loader tests passed! ✅")

if __name__ == "__main__":
    run_all_tests()