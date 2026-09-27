"""
config_loader.py
================
Configuration loader and schema validator for Enterprise File Organizer.
Validates category definitions, regex syntax, size units, and destinations.
"""

import copy
import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from organizer.exceptions import ConfigurationError, SecurityError
from organizer.models import ConflictStrategy, Rule, RuleType
from organizer.utils import parse_size_to_bytes, sanitize_relative_path

logger = logging.getLogger("EnterpriseOrganizer.ConfigLoader")


class ConfigLoader:
    """
    Loads, parses, validates, and serializes JSON configuration files.
    """

    @staticmethod
    def get_default_config_path() -> Path:
        """Return the path to the built-in default_rules.json."""
        # Relative to project root
        base_dir = Path(__file__).resolve().parent.parent
        return base_dir / "config" / "default_rules.json"

    @staticmethod
    def load_default_config() -> Dict[str, Any]:
        """Load and return the default system configuration."""
        default_path = ConfigLoader.get_default_config_path()
        return ConfigLoader.load_config(default_path)

    @staticmethod
    def load_config(config_path: Path) -> Dict[str, Any]:
        """Load, parse, and validate a JSON configuration file."""
        if not config_path.exists():
            raise ConfigurationError(f"Configuration file not found: {config_path}")
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as err:
            raise ConfigurationError(f"Invalid JSON syntax in {config_path}: {err}") from err
        except OSError as err:
            raise ConfigurationError(f"Could not read configuration file {config_path}: {err}") from err

        ConfigLoader.validate_config(data)
        return data

    @staticmethod
    def validate_config(data: Dict[str, Any]) -> None:
        """
        Validate structure and semantic constraints in the configuration dictionary.
        Raises ConfigurationError with a specific, helpful message if invalid.
        """
        if not isinstance(data, dict):
            raise ConfigurationError("Configuration root must be a JSON object.")

        # 1. Validate Conflict Strategy (Optional)
        if "conflict_strategy" in data:
            strat_val = str(data["conflict_strategy"]).lower()
            valid_strategies = [s.value for s in ConflictStrategy]
            if strat_val not in valid_strategies:
                raise ConfigurationError(
                    f"Invalid conflict_strategy '{data['conflict_strategy']}'. "
                    f"Must be one of: {', '.join(valid_strategies)}"
                )

        # 2. Validate Categories
        if "categories" in data:
            if not isinstance(data["categories"], dict):
                raise ConfigurationError("'categories' must be a JSON object mapping category names to extension lists.")
            for cat_name, extensions in data["categories"].items():
                if not isinstance(cat_name, str) or not cat_name.strip():
                    raise ConfigurationError("Category name must be a non-empty string.")
                if not isinstance(extensions, list):
                    raise ConfigurationError(f"Extensions for category '{cat_name}' must be a list of strings.")
                for ext in extensions:
                    if not isinstance(ext, str) or not ext.strip():
                        raise ConfigurationError(f"Invalid extension '{ext}' in category '{cat_name}'. Must be a non-empty string.")

        # 3. Validate Rules
        if "rules" in data:
            if not isinstance(data["rules"], list):
                raise ConfigurationError("'rules' must be a list of rule definitions.")
            for idx, rule in enumerate(data["rules"]):
                rule_desc = f"Rule #{idx + 1}"
                if isinstance(rule, dict) and "name" in rule:
                    rule_desc = f"Rule '{rule['name']}' (index {idx})"

                if not isinstance(rule, dict):
                    raise ConfigurationError(f"{rule_desc} must be a JSON object.")

                # Required fields
                for field in ("name", "type", "destination"):
                    if field not in rule:
                        raise ConfigurationError(f"{rule_desc} is missing required field '{field}'.")
                    if not isinstance(rule[field], str) or not rule[field].strip():
                        raise ConfigurationError(f"{rule_desc} field '{field}' must be a non-empty string.")

                # Rule Type check
                rule_type_val = rule["type"].lower()
                valid_types = [t.value for t in RuleType if t != RuleType.DEFAULT]
                if rule_type_val not in valid_types:
                    raise ConfigurationError(
                        f"{rule_desc} has invalid type '{rule['type']}'. "
                        f"Allowed types: {', '.join(valid_types)}"
                    )

                # Destination security check
                try:
                    sanitize_relative_path(rule["destination"])
                except SecurityError as sec_err:
                    raise ConfigurationError(f"{rule_desc} destination is invalid: {sec_err}") from sec_err

                # Type-specific validations
                if rule_type_val == RuleType.REGEX.value:
                    pattern = rule.get("pattern")
                    if not pattern or not isinstance(pattern, str):
                        raise ConfigurationError(f"{rule_desc} of type 'regex' requires a non-empty 'pattern' string.")
                    try:
                        re.compile(pattern)
                    except re.error as err:
                        raise ConfigurationError(f"{rule_desc} contains invalid regular expression pattern '{pattern}': {err}") from err

                elif rule_type_val == RuleType.FILENAME.value:
                    pattern = rule.get("pattern")
                    if not pattern or not isinstance(pattern, str):
                        raise ConfigurationError(f"{rule_desc} of type 'filename' requires a non-empty 'pattern' string.")

                elif rule_type_val == RuleType.EXTENSION.value:
                    pattern = rule.get("pattern")
                    if not pattern or not isinstance(pattern, str):
                        raise ConfigurationError(f"{rule_desc} of type 'extension' requires a non-empty 'pattern' string.")

                elif rule_type_val == RuleType.SIZE.value:
                    has_min = "min_size" in rule and rule["min_size"] is not None
                    has_max = "max_size" in rule and rule["max_size"] is not None
                    if not has_min and not has_max:
                        raise ConfigurationError(f"{rule_desc} of type 'size' must specify at least 'min_size' or 'max_size'.")
                    min_bytes = None
                    max_bytes = None
                    if has_min:
                        try:
                            min_bytes = parse_size_to_bytes(str(rule["min_size"]))
                        except ValueError as err:
                            raise ConfigurationError(f"{rule_desc} invalid 'min_size': {err}") from err
                    if has_max:
                        try:
                            max_bytes = parse_size_to_bytes(str(rule["max_size"]))
                        except ValueError as err:
                            raise ConfigurationError(f"{rule_desc} invalid 'max_size': {err}") from err
                    if min_bytes is not None and max_bytes is not None and min_bytes > max_bytes:
                        raise ConfigurationError(
                            f"{rule_desc} 'min_size' ({rule['min_size']}) cannot be greater than 'max_size' ({rule['max_size']})."
                        )

                elif rule_type_val == RuleType.DATE.value:
                    has_within = "modified_within_days" in rule and rule["modified_within_days"] is not None
                    has_older = "modified_older_than_days" in rule and rule["modified_older_than_days"] is not None
                    if not has_within and not has_older:
                        raise ConfigurationError(
                            f"{rule_desc} of type 'date' must specify 'modified_within_days' or 'modified_older_than_days'."
                        )
                    if has_within:
                        val = rule["modified_within_days"]
                        if not isinstance(val, (int, float)) or val < 0:
                            raise ConfigurationError(f"{rule_desc} 'modified_within_days' must be a non-negative number.")
                    if has_older:
                        val = rule["modified_older_than_days"]
                        if not isinstance(val, (int, float)) or val < 0:
                            raise ConfigurationError(f"{rule_desc} 'modified_older_than_days' must be a non-negative number.")

    @staticmethod
    def parse_rules(rules_data: List[Dict[str, Any]]) -> List[Rule]:
        """Convert raw rule dictionaries into typed Rule objects."""
        parsed_rules: List[Rule] = []
        for r_dict in rules_data:
            rule_type_val = r_dict["type"].lower()
            try:
                rule_type = RuleType(rule_type_val)
            except ValueError:
                raise ConfigurationError(f"Unknown rule type '{rule_type_val}' in rule '{r_dict.get('name')}'")

            min_bytes = None
            max_bytes = None
            if "min_size" in r_dict and r_dict["min_size"] is not None:
                min_bytes = parse_size_to_bytes(str(r_dict["min_size"]))
            if "max_size" in r_dict and r_dict["max_size"] is not None:
                max_bytes = parse_size_to_bytes(str(r_dict["max_size"]))

            rule = Rule(
                name=r_dict["name"],
                rule_type=rule_type,
                destination=r_dict["destination"],
                pattern=r_dict.get("pattern"),
                min_size_bytes=min_bytes,
                max_size_bytes=max_bytes,
                modified_within_days=r_dict.get("modified_within_days"),
                modified_older_than_days=r_dict.get("modified_older_than_days"),
                case_sensitive=r_dict.get("case_sensitive", False),
                priority=r_dict.get("priority", 0),
            )
            parsed_rules.append(rule)
        return parsed_rules

    @staticmethod
    def merge_with_defaults(user_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge a user configuration dictionary with system defaults.
        User rules take priority (are prepended), and user categories merge with defaults.
        """
        defaults = ConfigLoader.load_default_config()
        merged = copy.deepcopy(defaults)

        # Merge categories
        if "categories" in user_config:
            for cat, exts in user_config["categories"].items():
                if cat in merged["categories"]:
                    # Combine without duplicate extensions
                    existing = set(merged["categories"][cat])
                    for ext in exts:
                        if ext not in existing:
                            merged["categories"][cat].append(ext)
                else:
                    merged["categories"][cat] = exts

        # Merge rules: user rules precede default rules
        if "rules" in user_config:
            merged["rules"] = user_config["rules"] + merged.get("rules", [])

        if "conflict_strategy" in user_config:
            merged["conflict_strategy"] = user_config["conflict_strategy"]

        return merged

    @staticmethod
    def save_config(config_data: Dict[str, Any], output_path: Path) -> None:
        """Serialize configuration data to formatted JSON file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
            f.write("\n")
