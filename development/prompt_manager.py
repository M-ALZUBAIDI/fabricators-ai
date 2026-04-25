"""Prompt engineering management system for easy modification and versioning."""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Prompts directory
PROMPTS_DIR = Path("prompts")
PROMPTS_DIR.mkdir(exist_ok=True)


class PromptVersion:
    """Represents a version of a prompt."""

    def __init__(
        self,
        name: str,
        version: str,
        content: str,
        description: str = "",
        tags: List[str] = None,
    ):
        self.name = name
        self.version = version
        self.content = content
        self.description = description
        self.tags = tags or []
        self.created_at = datetime.now().isoformat()

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "name": self.name,
            "version": self.version,
            "content": self.content,
            "description": self.description,
            "tags": self.tags,
            "created_at": self.created_at,
        }


class PromptManager:
    """Manage prompt versions and experiments."""

    def __init__(self):
        self.prompts: Dict[str, List[PromptVersion]] = {}
        self.active_prompts: Dict[str, str] = {}  # prompt_name -> version

    def create_prompt(
        self,
        name: str,
        content: str,
        version: str = "1.0",
        description: str = "",
        tags: List[str] = None,
    ) -> PromptVersion:
        """
        Create a new prompt or version.

        Args:
            name: Prompt name (e.g., "fabrication_assistant", "report_generator")
            content: The actual prompt text
            version: Version string (e.g., "1.0", "1.1", "2.0")
            description: What changed in this version
            tags: Tags for categorization

        Returns:
            PromptVersion object
        """
        prompt = PromptVersion(name, version, content, description, tags)

        if name not in self.prompts:
            self.prompts[name] = []

        self.prompts[name].append(prompt)
        logger.info(f"Created prompt: {name} v{version}")

        return prompt

    def set_active_prompt(self, name: str, version: str):
        """Set which version is active for a prompt."""
        if name not in self.prompts:
            raise ValueError(f"Prompt {name} not found")

        # Check version exists
        versions = [p.version for p in self.prompts[name]]
        if version not in versions:
            raise ValueError(f"Version {version} not found for prompt {name}")

        self.active_prompts[name] = version
        logger.info(f"Activated: {name} v{version}")

    def get_active_prompt(self, name: str) -> Optional[str]:
        """Get the active prompt content."""
        if name not in self.active_prompts:
            # Return latest version if not explicitly set
            if name in self.prompts and self.prompts[name]:
                return self.prompts[name][-1].content
            return None

        version = self.active_prompts[name]
        for p in self.prompts[name]:
            if p.version == version:
                return p.content
        return None

    def get_prompt_versions(self, name: str) -> List[PromptVersion]:
        """Get all versions of a prompt."""
        return self.prompts.get(name, [])

    def save_prompts(self, filename: str = "prompts_backup.json"):
        """Save all prompts to JSON file."""
        filepath = PROMPTS_DIR / filename

        data = {
            "timestamp": datetime.now().isoformat(),
            "prompts": {
                name: [p.to_dict() for p in versions]
                for name, versions in self.prompts.items()
            },
            "active_prompts": self.active_prompts,
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Prompts saved to {filepath}")
        return filepath

    def load_prompts(self, filename: str = "prompts_backup.json"):
        """Load prompts from JSON file."""
        filepath = PROMPTS_DIR / filename

        if not filepath.exists():
            logger.warning(f"Prompts file not found: {filepath}")
            return

        with open(filepath, "r") as f:
            data = json.load(f)

        self.prompts = {}
        for name, versions in data.get("prompts", {}).items():
            self.prompts[name] = [
                PromptVersion(
                    name=v["name"],
                    version=v["version"],
                    content=v["content"],
                    description=v.get("description", ""),
                    tags=v.get("tags", []),
                )
                for v in versions
            ]

        self.active_prompts = data.get("active_prompts", {})
        logger.info(f"Prompts loaded from {filepath}")

    def compare_versions(self, name: str, version1: str, version2: str):
        """Compare two versions of a prompt."""
        p1 = self._get_prompt_version(name, version1)
        p2 = self._get_prompt_version(name, version2)

        if not p1 or not p2:
            return None

        return {
            "version1": {
                "version": p1.version,
                "content": p1.content,
                "description": p1.description,
            },
            "version2": {
                "version": p2.version,
                "content": p2.content,
                "description": p2.description,
            },
        }

    def _get_prompt_version(
        self, name: str, version: str
    ) -> Optional[PromptVersion]:
        """Get a specific prompt version."""
        for p in self.prompts.get(name, []):
            if p.version == version:
                return p
        return None

    def print_status(self):
        """Print current prompt status."""
        print("\n" + "="*80)
        print("PROMPT MANAGEMENT STATUS")
        print("="*80)

        for name, versions in self.prompts.items():
            active = self.active_prompts.get(name, versions[-1].version if versions else "None")
            print(f"\n📝 {name}")
            print(f"   Active Version: {active}")
            print(f"   Total Versions: {len(versions)}")

            for v in versions:
                marker = "✓" if v.version == active else " "
                print(f"   {marker} v{v.version}: {v.description}")

        print("="*80 + "\n")

    def export_for_production(self, output_file: str = "production_prompts.json"):
        """
        Export active prompts to production format.
        Use this to move tested prompts to production.
        """
        filepath = PROMPTS_DIR / output_file

        production_data = {}
        for name, version in self.active_prompts.items():
            prompt = self._get_prompt_version(name, version)
            if prompt:
                production_data[name] = {
                    "version": version,
                    "content": prompt.content,
                    "description": prompt.description,
                    "locked_at": datetime.now().isoformat(),
                }

        with open(filepath, "w") as f:
            json.dump(production_data, f, indent=2)

        logger.info(f"Production prompts exported to {filepath}")
        return filepath


# Convenience functions
def create_prompt_versions_for_testing():
    """Create sample prompt versions for testing."""
    manager = PromptManager()

    # Version 1.0 of fabrication assistant
    manager.create_prompt(
        name="fabrication_assistant",
        version="1.0",
        content="You are a basic fabrication assistant. Answer questions about 3D printing.",
        description="Initial basic version",
        tags=["basic", "v1"],
    )

    # Version 1.1 with improvements
    manager.create_prompt(
        name="fabrication_assistant",
        version="1.1",
        content="You are an expert fabrication assistant. Provide detailed, step-by-step guidance on design, materials, and fabrication methods. Warn about common mistakes.",
        description="Improved with step-by-step guidance",
        tags=["improved", "v1"],
    )

    # Version 2.0 with more detail
    manager.create_prompt(
        name="fabrication_assistant",
        version="2.0",
        content="You are a world-class fabrication expert with 20 years of experience. Provide comprehensive, professional guidance. Include specific tools, materials, and techniques. Provide cost and time estimates when relevant.",
        description="Professional version with expert perspective",
        tags=["professional", "v2"],
    )

    return manager
