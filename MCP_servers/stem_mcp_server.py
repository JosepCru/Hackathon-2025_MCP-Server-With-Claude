# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "mcp[cli]>=1.12.3",
#     "pydantic>=2.11.7",
#     "python-dotenv>=1.1.1",
#     "Pyro5>=5.14",
#     "numpy>=1.24.0",
#     "scikit-learn>=1.3.0",
#     "matplotlib>=3.7.2",
#     "requests>=2.32.0",
# ]
# ///

from mcp.server.fastmcp import FastMCP
from typing import List, Tuple, Optional
import numpy as np
import Pyro5.api
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import json
import os
import requests
import sys

mcp = FastMCP("STEMMicroscope")

# Global variable to store the microscope connection
_mic_server = None
_current_data = {
    "spectra": [],
    "locations": [],
    "overview_image": None,
    "pca_results": None,
    "clusters": None
}

def _get_microscope_connection(uri: str = "PYRO:microscope.server@localhost:9091"):
    """Get or create microscope server connection"""
    global _mic_server
    if _mic_server is None:
        _mic_server = Pyro5.api.Proxy(uri)
    return _mic_server

@mcp.tool(
    name="Download_Data_File",
    description="Download a data file from a URL to the current working directory"
)
def download_data_file(url: str, filename: Optional[str] = None) -> str:
    """
    Download a file from a URL.
    
    Args:
        url: URL of the file to download (e.g., https://github.com/.../test_stem.h5)
        filename: Optional custom filename. If not provided, extracts from URL
    """
    try:
        # Extract filename from URL if not provided
        if filename is None:
            filename = url.split('/')[-1]
        
        # Get absolute path for the file
        abs_path = os.path.abspath(filename)
        
        # Download the file
        print(f"Downloading from: {url}", file=sys.stderr)
        print(f"Saving to: {abs_path}", file=sys.stderr)
        
        response = requests.get(url, verify=False, stream=True)
        response.raise_for_status()
        
        # Save the file
        total_size = int(response.headers.get('content-length', 0))
        with open(abs_path, 'wb') as f:
            if total_size == 0:
                f.write(response.content)
            else:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
        
        # Verify file exists
        if os.path.exists(abs_path):
            file_size = os.path.getsize(abs_path)
            return f"File downloaded successfully!\n  URL: {url}\n  Filename: {filename}\n  Absolute path: {abs_path}\n  Size: {file_size:,} bytes"
        else:
            return f"Error: File download failed - file not found at {abs_path}"
            
    except requests.exceptions.RequestException as e:
        return f"Error downloading file: {str(e)}\n  URL: {url}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool(
    name="Initialize_Microscope",
    description="Initialize the STEM microscope connection and optionally register a data file"
)
def initialize_microscope(
    microscope_type: str = "STEM",
    data_file: Optional[str] = None,
    server_uri: str = "PYRO:microscope.server@localhost:9091"
) -> str:
    """
    Initialize microscope and optionally register data.
    
    Args:
        microscope_type: Type of microscope (default: "STEM")
        data_file: Optional H5 data file to register (e.g., "test_stem.h5" or full path)
        server_uri: Pyro5 server URI
    """
    try:
        mic_server = _get_microscope_connection(server_uri)
        mic_server.initialize_microscope(microscope_type)
        
        result = f"Microscope initialized successfully as {microscope_type}"
        
        if data_file:
            # Convert to absolute path
            abs_path = os.path.abspath(data_file)
            
            # Check if file exists
            if not os.path.exists(abs_path):
                return f"Error: File '{data_file}' not found at path: {abs_path}\n\nPlease ensure the file exists or provide the correct path."
            
            mic_server.register_data(abs_path)
            result += f"\nData file registered successfully:\n  Original: {data_file}\n  Absolute path: {abs_path}"
        
        return result
    except Exception as e:
        return f"Error initializing microscope: {str(e)}"

@mcp.tool(
    name="Register_Data_File",
    description="Register a data file (H5 format) with the microscope"
)
def register_data_file(data_file: str) -> str:
    """
    Register a data file with the microscope.
    
    Args:
        data_file: Path to H5 data file (e.g., "test_stem.h5" or full path)
    """
    try:
        # Convert to absolute path
        abs_path = os.path.abspath(data_file)
        
        # Check if file exists
        if not os.path.exists(abs_path):
            return f"Error: File '{data_file}' not found at path: {abs_path}\n\nPlease ensure the file exists or provide the correct path."
        
        mic_server = _get_microscope_connection()
        mic_server.register_data(abs_path)
        
        return f"Data file registered successfully:\n  Original: {data_file}\n  Absolute path: {abs_path}"
    except Exception as e:
        return f"Error registering data file: {str(e)}"

