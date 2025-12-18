# /// script
# dependencies = [
#     "mcp[cli]>=1.12.3",
#     "pydantic>=2.11.7",
#     "python-dotenv>=1.1.1",
#     "requests>=2.32.4",
# ]
# ///

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

class TakeImageRequest(BaseModel):
    confirm: bool = False
    resolution: int = 1024
    exposure_s: float = 1e-6

mcp = FastMCP("ParticleDetector")

@mcp.tool(
    name="Microscope_Connections",
    description="Controls the connection status of the microscope device."
)
def microscope_control(action: str):
    if action == "connect":
        return "Microscope connected successfully."

    elif action == "disconnect":
        return "Microscope disconnected successfully."

    else:
        return {"error": f"Unknown action '{action}'"}

    
@mcp.tool(
        name="Microscope_Movement_Control",
        description="Controls the movement of the microscope stage."
        )
def move_stage(direction: str, distance_um: float) -> str:
    try:
        return f"Stage moved {distance_um} micrometers to the {direction}."
    except Exception as e:
        return f"Failed to move stage: {e}"

@mcp.tool(
        name="Microscope_Zoom_Control",
        description="Controls the zoom level of the microscope."
        )
def zoom_in(factor: float) -> str:
    try:
        return f"Zoomed in by a factor of {factor}."
    except Exception as e:
        return f"Failed to zoom in: {e}"


@mcp.tool(
        name="Microscope_Image",
        description="Takes an image from the microscope. User can optionally specify resolution, magnification, and exposure."
        )

def take_image(params: TakeImageRequest):
    if not params.confirm:
        return {
            "status": "need_confirmation",
            "message": "Do you want to specify resolution, magnification, or exposure before taking the image?"
    }

    else:
        try:
            return {
            "status": "correct",
            "message": f"Success to take image from microscope"
            }
        
        except Exception as e:
            return {
            "status": "error",
            "message": f"Failed to take image from microscope: {e}"
            }
    

if __name__ == "__main__":
    mcp.run(transport="stdio")