"""Tests for 3D generator service."""
import pytest


@pytest.mark.asyncio
async def test_generate_cube(three_d_generator_service):
    """Test generating a cube."""
    try:
        assets = await three_d_generator_service.generate_cube(size=100, include_formats=["gltf", "stl"])

        assert len(assets) > 0
        assert any(asset.format == "gltf" for asset in assets)
        assert any(asset.format == "stl" for asset in assets)

        for asset in assets:
            assert asset.data_base64 is not None
            assert asset.filename is not None
            assert asset.size_bytes > 0
    except ImportError:
        pytest.skip("trimesh not installed")


@pytest.mark.asyncio
async def test_generate_cylinder(three_d_generator_service):
    """Test generating a cylinder."""
    try:
        assets = await three_d_generator_service.generate_cylinder(
            radius=50, height=100, include_formats=["gltf"]
        )

        assert len(assets) >= 1
        assert any(asset.format == "gltf" for asset in assets)
    except ImportError:
        pytest.skip("trimesh not installed")


@pytest.mark.asyncio
async def test_generate_sphere(three_d_generator_service):
    """Test generating a sphere."""
    try:
        assets = await three_d_generator_service.generate_sphere(
            radius=50, include_formats=["stl"]
        )

        assert len(assets) >= 1
        assert any(asset.format == "stl" for asset in assets)
    except ImportError:
        pytest.skip("trimesh not installed")