@mcp.tool(
    name="Get_Overview_Image",
    description="Get the overview image from the microscope and store it for visualization"
)
def get_overview_image() -> str:
    """
    Retrieve the overview image from the microscope.
    Returns information about the image shape and dtype.
    """
    try:
        mic_server = _get_microscope_connection()
        array_list, shape, dtype = mic_server.get_overview_image()
        
        # Store the image in global data
        im_array = np.array(array_list, dtype=dtype).reshape(shape)
        _current_data["overview_image"] = im_array
        
        return f"Overview image retrieved successfully.\nShape: {shape}\nDtype: {dtype}\nImage stored in memory for analysis."
    except Exception as e:
        return f"Error getting overview image: {str(e)}"

@mcp.tool(
    name="Get_Point_Spectrum",
    description="Get the spectrum from a specific point (x, y) on the sample"
)
def get_point_spectrum(x: int, y: int, channel: str = "Channel_001") -> str:
    """
    Get spectrum from a specific location.
    
    Args:
        x: X coordinate
        y: Y coordinate
        channel: Channel name (default: "Channel_001")
    """
    try:
        mic_server = _get_microscope_connection()
        array_list, shape, dtype = mic_server.get_point_data(channel, x, y)
        spectrum = np.array(array_list, dtype=dtype).reshape(shape)
        
        return f"Spectrum retrieved from point ({x}, {y}).\nShape: {shape}\nDtype: {dtype}\nSpectrum length: {len(spectrum.flatten())}"
    except Exception as e:
        return f"Error getting spectrum: {str(e)}"

@mcp.tool(
    name="Collect_Grid_Spectra",
    description="Collect spectra from a grid of points. This is useful for clustering and analysis."
)
def collect_grid_spectra(
    grid_size_x: int = 10,
    grid_size_y: int = 10,
    channel: str = "Channel_001"
) -> str:
    """
    Collect spectra from a grid of points.
    
    Args:
        grid_size_x: Number of points in X direction (default: 10)
        grid_size_y: Number of points in Y direction (default: 10)
        channel: Channel name (default: "Channel_001")
    """
    try:
        mic_server = _get_microscope_connection()
        
        spectra = []
        locations = []
        
        for x in range(grid_size_x):
            for y in range(grid_size_y):
                array_list, shape, dtype = mic_server.get_point_data(channel, x, y)
                spectrum = np.array(array_list, dtype=dtype).reshape(shape)
                spectra.append(spectrum.flatten())
                locations.append((x, y))
        
        # Store in global data
        _current_data["spectra"] = np.array(spectra)
        _current_data["locations"] = locations
        
        total_points = grid_size_x * grid_size_y
        return f"Collected {total_points} spectra from {grid_size_x}x{grid_size_y} grid.\nSpectra shape: {_current_data['spectra'].shape}\nData stored in memory for analysis."
    except Exception as e:
        return f"Error collecting spectra: {str(e)}"

@mcp.tool(
    name="Perform_PCA_Analysis",
    description="Perform Principal Component Analysis (PCA) on collected spectra to reduce dimensionality"
)
def perform_pca_analysis(n_components: int = 2) -> str:
    """
    Perform PCA on collected spectra.
    
    Args:
        n_components: Number of principal components (default: 2)
    """
    try:
        if len(_current_data["spectra"]) == 0:
            return "No spectra data available. Please collect spectra first using Collect_Grid_Spectra."
        
        pca = PCA(n_components=n_components)
        data_pca = pca.fit_transform(_current_data["spectra"])
        
        # Store PCA results
        _current_data["pca_results"] = data_pca
        
        explained_variance = pca.explained_variance_ratio_
        
        result = f"PCA completed successfully.\n"
        result += f"Reduced from {_current_data['spectra'].shape[1]} to {n_components} dimensions.\n"
        result += f"PCA shape: {data_pca.shape}\n"
        result += f"Explained variance ratio: {explained_variance}\n"
        result += f"Total variance explained: {sum(explained_variance):.2%}"
        
        return result
    except Exception as e:
        return f"Error performing PCA: {str(e)}"

