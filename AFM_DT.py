#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#      "mcp>=1.0.0",
#      "Pyro5>=5.14",
#      "numpy>=1.24.0",
# ]
# ///

"""
AFM Digital Twin MCP Server - Simple Connection Test
"""

import asyncio
import mcp.server.stdio
import mcp.types as types
from mcp.server import Server

# Initialize MCP server
app = Server("afm-digital-twin")


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    """List available tools"""
    return [
        types.Tool(
            name="test_connection",
            description="Test connection to the AFM Pyro5 server",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="initialize_afm",
            description="Initialize the AFM microscope with an H5 data file and setup the dataset",
            inputSchema={
                "type": "object",
                "properties": {
                    "data_path": {
                        "type": "string",
                        "description": "Path to the H5 file (e.g., 'dset_spm1.h5' or full path)"
                    },
                    "data_source": {
                        "type": "string",
                        "description": "Dataset name within the H5 file",
                        "default": "Compound_Dataset_1"
                    }
                },
                "required": ["data_path"]
            }
        ),
        types.Tool(
            name="get_full_scan",
            description="Get the complete 2D scan image from the dataset. The direction parameter specifies the fast-scanning axis, and trace emulates data acquisition on forward or backward pass. Use modification to simulate imperfections like broken tip or non-ideal PID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "channels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of channel names (e.g., ['HeightRetrace', 'Phase1Retrace'])"
                    },
                    "modification": {
                        "type": "string",
                        "description": "Optional: Apply imperfections to simulate realistic scanning (e.g., 'broken_tip', 'bad_pid'). Use None for no modification.",
                        "default": None
                    },
                    "direction": {
                        "type": "string",
                        "enum": ["horizontal", "vertical"],
                        "description": "Fast-scanning axis direction",
                        "default": "horizontal"
                    },
                    "trace": {
                        "type": "string",
                        "enum": ["forward", "backward"],
                        "description": "Data acquisition pass direction",
                        "default": "forward"
                    }
                },
                "required": ["channels"]
            }
        ),
        types.Tool(
            name="scan_individual_line",
            description="Scan a single line (horizontal or vertical) at a specific coordinate. The coord parameter specifies x-coordinate if direction='vertical' and y-coordinate if direction='horizontal'.",
            inputSchema={
                "type": "object",
                "properties": {
                    "direction": {
                        "type": "string",
                        "enum": ["vertical", "horizontal"],
                        "description": "Line direction: 'vertical' for constant x (scans along y), 'horizontal' for constant y (scans along x)"
                    },
                    "coord": {
                        "type": "number",
                        "description": "Coordinate in meters (e.g., -1e-6 for -1 micrometer)"
                    },
                    "channels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of channel names (e.g., ['Amplitude1Retrace', 'Phase1Retrace'])"
                    }
                },
                "required": ["direction", "coord", "channels"]
            }
        ),
        types.Tool(
            name="scan_arbitrary_path",
            description="Scan along an arbitrary path defined by corner coordinates. Returns data captured along the trajectory.",
            inputSchema={
                "type": "object",
                "properties": {
                    "corners": {
                        "type": "array",
                        "description": "Array of [x, y] coordinate pairs in meters (e.g., [[-2e-6, 2e-6], [1e-6, 1.8e-6], [2.1e-6, 2e-6]])",
                        "items": {
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 2,
                            "maxItems": 2
                        }
                    },
                    "channels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of channel names to scan"
                    }
                },
                "required": ["corners", "channels"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls"""
    
    if name == "test_connection":
        try:
            import Pyro5.api
            
            # Try to connect to the Pyro5 server
            uri = "PYRO:microscope.server@localhost:9092"
            mic_server = Pyro5.api.Proxy(uri)
            
            # Try to ping it
            mic_server._pyroBind()
            
            return [types.TextContent(
                type="text",
                text="✅ Successfully connected to AFM Pyro5 server at localhost:9092!"
            )]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"❌ Failed to connect to AFM server: {str(e)}\n\nMake sure 'run_server_afm' is running!"
            )]
    
    elif name == "initialize_afm":
        try:
            import Pyro5.api
            import numpy as np
            
            # Connect to the Pyro5 server
            uri = "PYRO:microscope.server@localhost:9092"
            mic_server = Pyro5.api.Proxy(uri)
            
            # Get parameters
            data_path = arguments["data_path"]
            data_source = arguments.get("data_source", "Compound_Dataset_1")
            
            # Initialize the microscope with the H5 file
            mic_server.initialize_microscope("AFM", data_path=data_path)
            
            # Setup the dataset
            mic_server.setup_microscope(data_source=data_source)
            
            # Get dataset info
            dataset_info = mic_server.get_dataset_info()
            
            result = f"✅ Successfully initialized AFM Digital Twin!\n\n"
            result += f"📁 Data file: {data_path}\n"
            result += f"📊 Dataset: {data_source}\n\n"
            result += f"Dataset Info:\n{dataset_info}"
            
            return [types.TextContent(
                type="text",
                text=result
            )]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"❌ Failed to initialize AFM: {str(e)}"
            )]
    
    elif name == "get_full_scan":
        try:
            import Pyro5.api
            import numpy as np
            
            # Connect to the Pyro5 server
            uri = "PYRO:microscope.server@localhost:9092"
            mic_server = Pyro5.api.Proxy(uri)
            
            # Get parameters
            channels = arguments["channels"]
            modification = arguments.get("modification")
            if modification == "None" or modification == "null":
                modification = None
            direction = arguments.get("direction", "horizontal")
            trace = arguments.get("trace", "forward")
            
            # Get the full scan
            array_list, shape, dtype = mic_server.get_scan(
                channels=channels,
                modification=modification,
                direction=direction,
                trace=trace
            )
            
            # Reshape the data
            dat = np.array(array_list, dtype=dtype).reshape(shape)
            
            # Build result summary
            result = f"✅ Full 2D scan completed!\n\n"
            result += f"Channels: {channels}\n"
            result += f"Direction: {direction} (fast-scan axis)\n"
            result += f"Trace: {trace}\n"
            result += f"Modification: {modification if modification else 'None'}\n"
            result += f"Image shape: {shape}\n\n"
            
            # Statistics for each channel
            for i, channel in enumerate(channels):
                channel_data = dat[i]
                result += f"{channel}:\n"
                result += f"  Image size: {channel_data.shape}\n"
                result += f"  Min: {np.min(channel_data):.6e}\n"
                result += f"  Max: {np.max(channel_data):.6e}\n"
                result += f"  Mean: {np.mean(channel_data):.6e}\n"
                result += f"  Std Dev: {np.std(channel_data):.6e}\n\n"
            
            return [types.TextContent(
                type="text",
                text=result
            )]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"❌ Failed to get full scan: {str(e)}"
            )]
    
    elif name == "scan_individual_line":
        try:
            import Pyro5.api
            import numpy as np
            
            # Connect to the Pyro5 server
            uri = "PYRO:microscope.server@localhost:9092"
            mic_server = Pyro5.api.Proxy(uri)
            
            # Get parameters
            direction = arguments["direction"]
            coord = arguments["coord"]
            channels = arguments["channels"]
            
            # Scan the line
            array_list, shape, dtype = mic_server.scan_individual_line(
                direction, coord=coord, channels=channels
            )
            
            # Reshape the data
            line = np.array(array_list, dtype=dtype).reshape(shape)
            
            # Build result summary
            result = f"✅ Line scan completed!\n\n"
            result += f"Direction: {direction}\n"
            result += f"Coordinate: {coord} meters ({coord*1e6:.2f} µm)\n"
            result += f"Channels: {channels}\n"
            result += f"Data shape: {shape}\n\n"
            
            # Statistics for each channel
            for i, channel in enumerate(channels):
                channel_data = line[i]
                result += f"{channel}:\n"
                result += f"  Points: {len(channel_data)}\n"
                result += f"  Min: {np.min(channel_data):.6e}\n"
                result += f"  Max: {np.max(channel_data):.6e}\n"
                result += f"  Mean: {np.mean(channel_data):.6e}\n"
                result += f"  Std Dev: {np.std(channel_data):.6e}\n\n"
            
            return [types.TextContent(
                type="text",
                text=result
            )]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"❌ Failed to scan line: {str(e)}"
            )]
    
    elif name == "scan_arbitrary_path":
        try:
            import Pyro5.api
            import numpy as np
            
            # Connect to the Pyro5 server
            uri = "PYRO:microscope.server@localhost:9092"
            mic_server = Pyro5.api.Proxy(uri)
            
            # Get parameters
            corners = np.array(arguments["corners"])
            channels = arguments["channels"]
            
            # Scan along the path
            array_list, shape, dtype = mic_server.scan_arbitrary_path(
                corners, channels=channels
            )
            
            # Reshape the data
            dat = np.array(array_list, dtype=dtype).reshape(shape)
            
            # Build result summary
            result = f"✅ Path scan completed!\n\n"
            result += f"Path defined by {len(corners)} corners:\n"
            for i, corner in enumerate(corners):
                result += f"  Point {i+1}: ({corner[0]*1e6:.2f}, {corner[1]*1e6:.2f}) µm\n"
            result += f"\nChannels: {channels}\n"
            result += f"Data shape: {shape}\n\n"
            
            # Statistics for each channel
            for i, channel in enumerate(channels):
                channel_data = dat[i]
                result += f"{channel}:\n"
                result += f"  Min: {np.min(channel_data):.6e}\n"
                result += f"  Max: {np.max(channel_data):.6e}\n"
                result += f"  Mean: {np.mean(channel_data):.6e}\n"
                result += f"  Std Dev: {np.std(channel_data):.6e}\n\n"
            
            return [types.TextContent(
                type="text",
                text=result
            )]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"❌ Failed to scan path: {str(e)}"
            )]
    
    return [types.TextContent(
        type="text",
        text=f"Unknown tool: {name}"
    )]


async def main():
    """Run the MCP server"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())