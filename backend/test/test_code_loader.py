"""
Tests for CodeLoader (Phase 10b).

Tests cover:
- Code file loading (Python, JS, TS, Java, etc.)
- Function/Class detection
- Code-aware splitting
- Metadata extraction
- Fallback splitting for unknown languages
"""

import pytest
import tempfile
from pathlib import Path
from src.services.loaders.code_loader import CodeLoader


class TestCodeLoader:
    """Test suite for CodeLoader."""

    def test_load_python_file_with_functions(self):
        """Test loading Python file with function-based splitting."""
        python_code = """
def hello():
    print("Hello")

def world():
    print("World")

def add(a, b):
    return a + b
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(python_code)
            temp_path = f.name

        try:
            loader = CodeLoader(temp_path)
            docs = loader.load()

            # Should have 3 chunks (3 functions)
            assert len(docs) >= 3

            # Check metadata
            for doc in docs:
                assert doc.metadata['language'] == 'python'
                assert doc.metadata['type'] in ['function', 'module']
                assert 'start_line' in doc.metadata

            # Check function names are captured
            function_chunks = [d for d in docs if d.metadata.get('type') == 'function']
            assert any('hello' in d.metadata.get('name', '') for d in function_chunks)
            assert any('add' in d.metadata.get('name', '') for d in function_chunks)

        finally:
            Path(temp_path).unlink()

    def test_load_python_file_with_class(self):
        """Test loading Python file with class."""
        python_code = """
class Calculator:
    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(python_code)
            temp_path = f.name

        try:
            loader = CodeLoader(temp_path)
            docs = loader.load()

            assert len(docs) >= 1

            # Find the class chunk
            class_chunks = [d for d in docs if d.metadata.get('type') == 'class']
            assert len(class_chunks) >= 1
            assert 'Calculator' in class_chunks[0].metadata.get('name', '')

        finally:
            Path(temp_path).unlink()

    def test_load_javascript_file(self):
        """Test loading JavaScript file."""
        js_code = """
function greet(name) {
    console.log("Hello " + name);
}

const add = (a, b) => {
    return a + b;
}

class Person {
    constructor(name) {
        this.name = name;
    }
}
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(js_code)
            temp_path = f.name

        try:
            loader = CodeLoader(temp_path)
            assert loader.language == 'javascript'

            docs = loader.load()
            assert len(docs) >= 3

            # Check for function and class
            types = [d.metadata.get('type') for d in docs]
            assert 'function' in types or 'module' in types
            assert 'class' in types or 'module' in types

        finally:
            Path(temp_path).unlink()

    def test_load_typescript_file(self):
        """Test loading TypeScript file."""
        ts_code = """
export interface User {
    name: string;
    age: number;
}

export class UserService {
    getUser(id: number): User {
        return { name: "Test", age: 25 };
    }
}

