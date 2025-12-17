# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "mcp[cli]>=1.12.3",
#     "pydantic>=2.11.7",
#     "python-dotenv>=1.1.1",
#     "requests>=2.32.4",
#     "matplotlib>=3.7.2",
# ]
# ///

from mcp.server.fastmcp import FastMCP
from matplotlib import pyplot as plt

mcp = FastMCP("DisplayImages")

@mcp.tool(
    name="Grid_Image_Display",
    description="Displays a grid of images submitted by the user"
)
def grid_image_display():
    return("Image grid displayed.")

if __name__ == "__main__":
    mcp.run(transport="stdio")