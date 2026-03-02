import os

directory = 'src/api/v1/rag'

for root, _, files in os.walk(directory):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r') as f:
                content = f.read()
                
            new_content = content.replace("from src.services.auth_service import get_current_user", "from src.core.auth import get_current_active_user")
            new_content = new_content.replace("Depends(get_current_user)", "Depends(get_current_active_user)")
            
            if new_content != content:
                print(f"Fixing {filepath}")
                with open(filepath, 'w') as f:
                    f.write(new_content)
