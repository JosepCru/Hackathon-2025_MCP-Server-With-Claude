# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "mcp[cli]>=1.12.3",
#     "python-dotenv>=1.1.1",
#     "requests>=2.32.4",
# ]
# ///

from mcp.server.fastmcp import FastMCP


mcp = FastMCP("StructureProperty")

@mcp.tool(
    name="Analyze_Structure",
    description="Analyzes the structure of a sample."
)
def structure_analysis():
    return "Sample structure analyzed."

@mcp.tool(
    name="Get_spectra_at_all_pixels",
    description="Extracts the spectrum from each pixel in the image and store it in a 3D array."
)
def get_spectra_at_all_pixels():
    return "Spectra extracted from all pixels."

if __name__ == "__main__":
    mcp.run(transport="stdio")