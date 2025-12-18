# /// script
# requires-python = ">=3.10"
# dependencies = [
#      "mcp>=1.0.0",
#      "matplotlib>=3.7.2",
#      "numpy>=1.24.0",
#      "Pyro5>=5.14",
#      "h5py>=3.8.0",
#      "sidpy>=0.1.2",
#      "scifireaders>=0.0.1",
# ]
# ///

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend

from mcp.server.fastmcp import FastMCP
import matplotlib.pyplot as plt
import numpy as np
import Pyro5.api
import sidpy
import subprocess
import time
import os

mcp = FastMCP("Scientific_AFM_Controller")

# Global state
mic_server = None
current_h5_path = None

def start_background_server():
    """Attempt to start the AFM server if it's not responding."""
    try:
        # Check if something is already on that port
        proxy = Pyro5.api.Proxy("PYRO:microscope.server@localhost:9092")
        proxy._pyroBind()
        return True
    except Exception:
        print("Starting AFM Server in background...")
        subprocess.Popen(["run_server_afm"], shell=True, stdout=subprocess.DEVNULL)
        time.sleep(3)  # Wait for startup
        return True

@mcp.tool()
def initialize_microscope(h5_file_path: str, dataset_name: str = 'Compound_Dataset_1') -> str:
    """
    Starts the AFM server and initializes connection to the H5 data file.
    """
    global mic_server, current_h5_path
    
    start_background_server()
    
    try:
        uri = "PYRO:microscope.server@localhost:9092"
        mic_server = Pyro5.api.Proxy(uri)
        mic_server.initialize_microscope("AFM", data_path=h5_file_path)
        mic_server.setup_microscope(data_source=dataset_name)
        
        current_h5_path = h5_file_path
        info = mic_server.get_dataset_info()
        return f"AFM Ready. Data: {os.path.basename(h5_file_path)}\nMetadata: {info}"
    except Exception as e:
        return f"Initialization failed: {str(e)}"

@mcp.tool()
def capture_and_analyze_scan(channels: list[str]) -> str:
    """
    Captures a full scan and returns visual path + scientific statistics (RMS, Mean).
    """
    global mic_server
    if not mic_server:
        return "Microscope not initialized."

    try:
        array_list, shape, dtype = mic_server.get_scan(channels=channels)
        raw_data = np.array(array_list, dtype=dtype).reshape(shape)
        
        analysis_results = []
        save_path = "latest_afm_scan.png"
        
        fig, axes = plt.subplots(1, len(channels), figsize=(5 * len(channels), 4))
        if len(channels) == 1: axes = [axes]

        for i, (chan, ax) in enumerate(zip(channels, axes)):
            # Convert to sidpy Dataset for processing
            data_slice = raw_data[i]
            dataset = sidpy.Dataset.from_array(data_slice, name=chan)
            
            # Calculate scientific stats
            rms = np.sqrt(np.mean(np.square(data_slice - np.mean(data_slice))))
            analysis_results.append(f"{chan}: RMS Roughness = {rms:.2e} m, P-P = {np.ptp(data_slice):.2e} m")
            
            im = ax.imshow(data_slice.T, cmap='magma', origin='lower')
            plt.colorbar(im, ax=ax, label='Value')
            ax.set_title(chan)
            ax.axis('off')

        plt.savefig(save_path)
        plt.close(fig)
        
        stats_str = "\n".join(analysis_results)
        return f"Scan saved to {save_path}\n\nScientific Analysis:\n{stats_str}"
        
    except Exception as e:
        return f"Scan failed: {str(e)}"

@mcp.tool()
def get_surface_profile(x_start: float, y_start: float, x_end: float, y_end: float, num_points: int = 100) -> str:
    """
    Draws a line on the surface and returns the height profile. 
    Coordinates are in meters.
    """
    global mic_server
    try:
        path = [[x_start, y_start], [x_end, y_end]]
        array_list, shape, dtype = mic_server.scan_arbitrary_path(path_points=path, channels=['HeightRetrace'])
        profile_data = np.array(array_list, dtype=dtype).flatten()
        
        save_path = "surface_profile.png"
        plt.figure(figsize=(8, 4))
        plt.plot(np.linspace(0, 1, len(profile_data)), profile_data, 'b-')
        plt.title("Surface Line Profile")
        plt.xlabel("Normalized Distance")
        plt.ylabel("Height (m)")
        plt.grid(True)
        plt.savefig(save_path)
        plt.close()
        
        return f"Profile captured. Max height change: {np.ptp(profile_data):.2e} m. Saved to {save_path}"
    except Exception as e:
        return f"Line profile failed: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")