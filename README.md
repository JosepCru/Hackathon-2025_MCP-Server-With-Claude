# 🔬 AI & ML for Microscopy Hackathon - MCP Server Project

<div align="center">

**Control STEM & AFM Digital Twins through Natural Language using Claude and MCP**

[Overview](#-overview) • [Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Architecture](#-architecture) • [Troubleshooting](#-troubleshooting)

</div>

---

## 📖 Overview

This project was developed for the **[AI and ML for Microscopy Hackathon](https://kaliningroup.github.io/mic_hackathon_2/)**, demonstrating the power of combining **Model Context Protocol (MCP)** with Claude AI to control scientific instruments through natural language.

### 🎯 The Challenge

The hackathon provided Python scripts for controlling digital twin simulations of STEM (Scanning Transmission Electron Microscope) and AFM (Atomic Force Microscope) instruments via Pyro5 servers. 

### 💡 Our Solution

We created **three MCP servers** that translate complex microscopy operations into simple, natural language commands that Claude can understand and execute. This allows researchers to:

- Control microscopes using conversational AI
- Perform complex analyses without writing code
- Visualize and interpret results automatically
- Chain multiple operations seamlessly

### 👥 Team

- **Josep Cru** - [@JosepCru](https://github.com/JosepCru)
- **Fanzhi Su**

---

## ✨ Features

### 🔬 Three Specialized MCP Servers

<table>
<tr>
<td width="33%" valign="top">

#### 1️⃣ STEM Digital Twin
**File:** `stem_mcp_server.py`

🎯 **Capabilities:**
- Download & register H5 data files
- Initialize STEM microscope
- Capture overview images
- Collect point & grid spectra
- Perform PCA analysis
- K-means clustering
- Generate visualizations
- Export analysis data

📊 **Use Cases:**
- Spectroscopic analysis
- Material composition mapping
- Pattern recognition
- Statistical analysis

</td>
<td width="33%" valign="top">

#### 2️⃣ AFM Digital Twin
**File:** `AFM_DT.py`

🎯 **Capabilities:**
- Test Pyro5 connection
- Initialize AFM with H5 data
- Full 2D scanning
- Individual line scans
- Arbitrary path scanning
- Simulate scanning imperfections
- Multiple channel support

📊 **Use Cases:**
- Surface topography
- Height mapping
- Phase imaging
- Custom trajectory scanning

</td>
<td width="33%" valign="top">

#### 3️⃣ Particle Segmentation
**File:** `particle_detection_mcp.py`

🎯 **Capabilities:**
- Load PyTorch models
- Segment microscopy images
- Detect particles/features
- Generate visualizations
- Save annotated results

📊 **Use Cases:**
- Particle detection
- Feature extraction
- Image segmentation
- Automated analysis

⚠️ **Status:** Experimental - Some compatibility issues with Claude Desktop

</td>
</tr>
</table>

---

## 🚀 Installation

### Prerequisites

- **Python 3.12+** (required for MCP servers)
- **Claude Desktop App** (not Claude Code CLI)
- **Hackathon Pyro5 servers** (provided by organizers)
- **H5 data files** (provided by hackathon)

### Step 1: Clone the Repository

```bash
git clone https://github.com/JosepCru/Hackathon-2025_MCP-Server-With-Claude.git
cd Hackathon-2025_MCP-Server-With-Claude
```

### Step 2: Verify Python Dependencies

The MCP servers use inline script metadata (PEP 723), so dependencies are automatically managed. Each script includes its requirements:

```python
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "mcp[cli]>=1.12.3",
#     "Pyro5>=5.14",
#     "numpy>=1.24.0",
#     # ... more dependencies
# ]
# ///
```

### Step 3: Start Hackathon Pyro5 Servers

Before using the MCP servers, start the appropriate Pyro5 servers:

```bash
# For STEM microscope (port 9091)
python run_server_stem.py

# For AFM microscope (port 9092)
python run_server_afm.py
```

### Step 4: Configure Claude Desktop

Add the MCP servers to your Claude Desktop configuration file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

**Linux:** `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "stem-microscope": {
      "command": "python",
      "args": [
        "/absolute/path/to/stem_mcp_server.py"
      ]
    },
    "afm-microscope": {
      "command": "python",
      "args": [
        "/absolute/path/to/AFM_DT.py"
      ]
    },
    "particle-segmentation": {
      "command": "python",
      "args": [
        "/absolute/path/to/particle_detection_mcp.py"
      ]
    }
  }
}
```

⚠️ **Important:** Use **absolute paths** to the Python scripts!

### Step 5: Restart Claude Desktop

Completely quit and restart the Claude Desktop app for the changes to take effect.

---

## 💻 Usage

### 🔬 STEM Digital Twin Examples

#### Example 1: Basic Setup & Analysis

```
You: Can you help me analyze a STEM dataset? First, download the test data from 
the hackathon GitHub, then initialize the microscope and show me an overview image.

Claude: I'll help you set up the STEM microscope analysis...
[Downloads data file]
[Initializes microscope]
[Displays overview image with statistics]
```

#### Example 2: Spectral Analysis & Clustering

```
You: Collect spectra from a 5x5 grid, then perform PCA with 3 components 
and cluster the results into 4 groups.

Claude: I'll collect the spectral data and perform the analysis...
[Collects 25 spectra from grid]
[Performs PCA dimensionality reduction]
[Runs K-means clustering with 4 clusters]
[Generates visualization showing cluster distribution]
```

#### Example 3: Targeted Point Analysis

```
You: Get the spectrum at position (50, 75) and tell me what you observe.

Claude: [Retrieves spectrum at coordinates]
Here's the spectral analysis for that location:
- Peak intensity: [values]
- Notable features: [analysis]
```

### 🔬 AFM Digital Twin Examples

#### Example 1: Full Surface Scan

```
You: Initialize the AFM with the dataset, then do a full scan of the 
Height and Phase channels in horizontal direction.

Claude: I'll set up the AFM and perform a complete surface scan...
[Initializes AFM with H5 file]
[Performs 2D scan on both channels]
[Returns scan statistics and image info]
```

#### Example 2: Line Profile Analysis

```
You: Scan a vertical line at x = -0.5 micrometers for the Amplitude channel.

Claude: [Performs line scan at specified coordinate]
Line scan results:
- 256 data points collected
- Min amplitude: 2.3e-9
- Max amplitude: 8.7e-9
```

#### Example 3: Custom Path Scanning

```
You: Scan along a path connecting these three points: 
(-2, 2), (1, 1.8), and (2.1, 2) micrometers. Use the Phase channel.

Claude: [Performs arbitrary path scan]
Path scan completed along 3 waypoints...
```

### 🎨 Particle Segmentation Examples

#### Example 1: Segment an Image

```
You: Can you segment the microscopy image at /path/to/image.png 
and show me where the particles are?

Claude: I'll load the segmentation model and analyze the image...
[Loads PyTorch model]
[Processes image]
[Generates side-by-side visualization]
Results saved to: segmentation_results/segmentation_20250119_143022.png
Detected 47 particles in the image.
```

⚠️ **Note:** The segmentation server currently has some compatibility issues with Claude Desktop. We're investigating the root cause.

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Claude Desktop App                       │
│                  (Natural Language Interface)                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ MCP Protocol (stdio)
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼────────┐ ┌────▼─────────┐ ┌───▼──────────────┐
│ STEM MCP       │ │ AFM MCP      │ │ Segmentation MCP │
│ Server         │ │ Server       │ │ Server           │
│ (FastMCP)      │ │ (MCP Server) │ │ (FastMCP)        │
└───────┬────────┘ └────┬─────────┘ └───┬──────────────┘
        │               │                │
        │ Pyro5         │ Pyro5          │
        │ RPC           │ RPC            │
        │               │                │
┌───────▼────────┐ ┌────▼─────────┐ ┌───▼──────────────┐
│ STEM Digital   │ │ AFM Digital  │ │ PyTorch Model    │
│ Twin Server    │ │ Twin Server  │ │ (model.pt)       │
│ (port 9091)    │ │ (port 9092)  │ │                  │
└───────┬────────┘ └────┬─────────┘ └──────────────────┘
        │               │
        │               │
┌───────▼───────────────▼─────────┐
│     H5 Data Files               │
│  (test_stem.h5, dset_spm1.h5)  │
└─────────────────────────────────┘
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **MCP Servers** | Python 3.12 + FastMCP / MCP SDK | Bridge between Claude and instruments |
| **Communication** | Pyro5 (Python Remote Objects) | RPC for digital twin servers |
| **Data Format** | HDF5 (.h5 files) | Scientific data storage |
| **Analysis** | NumPy, scikit-learn | Data processing & ML |
| **Visualization** | Matplotlib | Generate analysis plots |
| **Segmentation** | PyTorch | Deep learning model inference |
| **Transport** | stdio | MCP protocol communication |

---

## 🔧 Technical Details

### STEM MCP Server (`stem_mcp_server.py`)

**Transport:** stdio  
**Framework:** FastMCP  
**Pyro5 URI:** `PYRO:microscope.server@localhost:9091`

**Available Tools:**

| Tool Name | Description | Key Parameters |
|-----------|-------------|----------------|
| `Download_Data_File` | Download H5 files from URLs | `url`, `filename` |
| `Initialize_Microscope` | Connect and initialize STEM | `microscope_type`, `data_file` |
| `Register_Data_File` | Register H5 data with microscope | `data_file` |
| `Get_Overview_Image` | Retrieve overview scan image | - |
| `Get_Point_Spectrum` | Get spectrum at specific pixel | `x`, `y`, `channel` |
| `Collect_Grid_Spectra` | Collect spectra from NxM grid | `grid_size_x`, `grid_size_y` |
| `Perform_PCA_Analysis` | Dimensionality reduction via PCA | `n_components` |
| `Perform_Clustering` | K-means clustering on data | `n_clusters`, `use_pca` |
| `Get_Analysis_Summary` | Summary of current analysis state | - |
| `Export_Analysis_Data` | Export results as JSON | - |
| `Reset_Analysis` | Clear all stored data | - |

**Output:** Saves images to `stem_analysis_images/` directory

### AFM MCP Server (`AFM_DT.py`)

**Transport:** stdio  
**Framework:** MCP SDK (standard)  
**Pyro5 URI:** `PYRO:microscope.server@localhost:9092`

**Available Tools:**

| Tool Name | Description | Key Parameters |
|-----------|-------------|----------------|
| `test_connection` | Verify Pyro5 server connectivity | - |
| `initialize_afm` | Initialize with H5 dataset | `data_path`, `data_source` |
| `get_full_scan` | Complete 2D scan acquisition | `channels`, `modification`, `direction`, `trace` |
| `scan_individual_line` | Scan single line (H or V) | `direction`, `coord`, `channels` |
| `scan_arbitrary_path` | Scan along custom trajectory | `corners`, `channels` |

**Scan Modifications:**
- `None`: Ideal scanning
- `broken_tip`: Simulate tip damage
- `bad_pid`: Simulate poor feedback control

**Available Channels:**
- Height (Trace/Retrace)
- Amplitude (Trace/Retrace)
- Phase (Trace/Retrace)

### Particle Segmentation MCP Server (`particle_detection_mcp.py`)

**Transport:** stdio  
**Framework:** FastMCP  
**Model:** PyTorch (CPU inference)

**Available Tools:**

| Tool Name | Description | Key Parameters |
|-----------|-------------|----------------|
| `Check_Model_Status` | Verify model is loaded | - |
| `Segment_Image` | Apply segmentation to image | `image_path` |

**Output:** Saves images to `segmentation_results/` directory

⚠️ **Known Issue:** This server has compatibility issues with Claude Desktop. We suspect it may be related to:
- Model loading time (timeout issues)
- Memory requirements
- FastMCP vs standard MCP SDK differences

---

## 🐛 Troubleshooting

### Common Issues

#### Issue 1: "Failed to connect to Pyro5 server"

**Symptoms:**
```
❌ Failed to connect to STEM/AFM server: [Errno 61] Connection refused
Make sure 'run_server_stem' or 'run_server_afm' is running!
```

**Solutions:**
1. Verify the appropriate Pyro5 server is running:
   ```bash
   # Check if server is running
   lsof -i :9091  # For STEM
   lsof -i :9092  # For AFM
   ```

2. Start the server if not running:
   ```bash
   python run_server_stem.py  # For STEM
   python run_server_afm.py   # For AFM
   ```

3. Check firewall settings allow localhost connections

#### Issue 2: "MCP server not appearing in Claude"

**Solutions:**
1. Verify configuration file path is correct
2. Ensure you used **absolute paths** in the config
3. Completely quit and restart Claude Desktop (not just close the window)
4. Check Claude Desktop logs:
   ```bash
   # macOS
   tail -f ~/Library/Logs/Claude/mcp*.log
   
   # Windows
   type %APPDATA%\Claude\logs\mcp-server-*.log
   ```

#### Issue 3: "File not found" errors

**Solutions:**
1. Use absolute paths for H5 files:
   ```python
   # ❌ Bad
   "test_stem.h5"
   
   # ✅ Good
   "/Users/username/hackathon/data/test_stem.h5"
   ```

2. Verify file exists:
   ```bash
   ls -la /path/to/file.h5
   ```

#### Issue 4: Particle Segmentation not working

**Current Status:** Under investigation 🔍

**Possible causes:**
- Model loading timeout
- Memory issues with large models
- FastMCP compatibility with PyTorch
- File path issues with model loading

**Workaround:**
Use the STEM and AFM servers for now. The segmentation functionality can be accessed directly via the Python script if needed.

#### Issue 5: "Module not found" errors

**Solution:**
The inline script metadata should handle dependencies automatically. If you see import errors:

```bash
# Manually install dependencies
pip install mcp[cli]>=1.12.3 Pyro5>=5.14 numpy>=1.24.0 scikit-learn>=1.3.0 matplotlib>=3.7.2
```

### Debug Mode

Enable verbose logging in the MCP servers by checking stderr output:

```python
# The servers write debug info to stderr
print(f"Debug: {info}", file=sys.stderr)
```

View in Claude Desktop logs to see detailed execution traces.

---

## 📚 Additional Resources

### Hackathon Resources

- **Official Website:** [AI and ML for Microscopy Hackathon](https://microscopy-hackathon.org/)
- **H5 Data Files:** Provided by hackathon organizers
- **Pyro5 Servers:** `run_server_stem.py`, `run_server_afm.py` (from hackathon)

### MCP Protocol

- [Model Context Protocol Specification](https://spec.modelcontextprotocol.io)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Claude MCP Integration Guide](https://docs.anthropic.com/en/docs/build-with-claude/mcp)

### Scientific Computing

- [HDF5 Format](https://www.hdfgroup.org/solutions/hdf5/)
- [Pyro5 Documentation](https://pyro5.readthedocs.io/)
- [NumPy](https://numpy.org/)
- [scikit-learn](https://scikit-learn.org/)

---

## 🎓 What We Learned

This project demonstrates several key concepts:

1. **Natural Language Interfaces for Scientific Instruments**: By wrapping complex APIs in MCP servers, we make scientific instruments accessible through conversation.

2. **Bridging Legacy Systems**: The Pyro5 servers represent existing infrastructure. MCP provides a modern interface without requiring changes to the underlying systems.

3. **Compositional AI Tools**: Claude can chain multiple tool calls together, enabling complex workflows like "download → initialize → scan → analyze → visualize" from a single request.

4. **Rapid Prototyping**: MCP's simplicity allowed us to build three functional servers during the hackathon timeframe.

5. **Challenges with Complex Dependencies**: The segmentation server highlighted potential issues when integrating heavy ML frameworks (PyTorch) with MCP.

---

## 🚧 Future Improvements

- [ ] Fix particle segmentation server compatibility issues
- [ ] Add real-time progress indicators for long-running operations
- [ ] Implement caching for frequently-accessed data
- [ ] Add batch processing capabilities
- [ ] Create web-based visualization dashboard
- [ ] Support for more microscopy file formats
- [ ] Integration with additional analysis libraries
- [ ] Add automated report generation

---

## 🙏 Acknowledgments

- **Hackathon Organizers** at [Microscopy Hackathon](https://microscopy-hackathon.org/) for providing the digital twin servers and data
- **Anthropic** for Claude and the Model Context Protocol
- **Python Scientific Computing Community** for the excellent tools (NumPy, scikit-learn, Matplotlib)
- **FastMCP** developers for the simplified MCP server framework

---

## 📞 Contact & Links

**Team Members:**
- Josep Cru - [@JosepCru](https://github.com/JosepCru)
- Fanzhi Su

**Project Repository:** [github.com/JosepCru/Hackathon-2025_MCP-Server-With-Claude](https://github.com/JosepCru/Hackathon-2025_MCP-Server-With-Claude)

**Hackathon:** [AI and ML for Microscopy Hackathon](https://microscopy-hackathon.org/)

---

<div align="center">

**Built with 🔬 for the AI & ML for Microscopy Hackathon**

⭐ Star this repo if you find it useful!

</div>
