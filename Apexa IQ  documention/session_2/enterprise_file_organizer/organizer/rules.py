"""
rules.py
========
Deterministic Rule Engine for Enterprise File Organizer.
Evaluates files against ordered rules with strict priority:
1. Explicit Regex Rules
2. Filename Pattern Rules
3. Extension / Custom Type Rules
4. File Size Rules
5. Modification Date Rules
6. Default Category Fallback
"""

import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from organizer.classifier import FileClassifier
from organizer.exceptions import RuleError
from organizer.models import FileInfo, Rule, RuleType

logger = logging.getLogger("EnterpriseOrganizer.Rules")

RULE_TYPE_PRECEDENCE = {
    RuleType.REGEX: 1,
    RuleType.FILENAME: 2,
    RuleType.EXTENSION: 3,
    RuleType.SIZE: 4,
    RuleType.DATE: 5,
    RuleType.DEFAULT: 6,
}


class RuleEngine:
    """
    Evaluates file metadata against configured rules with strict, deterministic priority.
    """

    def __init__(self, rules: List[Rule], classifier: FileClassifier):
        self.classifier = classifier
        self._compiled_regexes: Dict[str, re.Pattern] = {}

        # Deterministically sort rules by precedence and priority
        self.rules = self._sort_rules(rules)
        self._compile_regexes()

    def _sort_rules(self, rules: List[Rule]) -> List[Rule]:
        """
        Sort rules deterministically:
        1. Rule Type Precedence (Regex -> Filename -> Extension -> Size -> Date)
        2. Explicit rule.priority (lower number = higher priority)
        """
        indexed_rules = list(enumerate(rules))
        sorted_indexed = sorted(
            indexed_rules,
            key=lambda item: (
                RULE_TYPE_PRECEDENCE.get(item[1].rule_type, 99),
                item[1].priority,
                item[0],  # stable original index
            ),
        )
        return [rule for _, rule in sorted_indexed]

    def _compile_regexes(self) -> None:
        """Pre-compile all regex rules with error checking."""
        for rule in self.rules:
            if rule.rule_type == RuleType.REGEX:
                if not rule.pattern:
                    raise RuleError(f"Regex rule '{rule.name}' has no pattern defined.")
                try:
                    flags = 0 if rule.case_sensitive else re.IGNORECASE
                    self._compiled_regexes[rule.name] = re.compile(rule.pattern, flags)
                except re.error as err:
                    raise RuleError(f"Failed to compile regex for rule '{rule.name}': {err}") from err

    def evaluate(self, file_info: FileInfo) -> Tuple[str, str]:
        """
        Evaluate file metadata against rules and return (destination_subpath, matched_rule_name).
        """
        res = self.evaluate_detailed(file_info)
        return res["destination"], res["rule_name"]

    def evaluate_detailed(self, file_info: FileInfo) -> Dict[str, Any]:
        """
        Perform in-depth evaluation and return full trace details.
        """
        rel_path_str = str(file_info.relative_path).replace("\\", "/") if file_info.relative_path else ""

        # 1. Regex Rules
        for rule in self.rules:
            if rule.rule_type == RuleType.REGEX:
                regex = self._compiled_regexes.get(rule.name)
                if regex:
                    # Match against filename or relative path
                    if regex.search(file_info.name) or (rel_path_str and regex.search(rel_path_str)):
                        logger.debug("File '%s' matched regex rule '%s'", file_info.name, rule.name)
                        return {
                            "destination": rule.destination,
                            "rule_name": rule.name,
                            "rule_type": RuleType.REGEX.value,
                            "reason": f"Matched pattern '{rule.pattern}'",
                        }

        # 2. Filename Pattern Rules
        for rule in self.rules:
            if rule.rule_type == RuleType.FILENAME and rule.pattern:
                pat = rule.pattern if rule.case_sensitive else rule.pattern.lower()
                target_name = file_info.name if rule.case_sensitive else file_info.name.lower()
                if pat in target_name:
                    logger.debug("File '%s' matched filename rule '%s'", file_info.name, rule.name)
                    return {
                        "destination": rule.destination,
                        "rule_name": rule.name,
                        "rule_type": RuleType.FILENAME.value,
                        "reason": f"Filename contains substring '{rule.pattern}'",
                    }

        # 3. Extension Rules
        for rule in self.rules:
            if rule.rule_type == RuleType.EXTENSION and rule.pattern:
                norm_pat = rule.pattern.lower()
                if not norm_pat.startswith("."):
                    norm_pat = f".{norm_pat}"
                if file_info.extension.lower() == norm_pat:
                    logger.debug("File '%s' matched extension rule '%s'", file_info.name, rule.name)
                    return {
                        "destination": rule.destination,
                        "rule_name": rule.name,
                        "rule_type": RuleType.EXTENSION.value,
                        "reason": f"Extension matches '{rule.pattern}'",
                    }

        # 4. File Size Rules
        for rule in self.rules:
            if rule.rule_type == RuleType.SIZE:
                matches_min = rule.min_size_bytes is None or file_info.size >= rule.min_size_bytes
                matches_max = rule.max_size_bytes is None or file_info.size <= rule.max_size_bytes
                if matches_min and matches_max:
                    logger.debug("File '%s' matched size rule '%s'", file_info.name, rule.name)
                    return {
                        "destination": rule.destination,
                        "rule_name": rule.name,
                        "rule_type": RuleType.SIZE.value,
                        "reason": f"Size {file_info.size} bytes fits range [{rule.min_size_bytes}, {rule.max_size_bytes}]",
                    }

        # 5. Modification Date Rules
        now = datetime.now(timezone.utc) if file_info.modified_time.tzinfo else datetime.now()
        age_days = (now - file_info.modified_time).total_seconds() / 86400.0
        # Prevent negative age caused by microsecond clock skew
        age_days = max(0.0, age_days)

        for rule in self.rules:
            if rule.rule_type == RuleType.DATE:
                matches_recent = (
                    rule.modified_within_days is None or age_days <= rule.modified_within_days
                )
                matches_old = (
                    rule.modified_older_than_days is None or age_days >= rule.modified_older_than_days
                )
                if matches_recent and matches_old:
                    logger.debug("File '%s' matched date rule '%s'", file_info.name, rule.name)
                    return {
                        "destination": rule.destination,
                        "rule_name": rule.name,
                        "rule_type": RuleType.DATE.value,
                        "reason": f"File age {age_days:.1f} days fits criteria",
                    }

        # 6. Default Category Fallback
        category = self.classifier.classify_filename(file_info.name)
        return {
            "destination": category,
            "rule_name": f"DefaultCategory:{category}",
            "rule_type": RuleType.DEFAULT.value,
            "reason": f"Classified by extension to default category '{category}'",
        }
