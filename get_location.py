import os.path

def get_location(path: str, current_path: str, resource_id: int, user_id: int):
    if os.path.isabs(path):
        return path
    return os.path.abspath(os.path.join(current_path, path))