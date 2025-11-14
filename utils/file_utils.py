"""
File handling utilities for the application.
"""
import os
import tempfile
from pathlib import Path
from typing import Union, BinaryIO, Dict, Any, Optional, List

# Try to import magic, but make it optional
try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False
    import warnings
    warnings.warn(
        "python-magic is not installed. Some file type validations will be limited.\n"
        "Install it with: pip install python-magic-bin (Windows) or "
        "brew install libmagic (macOS) or apt-get install libmagic1 (Linux)"
    )

from PIL import Image
import io

# Supported file types
SUPPORTED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/jpg']
SUPPORTED_AUDIO_TYPES = ['audio/mpeg', 'audio/wav', 'audio/m4a', 'audio/ogg']

def validate_file_type(file: BinaryIO, allowed_types: list) -> bool:
    """
    Validate if a file's MIME type is in the allowed types.
    
    Args:
        file: File-like object or path to file
        allowed_types: List of allowed MIME types
        
    Returns:
        bool: True if file type is allowed, False otherwise
    """
    if not HAS_MAGIC:
        # Fallback to file extension check if magic is not available
        try:
            if hasattr(file, 'name'):
                ext = os.path.splitext(file.name)[1].lower()
            else:
                ext = os.path.splitext(str(file))[1].lower()
            
            # Map common extensions to MIME types
            ext_to_mime = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.webp': 'image/webp',
                '.mp3': 'audio/mpeg',
                '.wav': 'audio/wav',
                '.m4a': 'audio/m4a',
                '.ogg': 'audio/ogg'
            }
            
            file_type = ext_to_mime.get(ext, '')
            return file_type in allowed_types
            
        except Exception as e:
            print(f"Error in fallback file type validation: {e}")
            return False
    
    try:
        # Read the first 1024 bytes to determine the file type
        if hasattr(file, 'read'):
            pos = file.tell()
            file_header = file.read(1024)
            file.seek(pos)  # Reset file pointer
        else:
            with open(file, 'rb') as f:
                file_header = f.read(1024)
        
        # Get MIME type using magic
        mime = magic.Magic(mime=True)
        file_type = mime.from_buffer(file_header)
        
        return file_type in allowed_types
        
    except Exception as e:
        print(f"Error validating file type: {e}")
        return False

def process_image_upload(file: Union[BinaryIO, str, bytes], 
                        max_size: tuple = (800, 800),
                        quality: int = 85) -> Optional[bytes]:
    """
    Process an uploaded image file.
    
    Args:
        file: File-like object, file path, or bytes
        max_size: Maximum dimensions (width, height)
        quality: JPEG quality (1-100)
        
    Returns:
        Processed image as bytes or None if processing fails
    """
    try:
        # Handle different input types
        if isinstance(file, bytes):
            img = Image.open(io.BytesIO(file))
        elif hasattr(file, 'read'):
            img = Image.open(file)
        else:  # Assume it's a file path
            img = Image.open(file)
        
        # Convert to RGB if needed
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        
        # Resize if needed
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Save to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG', quality=quality, optimize=True)
        
        return img_byte_arr.getvalue()
        
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

def save_uploaded_file(uploaded_file, directory: str = "uploads") -> Optional[str]:
    """
    Save an uploaded file to the specified directory.
    
    Args:
        uploaded_file: Streamlit UploadedFile object or similar
        directory: Directory to save the file in
        
    Returns:
        Path to the saved file or None if saving fails
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)
        
        # Generate a unique filename
        file_ext = os.path.splitext(uploaded_file.name)[1]
        file_name = f"{os.urandom(8).hex()}{file_ext}"
        file_path = os.path.join(directory, file_name)
        
        # Save the file
        with open(file_path, "wb") as f:
            if hasattr(uploaded_file, 'read'):
                f.write(uploaded_file.read())
            else:
                f.write(uploaded_file)
        
        return file_path
        
    except Exception as e:
        print(f"Error saving file: {e}")
        return None

def get_file_extension(file: Union[BinaryIO, str]) -> Optional[str]:
    """
    Get the file extension from a file or file path.
    
    Args:
        file: File-like object or file path
        
    Returns:
        File extension (without dot) or None if not found
    """
    try:
        if hasattr(file, 'name'):
            # Handle file-like objects with name attribute
            _, ext = os.path.splitext(file.name)
        elif isinstance(file, str):
            # Handle file paths
            _, ext = os.path.splitext(file)
        else:
            return None
        
        return ext.lstrip('.').lower() if ext else None
        
    except Exception:
        return None

def cleanup_temp_files():
    """Clean up any temporary files in the uploads directory."""
    try:
        if os.path.exists("uploads"):
            for filename in os.listdir("uploads"):
                file_path = os.path.join("uploads", filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")
    except Exception as e:
        print(f"Error during cleanup: {e}")
