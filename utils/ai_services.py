"""AI service integrations for the application."""
import os
from typing import Dict, Any, Optional, List, Union, BinaryIO
import base64
import io
import tempfile
from pathlib import Path

# Third-party imports

# OpenAI client compatibility (v1+ and legacy)
_OPENAI_V1 = False

def _get_api_key_and_org() -> (Optional[str], Optional[str]):
    """Fetch API key and org from env or Streamlit secrets each time."""
    key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_APIKEY")
    org = os.getenv("OPENAI_ORG_ID") or os.getenv("OPENAI_ORGANIZATION")
    if not key:
        try:
            import streamlit as st  # type: ignore
            key = st.secrets.get("OPENAI_API_KEY") or st.secrets.get("openai_api_key")
            org = org or st.secrets.get("OPENAI_ORG_ID") or st.secrets.get("openai_organization")
        except Exception:
            pass
    return key, org

_client_holder = {"client": None, "api_key": None, "org": None}

try:
    from openai import OpenAI  # v1+
    _OPENAI_V1 = True
except Exception:
    _OPENAI_V1 = False
    import openai as _openai_legacy  # legacy <1.0

def _ensure_client() -> Dict[str, Any]:
    """Ensure OpenAI client is initialized with the current API key and org.
    Returns a dict with keys: success(bool), error(str?)
    """
    key, org = _get_api_key_and_org()
    if not key:
        return {"success": False, "error": "Missing OpenAI API key", "error_type": "AuthError"}
    # Recreate client if key/org changed or missing
    if _OPENAI_V1:
        if (_client_holder["client"] is None) or (_client_holder["api_key"] != key) or (_client_holder["org"] != org):
            from openai import OpenAI  # type: ignore
            _client_holder["client"] = OpenAI(api_key=key, organization=org)
            _client_holder["api_key"] = key
            _client_holder["org"] = org
    else:
        # Legacy client uses module-level configuration
        _openai_legacy.api_key = key
        if org:
            try:
                _openai_legacy.organization = org
            except Exception:
                pass
        _client_holder["client"] = _openai_legacy
        _client_holder["api_key"] = key
        _client_holder["org"] = org
    return {"success": True}

