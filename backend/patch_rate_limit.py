import re
import sys

def patch_file(filepath, limit_name):
    with open(filepath, 'r') as f:
        content = f.read()

    # Add imports
    if 'from fastapi import Request' not in content and ' Request,' not in content and ' Request ' not in content:
        content = re.sub(r'from fastapi import \(?', r'from fastapi import Request, \n    ', content, count=1)
        if 'from fastapi import Request' not in content:
            content = content.replace('from fastapi import', 'from fastapi import Request,')

    if 'from src.core.rate_limiter import limiter, RATE_LIMITS' not in content:
        content = 'from src.core.rate_limiter import limiter, RATE_LIMITS\n' + content

    # Add decorators and request param
    # Match @router.something(...)
    # async def func_name(
    
    pattern = re.compile(r'(@router\.(?:get|post|delete|put|patch)\([^)]*\)\n)(async def [a-zA-Z0-9_]+\()')
    
    def repl(m):
        router_dec = m.group(1)
        func_sig = m.group(2)
        # Check if already limited
        if '@limiter.limit' in router_dec:
            return m.group(0)
        return f'{router_dec}@limiter.limit(RATE_LIMITS["{limit_name}"])\n{func_sig}request: Request, '

    new_content = pattern.sub(repl, content)

    with open(filepath, 'w') as f:
        f.write(new_content)
    print(f"Patched {filepath}")

patch_file('src/api/v1/email.py', 'email')
patch_file('src/api/v1/rag/documents/upload.py', 'ingest')
patch_file('src/api/v1/auto_draft.py', 'default')

