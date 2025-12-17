# 3D Software Renderer

A high-performance CPU-based 3D rendering engine written in Python with Numba JIT compilation. Features real-time mesh rendering, shadow mapping, diffuse lighting, and texture mapping.

## ✨ Features

- **Pure CPU Rendering**: Software rasterization with parallel processing support
- **Real-time Performance**: Numba JIT compilation for near-native speed
- **Shadow Mapping**: Dynamic shadow generation from multiple light sources
- **Diffuse Lighting**: Per-triangle lighting calculations with ambient + directional components
- **Texture Mapping**: Full UV texture support with perspective-correct interpolation
- **3D Scene Loading**: Load meshes from GLTF/GLB files using Trimesh
- **Interactive Camera**: FPS-style camera controls with mouse look
- **Object Selection**: Click-to-select objects with bounding box visualization
- **Multi-threading**: Configurable parallel rendering across CPU cores

## 📋 Requirements

- Python 3.8+
- NumPy
- Numba
- PySDL2
- Trimesh
- SciPy
- PIL (Pillow)

## 🚀 Installation

```bash
# Install dependencies
pip install numpy numba pysdl2 pysdl2-dll trimesh scipy pillow

## 💻 Usage

### Basic Example

```python
from renderer import Renderer
from loader.mesh_loader import load_scene

# Initialize renderer
renderer = Renderer(width=800, height=600, title="My 3D Scene")

# Load 3D scene
meshes, texs, uvs, nodes, bounds, positions, rotations = load_scene("path/to/model.glb", nom_mesh=True)

# Add meshes to renderer
for i in range(len(meshes)):
    renderer.add_mesh(
        position=positions[i],
        pivot=(0, 0, 0),
        rotation=rotations[i],
        loaded_meshes=meshes[i],
        loaded_texs=texs[i],
        loaded_uvs=uvs[i],
        aabb_data=bounds[i]
    )

# Add light source
light_id = renderer.add_light(
    position=(0.0, 10.0, 0.0),
    target=(0.0, 0.0, 0.0)
)

# Set camera
renderer.set_camera_position((0.0, 5.0, -10.0))
renderer.set_camera_target((0.0, 0.0, 0.0))

# Render loop
renderer.show()
while running:
    renderer.render_meshes()
    renderer.render_lights()
    renderer.present()