class AIService:
    """Handles all AI-related operations including vision and audio processing."""
    
    @staticmethod
    def analyze_image(image_data: Union[bytes, BinaryIO, str, Path]) -> Dict[str, Any]:
        """
        Analyze an image using GPT-4 Vision.
        
        Args:
            image_data: Binary image data, file-like object, or file path
            
        Returns:
            Dict containing analysis results
        """
        init = _ensure_client()
        if not init.get("success"):
            return init
        try:
            # Convert image to base64
            if hasattr(image_data, 'read'):
                image_data = image_data.read()
            elif isinstance(image_data, (str, Path)) and os.path.isfile(image_data):
                with open(image_data, 'rb') as f:
                    image_data = f.read()
            
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyze this image in detail."},
                        {
                            "type": "image_url",
                            "image_url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    ],
                }
            ]
            if _OPENAI_V1:
                response = _client_holder["client"].chat.completions.create(
                    model="gpt-4-vision-preview",
                    messages=messages,
                    max_tokens=1000,
                )
                content = response.choices[0].message.content
            else:
                response = _openai_legacy.ChatCompletion.create(
                    model="gpt-4-vision-preview",
                    messages=messages,
                    max_tokens=1000,
                )
                content = response["choices"][0]["message"]["content"]
            
            return {"success": True, "analysis": content}
            
        except Exception as e:
            msg = str(e)
            if "invalid_api_key" in msg or "Incorrect API key provided" in msg:
                return {"success": False, "error": "Invalid OpenAI API key. Check your .env or Streamlit secrets and restart the app.", "error_type": "AuthError"}
            return {
                "success": False,
                "error": msg,
                "error_type": type(e).__name__
            }
    
    @staticmethod
    def transcribe_audio(audio_data: Union[bytes, BinaryIO, str, Path], 
                         file_extension: str = None) -> Dict[str, Any]:
        """
        Transcribe audio using Whisper.
        
        Args:
            audio_data: Audio data, file-like object, or file path
            file_extension: Optional file extension (e.g., 'mp3', 'wav')
            
        Returns:
            Dict containing the transcription and metadata
        """
        temp_file = None
        init = _ensure_client()
        if not init.get("success"):
            return init
        try:
            # Handle different input types
            if isinstance(audio_data, bytes):
                if not file_extension:
                    file_extension = 'mp3'  # Default to mp3 if not specified
                temp_file = tempfile.NamedTemporaryFile(suffix=f'.{file_extension}', delete=False)
                temp_file.write(audio_data)
                temp_file.close()
                audio_path = temp_file.name
                
            elif hasattr(audio_data, 'read'):
                # For file-like objects
                if not file_extension and hasattr(audio_data, 'name'):
                    file_extension = os.path.splitext(audio_data.name)[1][1:] or 'mp3'
                temp_file = tempfile.NamedTemporaryFile(suffix=f'.{file_extension}', delete=False)
                temp_file.write(audio_data.read())
                temp_file.close()
                audio_path = temp_file.name
                
            elif isinstance(audio_data, (str, Path)) and os.path.isfile(audio_data):
                audio_path = str(audio_data)
                
            else:
                return {
                    "success": False,
                    "error": "Invalid audio data format"
                }
            
            # Transcribe the audio file
            with open(audio_path, 'rb') as audio_file:
                if _OPENAI_V1:
                    transcript = _client_holder["client"].audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        response_format="json",
                    )
                    text = transcript.text
                    language = getattr(transcript, 'language', 'en')
                    raw = transcript.model_dump()
                else:
                    transcript = _openai_legacy.Audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        response_format="json",
                    )
                    text = transcript.get("text", "")
                    language = transcript.get("language", "en")
                    raw = transcript

            return {
                "success": True,
                "text": text,
                "language": language,
                "raw_response": raw,
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
            
        finally:
            # Clean up temp file if we created one
            if temp_file is not None and os.path.exists(temp_file.name):
                try:
                    os.unlink(temp_file.name)
                except Exception as e:
                    print(f"Error cleaning up temp file: {e}")
        
    
    @staticmethod
    def generate_content(prompt: str, 
                        model: str = "gpt-4-1106-preview",
                        temperature: float = 0.7,
                        max_tokens: int = 1000) -> Dict[str, Any]:
        """
        Generate text content using the specified model.
        
        Args:
            prompt: The prompt to generate content from
            model: The model to use (default: gpt-4-1106-preview)
            temperature: Controls randomness (0.0 to 2.0)
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            Dict containing the generated text and metadata
        """
        init = _ensure_client()
        if not init.get("success"):
            return init
        try:
            messages = [{"role": "user", "content": prompt}]
            if _OPENAI_V1:
                response = _client_holder["client"].chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                text = response.choices[0].message.content
                usage = {
                    "prompt_tokens": getattr(response.usage, 'prompt_tokens', None),
                    "completion_tokens": getattr(response.usage, 'completion_tokens', None),
                    "total_tokens": getattr(response.usage, 'total_tokens', None),
                }
                raw = response.model_dump()
            else:
                response = _openai_legacy.ChatCompletion.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                text = response["choices"][0]["message"]["content"]
                usage = response.get("usage", {})
                raw = response

            return {
                "success": True,
                "text": text,
                "model": model,
                "usage": usage,
                "raw_response": raw,
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }


# Singleton instance
ai_service = AIService()

# Helper functions for backward compatibility
def analyze_image(*args, **kwargs):
    return ai_service.analyze_image(*args, **kwargs)

def transcribe_audio(*args, **kwargs):
    return ai_service.transcribe_audio(*args, **kwargs)

def generate_content(*args, **kwargs):
    return ai_service.generate_content(*args, **kwargs)
