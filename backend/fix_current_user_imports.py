import os

directory = 'src/api/v1'

for root, _, files in os.walk(directory):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r') as f:
                content = f.read()
                
            if 'CurrentUser' in content and 'from src.api.v1.deps import CurrentUser' not in content:
                print(f"Fixing {filepath}")
                new_content = "from src.api.v1.deps import CurrentUser\n" + content
                with open(filepath, 'w') as f:
                    f.write(new_content)
