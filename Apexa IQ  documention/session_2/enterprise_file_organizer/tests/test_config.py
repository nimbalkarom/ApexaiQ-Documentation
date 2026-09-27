"""
Unit tests for configuration loading, validation, merging, and error handling.
"""

import json
import pytest
from pathlib import Path

from organizer.config_loader import ConfigLoader
from organizer.exceptions import ConfigurationError
from organizer.models import ConflictStrategy, RuleType


def test_load_default_and_example_configs():
    """Verify built-in default and example configurations are strictly valid."""
    default_cfg = ConfigLoader.load_default_config()
    assert "categories" in default_cfg
    assert "rules" in default_cfg
    assert default_cfg["conflict_strategy"] == "rename_auto"

    example_path = Path(__file__).resolve().parent.parent / "config" / "example_rules.json"
    example_cfg = ConfigLoader.load_config(example_path)
    assert len(example_cfg["rules"]) >= 5

    parsed_rules = ConfigLoader.parse_rules(example_cfg["rules"])
    assert len(parsed_rules) == len(example_cfg["rules"])


def test_missing_config_file(tmp_path: Path):
    """Loading a non-existent configuration file must raise ConfigurationError."""
    missing = tmp_path / "non_existent.json"
    with pytest.raises(ConfigurationError, match="Configuration file not found"):
        ConfigLoader.load_config(missing)


def test_invalid_json_syntax(tmp_path: Path):
    """Malformed JSON syntax must raise ConfigurationError with details."""
    broken = tmp_path / "broken.json"
    broken.write_text("{ unquoted_key: 123, }", encoding="utf-8")
    with pytest.raises(ConfigurationError, match="Invalid JSON syntax"):
        ConfigLoader.load_config(broken)


def test_non_dict_root(tmp_path: Path):
    """Config root must be a JSON object, not a list or scalar."""
    bad = tmp_path / "list_root.json"
    bad.write_text("[]", encoding="utf-8")
    with pytest.raises(ConfigurationError, match="must be a JSON object"):
        ConfigLoader.load_config(bad)


def test_invalid_categories(tmp_path: Path):
    """Categories must map to list of extension strings."""
    bad = tmp_path / "bad_cat.json"
    bad.write_text(json.dumps({"categories": "not-a-dict"}), encoding="utf-8")
    with pytest.raises(ConfigurationError, match="'categories' must be a JSON object"):
        ConfigLoader.load_config(bad)

    bad2 = tmp_path / "bad_cat2.json"
    bad2.write_text(json.dumps({"categories": {"Docs": ".pdf"}}), encoding="utf-8")
    with pytest.raises(ConfigurationError, match="must be a list of strings"):
        ConfigLoader.load_config(bad2)


def test_invalid_rule_missing_fields(tmp_path: Path):
    """Rules missing name, type, or destination must fail validation."""
    bad_rule = tmp_path / "missing_field.json"
    bad_rule.write_text(json.dumps({"rules": [{"name": "Test", "type": "regex"}]}), encoding="utf-8")
    with pytest.raises(ConfigurationError, match="missing required field 'destination'"):
        ConfigLoader.load_config(bad_rule)


def test_invalid_rule_type(tmp_path: Path):
    """Rules with unrecognized types must fail validation."""
    bad = tmp_path / "bad_type.json"
    bad.write_text(json.dumps({
        "rules": [{"name": "Magic", "type": "quantum_classifier", "destination": "Dest"}]
    }), encoding="utf-8")
    with pytest.raises(ConfigurationError, match="invalid type 'quantum_classifier'"):
        ConfigLoader.load_config(bad)


def test_invalid_regex_syntax(tmp_path: Path):
    """Invalid regex pattern must fail with descriptive error."""
    bad = tmp_path / "bad_regex.json"
    bad.write_text(json.dumps({
        "rules": [{"name": "Bad Regex", "type": "regex", "pattern": "(?P<incomplete", "destination": "Dest"}]
    }), encoding="utf-8")
    with pytest.raises(ConfigurationError, match="invalid regular expression pattern"):
        ConfigLoader.load_config(bad)


