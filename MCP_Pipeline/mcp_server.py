import os 
import base64
import httpx
from dotenv import load_dotenv
from mcp.server.mcpserver  import MCPServer, Image
from mcp.server.mcpserver.exceptions import ToolError 
 
load_dotenv() 

HOST = "0.0.0.0" 
PORT = 8001 

CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")

MODEL = "@cf/black-forest-labs/flux-1-schnell"

API_URL = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/run/{MODEL}"

mcp = MCPServer("medical-image-server")


# generate_image 
@mcp.tool() 
async def generate_image(question: str) -> Image:
    """Generate an educational medical illustration for the user's question."""

    if not CLOUDFLARE_ACCOUNT_ID or not CLOUDFLARE_API_TOKEN:
        raise ToolError("Cloudflare keys are missing. Check the names and values in you .env file.")

    prompt = (
        f"A clear, professtional, educational medical illustration that explains: {question}."
    )
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                API_URL,
                headers={"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}"},
                json={"prompt": prompt, "steps":4},
            )
    except httpx.HTTPError as e:
        raise ToolError(f"Image generation failed: {e!r}")

    if response.status_code != 200:
        raise ToolError(f"Cloudflare error {response.status_code}: {response.text[:300]}")

    # Cloudflare returns the picture as a base64 string inside {"result": {"image": "...."}}
    image_b64 = response.json().get("result", {}).get("image")
    if not image_b64:
        raise ToolError("Cloudflare did not return an image.")
    return Image(data = base64.b64decode(image_b64), format='jpeg')


if __name__ == "__main__":
    mcp.run(transport = 'streamable-http', host=HOST, port=PORT)


