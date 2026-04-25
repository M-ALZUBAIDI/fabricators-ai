"""Configuration module."""
from config.settings import Settings, get_settings
from config.development import DevelopmentSettings
from config.production import ProductionSettings

__all__ = ["Settings", "get_settings", "DevelopmentSettings", "ProductionSettings"]
