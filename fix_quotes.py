import os

d = r'C:\Users\皮蛋超人\Documents\egg_cat'
for fname in ['main.py', 'auth.py', 'crud.py', 'models.py', 'schemas.py', 'test_main.py', 'database.py']:
    fp = os.path.join(d, fname)
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()
    # Fix the PowerShell escaped triple-quotes issue
    content = content.replace('\\\"\"\"', '\"\"\"')
    content = content.replace('\\\"', '\"')
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Fixed: {fname}')
