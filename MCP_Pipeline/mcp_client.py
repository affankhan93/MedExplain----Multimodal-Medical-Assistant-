import asyncio
import base64
import os 
import sys 
from dotenv import load_dotenv 
from mcp import ClientSession 
from mcp.client.streamable_http import streamable_http_client

load_dotenv() 

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", 'http://localhost:8001/mcp')

async def generate_image(question: str):
    """Send the question to the MCP server and return the image as a base64 string."""

    async with streamable_http_client(MCP_SERVER_URL) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize() 
            result = await session.call_tool("generate_image", {"question": question})

    if result.is_error:
        message = result.content[0].text if result.content else "unknown error"
        raise RuntimeError(f"MCP server error: {message}")

    for item in result.content:
        if item.type == 'image':
            return item.data 
        
    raise RuntimeError(f"MCP server sent no image. It sent: {result.content}")

if __name__ == "__main__":
    question = sys.argv[1] if len(sys.argv) > 1 else "What are the symptoms of diabetes?"
    image_b64 = asyncio.run(generate_image(question))

    if image_b64:
        with open("test_image.png", 'wb') as f:
            f.write(base64.b64decode(image_b64))
        print("Image saved as test_image.png")
    else:
        print("No image returned.")

