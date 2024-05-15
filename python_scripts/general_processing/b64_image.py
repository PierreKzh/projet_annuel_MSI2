from io import BytesIO
import base64
from PIL import Image

def image_to_base64(img: Image) -> str:
    """Convert a PIL Image to a base64 string."""
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