def test_invalid_size_rules(tmp_path: Path):
    """Size rules must have valid units and min_size <= max_size."""
    bad_unit = tmp_path / "bad_unit.json"
    bad_unit.write_text(json.dumps({
        "rules": [{"name": "Bad Size", "type": "size", "min_size": "500FOOBAR", "destination": "Dest"}]
    }), encoding="utf-8")
    with pytest.raises(ConfigurationError, match="invalid 'min_size'"):
        ConfigLoader.load_config(bad_unit)

    inverted_size = tmp_path / "inverted_size.json"
    inverted_size.write_text(json.dumps({
        "rules": [{"name": "Inverted", "type": "size", "min_size": "1GB", "max_size": "10MB", "destination": "Dest"}]
    }), encoding="utf-8")
    with pytest.raises(ConfigurationError, match="cannot be greater than 'max_size'"):
        ConfigLoader.load_config(inverted_size)


def test_invalid_date_rules(tmp_path: Path):
    """Date rules must have positive numbers."""
    negative_date = tmp_path / "neg_date.json"
    negative_date.write_text(json.dumps({
        "rules": [{"name": "Past", "type": "date", "modified_within_days": -10, "destination": "Dest"}]
    }), encoding="utf-8")
    with pytest.raises(ConfigurationError, match="must be a non-negative number"):
        ConfigLoader.load_config(negative_date)


def test_destination_path_traversal(tmp_path: Path):
    """Destinations escaping root with '..' or absolute paths must be rejected."""
    traversal = tmp_path / "traversal.json"
    traversal.write_text(json.dumps({
        "rules": [{"name": "Escape", "type": "filename", "pattern": "test", "destination": "../../etc/passwd"}]
    }), encoding="utf-8")
    with pytest.raises(ConfigurationError, match="Unsafe path traversal detected"):
        ConfigLoader.load_config(traversal)


def test_invalid_conflict_strategy(tmp_path: Path):
    """Unknown conflict strategy must raise ConfigurationError."""
    bad_strat = tmp_path / "bad_strat.json"
    bad_strat.write_text(json.dumps({
        "conflict_strategy": "destroy_all",
        "rules": []
    }), encoding="utf-8")
    with pytest.raises(ConfigurationError, match="Invalid conflict_strategy 'destroy_all'"):
        ConfigLoader.load_config(bad_strat)


def test_merge_with_defaults():
    """User rules must prepend default rules and custom categories must extend defaults."""
    user_config = {
        "conflict_strategy": "skip",
        "categories": {
            "CAD": [".dwg"],
            "Documents": [".customdoc"]
        },
        "rules": [
            {
                "name": "Custom User Rule",
                "type": "filename",
                "pattern": "custom_tag",
                "destination": "Custom/Tag"
            }
        ]
    }

    merged = ConfigLoader.merge_with_defaults(user_config)
    assert merged["conflict_strategy"] == "skip"
    assert "CAD" in merged["categories"]
    assert ".dwg" in merged["categories"]["CAD"]
    assert ".customdoc" in merged["categories"]["Documents"]
    assert ".pdf" in merged["categories"]["Documents"]  # Preserved original

    # User rule is prepended
    assert merged["rules"][0]["name"] == "Custom User Rule"
    assert len(merged["rules"]) > 1


def test_save_and_reload_config(tmp_path: Path):
    """Configuration saved to disk must be fully reloadable."""
    sample = {
        "categories": {"Code": [".py", ".rs"]},
        "rules": [
            {"name": "Rust Rule", "type": "filename", "pattern": "rs_", "destination": "RustCode"}
        ]
    }
    out_file = tmp_path / "saved_rules.json"
    ConfigLoader.save_config(sample, out_file)
    assert out_file.exists()

    reloaded = ConfigLoader.load_config(out_file)
    assert reloaded["categories"]["Code"] == [".py", ".rs"]
    assert len(reloaded["rules"]) == 1
