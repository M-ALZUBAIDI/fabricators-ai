"""3D asset generation service."""
import logging
import base64
from io import BytesIO
from typing import Tuple, Optional

from models import Design3DAsset

logger = logging.getLogger(__name__)


class ThreeDGeneratorService:
    """Service for generating 3D assets (GLTF and STL)."""

    def __init__(self):
        self.supported_formats = ["gltf", "stl"]

    async def generate_cube(
        self, size: float = 100, include_formats: list = None
    ) -> list[Design3DAsset]:
        """Generate a simple cube in specified formats."""
        if include_formats is None:
            include_formats = ["gltf", "stl"]

        assets = []

        try:
            import trimesh
            import numpy as np

            # Create cube mesh
            mesh = trimesh.creation.box(extents=[size, size, size])

            for format_type in include_formats:
                if format_type.lower() == "gltf":
                    asset = await self._generate_gltf(mesh, "cube")
                    if asset:
                        assets.append(asset)
                elif format_type.lower() == "stl":
                    asset = await self._generate_stl(mesh, "cube")
                    if asset:
                        assets.append(asset)

            logger.info(f"Generated cube with {len(assets)} formats")
            return assets

        except Exception as e:
            logger.error(f"Error generating cube: {e}")
            return []

    async def generate_cylinder(
        self, radius: float = 50, height: float = 100, include_formats: list = None
    ) -> list[Design3DAsset]:
        """Generate a cylinder in specified formats."""
        if include_formats is None:
            include_formats = ["gltf", "stl"]

        assets = []

        try:
            import trimesh

            # Create cylinder mesh
            mesh = trimesh.creation.cylinder(radius=radius, height=height)

            for format_type in include_formats:
                if format_type.lower() == "gltf":
                    asset = await self._generate_gltf(mesh, "cylinder")
                    if asset:
                        assets.append(asset)
                elif format_type.lower() == "stl":
                    asset = await self._generate_stl(mesh, "cylinder")
                    if asset:
                        assets.append(asset)

            logger.info(f"Generated cylinder with {len(assets)} formats")
            return assets

        except Exception as e:
            logger.error(f"Error generating cylinder: {e}")
            return []

    async def generate_sphere(
        self, radius: float = 50, include_formats: list = None
    ) -> list[Design3DAsset]:
        """Generate a sphere in specified formats."""
        if include_formats is None:
            include_formats = ["gltf", "stl"]

        assets = []

        try:
            import trimesh

            # Create sphere mesh
            mesh = trimesh.creation.icosphere(radius=radius)

            for format_type in include_formats:
                if format_type.lower() == "gltf":
                    asset = await self._generate_gltf(mesh, "sphere")
                    if asset:
                        assets.append(asset)
                elif format_type.lower() == "stl":
                    asset = await self._generate_stl(mesh, "sphere")
                    if asset:
                        assets.append(asset)

            logger.info(f"Generated sphere with {len(assets)} formats")
            return assets

        except Exception as e:
            logger.error(f"Error generating sphere: {e}")
            return []

    async def _generate_gltf(
        self, mesh, name: str = "object"
    ) -> Optional[Design3DAsset]:
        """Generate GLTF format from mesh."""
        try:
            # Export to GLTF (returns dict with file contents)
            gltf_data = mesh.export(file_type='gltf')

            # gltf_data is a dict with keys like 'model.gltf', 'gltf_buffer_0.bin', etc.
            # Use the model.gltf which contains the JSON structure
            if isinstance(gltf_data, dict):
                if 'model.gltf' in gltf_data:
                    gltf_bytes = gltf_data['model.gltf']
                else:
                    # If no model.gltf, just use first value
                    gltf_bytes = next(iter(gltf_data.values()))
            else:
                gltf_bytes = gltf_data if isinstance(gltf_data, bytes) else gltf_data.encode()

            # Encode to base64
            gltf_base64 = base64.b64encode(gltf_bytes).decode()

            return Design3DAsset(
                format="gltf",
                data_base64=gltf_base64,
                filename=f"{name}.gltf",
                size_bytes=len(gltf_bytes),
            )

        except Exception as e:
            logger.error(f"Error generating GLTF: {e}")
            return None

    async def _generate_stl(
        self, mesh, name: str = "object"
    ) -> Optional[Design3DAsset]:
        """Generate STL format from mesh."""
        try:
            import trimesh

            # Export to STL
            stl_bytes = trimesh.exchange.stl.export_stl(mesh)

            # Encode to base64
            stl_base64 = base64.b64encode(stl_bytes).decode()

            return Design3DAsset(
                format="stl",
                data_base64=stl_base64,
                filename=f"{name}.stl",
                size_bytes=len(stl_bytes),
            )

        except Exception as e:
            logger.error(f"Error generating STL: {e}")
            return None

    async def generate_from_spec(
        self, spec_dict: dict, include_formats: list = None
    ) -> list[Design3DAsset]:
        """Generate 3D asset from design specification."""
        if include_formats is None:
            include_formats = ["gltf", "stl"]

        # Extract common parameters
        shape_type = spec_dict.get("shape", "cube").lower()
        size = spec_dict.get("size", 100)
        radius = spec_dict.get("radius", 50)
        height = spec_dict.get("height", 100)

        # Generate based on shape type
        if shape_type == "cube":
            return await self.generate_cube(size, include_formats)
        elif shape_type == "cylinder":
            return await self.generate_cylinder(radius, height, include_formats)
        elif shape_type == "sphere":
            return await self.generate_sphere(radius, include_formats)
        else:
            logger.warning(f"Unknown shape type: {shape_type}, defaulting to cube")
            return await self.generate_cube(size, include_formats)