@mcp.tool(
    name="Perform_Clustering",
    description="Perform K-means clustering on PCA-reduced data or original spectra"
)
def perform_clustering(
    n_clusters: int = 3,
    use_pca: bool = True,
    random_state: int = 42
) -> str:
    """
    Perform K-means clustering.
    
    Args:
        n_clusters: Number of clusters (default: 3)
        use_pca: Use PCA-reduced data if available (default: True)
        random_state: Random state for reproducibility (default: 42)
    """
    try:
        # Determine which data to use
        if use_pca and _current_data["pca_results"] is not None:
            data = _current_data["pca_results"]
            data_type = "PCA-reduced data"
        elif len(_current_data["spectra"]) > 0:
            data = _current_data["spectra"]
            data_type = "original spectra"
        else:
            return "No data available. Please collect spectra first using Collect_Grid_Spectra."
        
        # Perform clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=random_state)
        clusters = kmeans.fit_predict(data)
        
        # Store results
        _current_data["clusters"] = clusters
        
        # Count samples per cluster
        cluster_counts = {}
        for i in range(n_clusters):
            cluster_counts[f"Cluster {i}"] = int(np.sum(clusters == i))
        
        result = f"K-means clustering completed successfully.\n"
        result += f"Data used: {data_type}\n"
        result += f"Number of clusters: {n_clusters}\n"
        result += f"Data shape: {data.shape}\n"
        result += f"\nCluster distribution:\n"
        for cluster, count in cluster_counts.items():
            result += f"  {cluster}: {count} samples\n"
        
        return result
    except Exception as e:
        return f"Error performing clustering: {str(e)}"

@mcp.tool(
    name="Get_Analysis_Summary",
    description="Get a summary of all current analysis results including spectra, PCA, and clustering"
)
def get_analysis_summary() -> str:
    """
    Get a comprehensive summary of current analysis state.
    """
    summary = "=== STEM Analysis Summary ===\n\n"
    
    # Overview image
    if _current_data["overview_image"] is not None:
        summary += f"Overview Image: Available (shape: {_current_data['overview_image'].shape})\n\n"
    else:
        summary += "Overview Image: Not loaded\n\n"
    
    # Spectra
    if len(_current_data["spectra"]) > 0:
        summary += f"Spectra Data:\n"
        summary += f"  - Number of spectra: {len(_current_data['spectra'])}\n"
        summary += f"  - Spectrum length: {_current_data['spectra'].shape[1]}\n"
        summary += f"  - Locations: {len(_current_data['locations'])} points\n\n"
    else:
        summary += "Spectra Data: No spectra collected\n\n"
    
    # PCA
    if _current_data["pca_results"] is not None:
        summary += f"PCA Results:\n"
        summary += f"  - Shape: {_current_data['pca_results'].shape}\n"
        summary += f"  - Components: {_current_data['pca_results'].shape[1]}\n\n"
    else:
        summary += "PCA Results: Not performed\n\n"
    
    # Clustering
    if _current_data["clusters"] is not None:
        n_clusters = len(np.unique(_current_data["clusters"]))
        summary += f"Clustering Results:\n"
        summary += f"  - Number of clusters: {n_clusters}\n"
        summary += f"  - Samples clustered: {len(_current_data['clusters'])}\n"
    else:
        summary += "Clustering Results: Not performed\n"
    
    return summary

@mcp.tool(
    name="Export_Analysis_Data",
    description="Export current analysis data as JSON for further processing"
)
def export_analysis_data() -> str:
    """
    Export analysis data in JSON format.
    Returns cluster assignments and locations if available.
    """
    try:
        export_data = {}
        
        if _current_data["clusters"] is not None and len(_current_data["locations"]) > 0:
            export_data["cluster_map"] = [
                {
                    "location": {"x": loc[0], "y": loc[1]},
                    "cluster": int(_current_data["clusters"][i])
                }
                for i, loc in enumerate(_current_data["locations"])
            ]
        
        if _current_data["pca_results"] is not None:
            export_data["pca_summary"] = {
                "shape": list(_current_data["pca_results"].shape),
                "n_components": _current_data["pca_results"].shape[1]
            }
        
        if len(export_data) == 0:
            return "No analysis data available to export."
        
        return json.dumps(export_data, indent=2)
    except Exception as e:
        return f"Error exporting data: {str(e)}"

@mcp.tool(
    name="Reset_Analysis",
    description="Clear all stored analysis data and start fresh"
)
def reset_analysis() -> str:
    """
    Reset all stored analysis data.
    """
    _current_data["spectra"] = []
    _current_data["locations"] = []
    _current_data["overview_image"] = None
    _current_data["pca_results"] = None
    _current_data["clusters"] = None
    
    return "All analysis data has been reset. Ready for new analysis."

if __name__ == "__main__":
    mcp.run(transport="stdio")