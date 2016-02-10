import os

def pretty(path):
    # Remove trailing /
    path = path.rstrip('/')
    
    # Replace user home with ~.
    if (path.startswith(os.path.expanduser('~'))):
        path = path.replace(os.path.expanduser('~'), '~')
    
    return path

def full(path):
    # Replace ~
        if (path.startswith('~')):
            path = path.replace('~', os.path.expanduser('~'))
        
        # Handle relative path
        if (not path.startswith('/')):
            path = os.path.join(os.getcwd(), path)
        return path
