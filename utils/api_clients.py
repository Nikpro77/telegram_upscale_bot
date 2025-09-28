import aiohttp
import base64
from config import DEEPAI_API_KEY, IMGBB_API_KEY

async def upscale_image(image_bytes: bytes, quality: str = "standard") -> bytes:
    """
    Upscale image using DeepAI API.
    quality param can be extended for different API params if supported.
    """
    url = "https://api.deepai.org/api/torch-srgan"
    headers = {"api-key": DEEPAI_API_KEY}
    data = aiohttp.FormData()
    data.add_field('image', image_bytes, filename='image.jpg', content_type='image/jpeg')

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data, headers=headers) as resp:
            if resp.status != 200:
                raise Exception(f"Upscale API error: {resp.status}")
            result = await resp.json()
            output_url = result.get("output_url")
            if not output_url:
                raise Exception("No output_url in upscale API response")

        async with session.get(output_url) as img_resp:
            if img_resp.status != 200:
                raise Exception(f"Failed to download upscaled image: {img_resp.status}")
            return await img_resp.read()

async def upload_image_to_imgbb(image_bytes: bytes) -> str:
    """
    Upload image to ImgBB and return direct URL.
    """
    url = "https://api.imgbb.com/1/upload"
    b64_image = base64.b64encode(image_bytes).decode('utf-8')
    params = {
        "key": IMGBB_API_KEY,
        "image": b64_image
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=params) as resp:
            if resp.status != 200:
                raise Exception(f"Image upload error: {resp.status}")
            result = await resp.json()
            if not result.get("success"):
                raise Exception("Image upload failed")
            return result["data"]["url"]
