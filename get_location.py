import os.path

def get_location(path_to_resolve: str, local_path: str, resource_id: int, user_id: int) -> str:
    if os.path.isabs(path_to_resolve):
        return path_to_resolve
    return os.path.abspath(os.path.join(local_path, path_to_resolve))