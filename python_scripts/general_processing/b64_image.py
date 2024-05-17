from io import BytesIO
import base64
from PIL import Image

def image_to_base64(img: Image) -> str:
    """Convert a PIL Image to a base64 string."""
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def base64_to_image(base64_str: str) -> Image:
    """
    Convert a base64 string to a PIL Image.

    Args:
    base64_str (str): The base64 encoded string of the image.

    Returns:
    Image: The PIL Image object.
    """
    image_data: bytes = base64.b64decode(base64_str)
    buffered: BytesIO = BytesIO(image_data)
    img: Image = Image.open(buffered)
    return img