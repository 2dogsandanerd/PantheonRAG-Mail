import os

directory = 'src/api/v1'

for root, _, files in os.walk(directory):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r') as f:
                content = f.read()
                
            if 'get_current_active_user' in content and 'from src.core.auth import get_current_active_user' not in content:
                print(f"Fixing {filepath}")
                new_content = "from src.core.auth import get_current_active_user\n" + content
                with open(filepath, 'w') as f:
                    f.write(new_content)