export const formatUser = (user: User) => {
    return `${user.name} (${user.age})`;
}
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ts', delete=False) as f:
            f.write(ts_code)
            temp_path = f.name

        try:
            loader = CodeLoader(temp_path)
            assert loader.language == 'typescript'

            docs = loader.load()
            assert len(docs) >= 2

            # Check for interface and class
            types = [d.metadata.get('type') for d in docs]
            assert 'interface' in types or 'module' in types
            assert 'class' in types or 'module' in types

        finally:
            Path(temp_path).unlink()

    def test_language_detection_from_extension(self):
        """Test automatic language detection."""
        test_cases = [
            ('.py', 'python'),
            ('.js', 'javascript'),
            ('.ts', 'typescript'),
            ('.java', 'java'),
            ('.cpp', 'cpp'),
            ('.c', 'c'),
            ('.go', 'go'),
            ('.rs', 'rust'),
            ('.rb', 'ruby'),
            ('.php', 'php'),
        ]

        for ext, expected_lang in test_cases:
            with tempfile.NamedTemporaryFile(mode='w', suffix=ext, delete=False) as f:
                f.write("// test")
                temp_path = f.name

            try:
                loader = CodeLoader(temp_path)
                assert loader.language == expected_lang, f"Failed for {ext}"
            finally:
                Path(temp_path).unlink()

    def test_fallback_splitting_for_unknown_language(self):
        """Test that unknown languages use fallback splitting."""
        unknown_code = "This is some unknown code format\n" * 100

        with tempfile.NamedTemporaryFile(mode='w', suffix='.xyz', delete=False) as f:
            f.write(unknown_code)
            temp_path = f.name

        try:
            loader = CodeLoader(temp_path)
            assert loader.language == 'unknown'

            docs = loader.load()

            # Should use standard splitting
            assert len(docs) >= 1
            assert docs[0].metadata['type'] == 'chunk'

        finally:
            Path(temp_path).unlink()

    def test_load_nonexistent_file_raises_error(self):
        """Test that loading non-existent file raises FileNotFoundError."""
        loader = CodeLoader('/tmp/nonexistent_code_12345.py')

        with pytest.raises(FileNotFoundError):
            loader.load()

    def test_metadata_completeness(self):
        """Test that all metadata fields are present."""
        python_code = """
def test_function():
    pass
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(python_code)
            temp_path = f.name

        try:
            loader = CodeLoader(temp_path)
            docs = loader.load()

            assert len(docs) >= 1
            metadata = docs[0].metadata

            # Check required metadata fields
            assert 'source' in metadata
            assert 'language' in metadata
            assert 'file_type' in metadata
            assert 'start_line' in metadata
            assert 'type' in metadata

            if metadata['type'] in ['function', 'class']:
                assert 'name' in metadata

        finally:
            Path(temp_path).unlink()

    def test_empty_code_file(self):
        """Test loading empty code file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("")
            temp_path = f.name

        try:
            loader = CodeLoader(temp_path)
            docs = loader.load()

            # Should return empty list or skip empty chunks
            assert isinstance(docs, list)

        finally:
            Path(temp_path).unlink()

    def test_custom_chunk_size(self):
        """Test that custom chunk size is respected in fallback mode."""
        large_code = "# Line\n" * 1000

        with tempfile.NamedTemporaryFile(mode='w', suffix='.xyz', delete=False) as f:
            f.write(large_code)
            temp_path = f.name

        try:
            loader = CodeLoader(temp_path, chunk_size=500, chunk_overlap=50)
            docs = loader.load()

            # Should create multiple chunks
            assert len(docs) > 1

        finally:
            Path(temp_path).unlink()


class TestCodeLoaderEdgeCases:
    """Test edge cases and complex scenarios."""

    def test_python_async_functions(self):
        """Test detection of async functions."""
        python_code = """
async def fetch_data():
    return "data"

async def process_data():
    data = await fetch_data()
    return data
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(python_code)
            temp_path = f.name

        try:
            loader = CodeLoader(temp_path)
            docs = loader.load()

            # Should detect async functions
            function_chunks = [d for d in docs if d.metadata.get('type') == 'function']
            assert len(function_chunks) >= 2

        finally:
            Path(temp_path).unlink()

    def test_nested_functions(self):
        """Test handling of nested functions."""
        python_code = """
def outer():
    def inner():
        return "inner"
    return inner()
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(python_code)
            temp_path = f.name

        try:
            loader = CodeLoader(temp_path)
            docs = loader.load()

            # Should handle nested structure
            assert len(docs) >= 1

        finally:
            Path(temp_path).unlink()

    def test_code_with_comments(self):
        """Test that comments don't break parsing."""
        python_code = """
# This is a comment
def hello():
    # Another comment
    print("Hello")
    # More comments
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(python_code)
            temp_path = f.name

        try:
            loader = CodeLoader(temp_path)
            docs = loader.load()

            # Should still parse correctly
            assert len(docs) >= 1
            # 'hello' should be in at least one doc (might be split by comments)
            assert any('hello' in doc.text for doc in docs)

        finally:
            Path(temp_path).unlink()