```

### Running the Demo

The `main.py` file provides a complete example application that demonstrates the renderer's capabilities. It includes:
- JIT compilation warmup and diagnostics
- Loading a 3D scene (chess pieces from GLB file)
- Setting up lights and camera
- Interactive FPS-style controls
- Real-time rendering with performance statistics

```bash
python main.py
```

**Note**: Make sure you have a `res/chess_pieces.glb` file or modify the path in `main.py` to load your own 3D model.

## 🎮 Controls

| Input | Action |
|-------|--------|
| **W/A/S/D** | Move camera forward/left/backward/right |
| **Space** | Move camera up |
| **Ctrl** | Move camera down |
| **Mouse** | Look around (when window focused) |
| **Left Click** | Select object under cursor |
| **E / Q** | Cycle through objects |
| **Arrow Keys** | Move selected object |
| **Tab** | Reset camera to look at origin |
| **Esc** | Release mouse capture |

## 🏗️ Architecture

### Core Modules

- **`core.py`** - Main renderer class with scene management
- **`rasterizer.py`** - Triangle rasterization and rendering pipeline
- **`math3d.py`** - 3D math operations (matrices, transformations, projections)
- **`geometry.py`** - Clipping and polygon triangulation
- **`shadow_mapping.py`** - Shadow map generation and shadow testing
- **`lighting.py`** - Diffuse lighting calculations
- **`mesh_loader.py`** - 3D model loading from GLTF/GLB files
- **`setting.py`** - Configuration constants and type definitions
- **`compiler.py`** - JIT compilation warmup utilities

### Rendering Pipeline

```
┌─────────────────┐
│  Load Meshes    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Transform (MVP) │ ◄── Model-View-Projection matrices
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Frustum Culling │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Clipping        │ ◄── Clip against view frustum
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Rasterization   │ ◄── Perspective-correct interpolation
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Shadow Testing  │ ◄── Check shadow maps
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Lighting        │ ◄── Apply diffuse lighting
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Texture Mapping │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Framebuffer     │
└─────────────────┘
```

## ⚙️ Configuration

Key settings in `setting.py`:

```python
DEFAULT_WIDTH = 800      # Window width
DEFAULT_HEIGHT = 600     # Window height
DEFAULT_FOV = 90         # Field of view (degrees)
AMBIENT = 0.3            # Ambient light intensity
INTENSITY = 0.8          # Diffuse light intensity
MAX_TRIS = 112000        # Maximum triangles per frame
MAX_MESHES = 100         # Maximum mesh objects
```

## 🔧 API Reference

### Renderer Class

#### Initialization
```python
renderer = Renderer(width=800, height=600, title="3D Renderer")
```

#### Mesh Management
```python
mesh_id = renderer.add_mesh(position, pivot, rotation, loaded_meshes, loaded_texs, loaded_uvs, aabb_data)
renderer.set_mesh_transform(mesh_id, position=(x, y, z))
renderer.set_mesh_visible_flag(mesh_id, visible=True)
renderer.remove_mesh(mesh_id)
```

#### Lighting
```python
light_id = renderer.add_light(position=(x, y, z), target=(tx, ty, tz))
renderer.set_light_transform(light_id, position=(x, y, z))
renderer.set_light_active_flag(light_id, enabled=True)
renderer.update_light()  # Refresh shadow maps
```

#### Camera Control
```python
renderer.set_camera_position((x, y, z))
renderer.set_camera_target((x, y, z))
renderer.move_camera(forward=1.0, right=0.5, up=0.0)
renderer.rotate_camera(yaw, pitch)
```

#### Rendering
```python
renderer.render_meshes()              # Render all meshes
renderer.render_lights()              # Render light gizmos
renderer.render_bounding_box(idx, width, color)
renderer.present()                    # Display frame
```

## 🎯 Performance Tips

1. **Polygon Count**: Keep triangle count under 50,000 for smooth 60 FPS
2. **Texture Size**: Use power-of-2 textures (256x256, 512x512, 1024x1024)
3. **Parallel Mode**: Enable parallel rendering for multi-core CPUs
4. **Shadow Resolution**: Match shadow map resolution to viewport
5. **Culling**: Utilize visibility flags to skip rendering hidden objects

## 🐛 Known Limitations

- No texture filtering (nearest-neighbor only)
- No transparency/alpha blending
- Shadow maps use single depth buffer (no soft shadows)

## 🔬 Technical Details

- **Coordinate System**: Right-handed, Y-up
- **Clip Space**: OpenGL-style [-1, 1] normalized device coordinates
- **Depth Buffer**: 32-bit float Z-buffer with depth testing
- **Shadow Bias**: 0.005 (configurable in `shadow_mapping.py`)
- **Backface Culling**: Enabled by default (view-space normals)

## 📝 File Structure

```
├── main.py                 # Demo application entry point
├── compiler.py             # JIT compilation warmup
├── renderer/
│   ├── core.py            # Main renderer class
│   ├── rasterizer.py      # Rasterization engine
│   ├── math3d.py          # 3D mathematics
│   ├── geometry.py        # Clipping & triangulation
│   ├── shadow_mapping.py  # Shadow generation
│   ├── lighting.py        # Lighting calculations
│   └── setting.py         # Configuration
└── loader     # 3D model loading
```

## 🙏 Acknowledgments

- Built with [Numba](https://numba.pydata.org/) for JIT compilation
- Uses [Trimesh](https://trimsh.org/) for 3D model loading
- Rendering powered by [PySDL2](https://pysdl2.readthedocs.io/)

## 📧 Contact

For questions or feedback, please open an issue on GitHub.
