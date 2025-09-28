import os
import tempfile

async def save_file_to_temp(file_bytes: bytes, suffix=".jpg") -> str:
    """
    Save bytes to a temporary file and return path.
    """
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, 'wb') as tmp:
        tmp.write(file_bytes)
    return path

def cleanup_file(path: str):
    try:
        os.remove(path)
    except Exception:
        pass
