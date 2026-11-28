import os
from typing import Dict, List, Any, Optional, Tuple
import yaml


class RulesEngine:
    def __init__(self, rules_dir: Optional[str] = None):
        if rules_dir is None:
            rules_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "rules"))
        self.rules_dir = rules_dir
        self.safety_data = self._load_yaml("safety_blocklist.yaml")
        self.dfm_data = self._load_yaml("dfm_rules.yaml")
        self.readiness_data = self._load_yaml("readiness_rules.yaml")

    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        path = os.path.join(self.rules_dir, filename)
        if not os.path.exists(path):
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def check_safety_domain(self, idea_text: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Scans idea_text against safety categories.
        Returns (is_safety_critical, warning_message, category_name).
        """
        lower_text = idea_text.lower()
        for cat in self.safety_data.get("categories", []):
            for kw in cat.get("keywords", []):
                if kw.lower() in lower_text:
                    return True, cat.get("warning"), cat.get("name")
        return False, None, None

    def evaluate_project(
        self,
        idea_text: str,
        requirements: List[Dict[str, Any]],
        bom_items: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Evaluates safety, DFM, and readiness rules.
        """
        safety_flag, safety_warning, safety_cat = self.check_safety_domain(idea_text)

        findings: List[Dict[str, Any]] = []

        # Convert bom items to lower-cased component names & specs
        bom_names = [item.get("name", "").lower() for item in bom_items]
        all_specs_str = " ".join([str(item.get("specs_json", "")).lower() for item in bom_items])

        # Evaluate DFM rules
        for r in self.dfm_data.get("rules", []):
            finding = self._evaluate_dfm_rule(r, bom_items, bom_names, all_specs_str)
            findings.append(finding)

        # Evaluate Readiness rules
        for r in self.readiness_data.get("rules", []):
            finding = self._evaluate_readiness_rule(r, bom_items, bom_names, all_specs_str)
            findings.append(finding)

        # Determine overall readiness status
        if safety_flag:
            overall_status = "not assessed: requires qualified engineer"
        else:
            has_fail = any(f["status"] == "fail" for f in findings)
            has_warn = any(f["status"] == "warn" for f in findings)
            if has_fail:
                overall_status = "revisions_needed"
            elif has_warn:
                overall_status = "preliminary_pass_with_warnings"
            else:
                overall_status = "preliminary_ready"

        return {
            "safety_flag": safety_flag,
            "safety_warning": safety_warning,
            "safety_category": safety_cat,
            "overall_status": overall_status,
            "findings": findings,
        }

    def _evaluate_dfm_rule(
        self,
        rule: Dict[str, Any],
        bom_items: List[Dict[str, Any]],
        bom_names: List[str],
        all_specs_str: str,
    ) -> Dict[str, Any]:
        r_id = rule["id"]
        status = "pass"
        note = rule.get("pass_note", "Passed")

        if r_id == "DFM-01":
            # Fastener count check
            fastener_names = [n for n in bom_names if any(w in n for w in ["screw", "bolt", "m3", "m4", "m5"])]
            if len(fastener_names) > 3:
                status = "warn"
                note = rule.get("warn_note", "")
        elif r_id == "DFM-03":
            # High current wire gauge
            has_motor = any("motor" in n for n in bom_names)
            has_wire = any("14 awg" in n or "14 awg" in all_specs_str or "wire" in n for n in bom_names)
            if has_motor and not has_wire:
                status = "fail"
                note = rule.get("fail_note", "")
        elif r_id == "DFM-05":
            # Outdoor IP rating
            has_enclosure = any("ip65" in n or "ip67" in n or "ip65" in all_specs_str for n in bom_names)
            if not has_enclosure:
                status = "warn"
                note = rule.get("warn_note", "")
        elif r_id == "DFM-06":
            # Vibration loosening
            has_damping = any(any(k in n for k in ["threadlocker", "locknut", "vibration", "rubber mount"]) for n in bom_names)
            if not has_damping:
                status = "warn"
                note = rule.get("warn_note", "")
        elif r_id == "DFM-07":
            # Bearing support for wheel
            has_wheel = any("wheel" in n for n in bom_names)
            has_bearing = any("bearing" in n or "pillow block" in n for n in bom_names)
            if has_wheel and not has_bearing:
                status = "warn"
                note = rule.get("warn_note", "")
        elif r_id == "DFM-08":
            # Compute cooling
            has_sbc = any(any(k in n for k in ["raspberry pi", "jetson", "orange pi"]) for n in bom_names)
            has_fan = any("fan" in n or "heatsink" in n for n in bom_names)
            if has_sbc and not has_fan:
                status = "warn"
                note = rule.get("warn_note", "")

        return {
            "rule_id": r_id,
            "name": rule["name"],
            "area": "dfm",
            "status": status,
            "note": note,
        }

    def _evaluate_readiness_rule(
        self,
        rule: Dict[str, Any],
        bom_items: List[Dict[str, Any]],
        bom_names: List[str],
        all_specs_str: str,
    ) -> Dict[str, Any]:
        r_id = rule["id"]
        status = "pass"
        note = rule.get("pass_note", "Passed")

        if r_id == "READ-01":
            # Emergency stop check
            has_estop = any("emergency stop" in n or "e-stop" in n for n in bom_names)
            if not has_estop:
                status = "fail"
                note = rule.get("fail_note", "")
        elif r_id == "READ-02":
            # Fuse block check
            has_fuse = any("fuse" in n for n in bom_names)
            if not has_fuse:
                status = "fail"
                note = rule.get("fail_note", "")
        elif r_id == "READ-03":
            # Battery BMS check
            has_lithium = any("lifepo4" in n or "lithium" in n for n in bom_names)
            has_bms = any("bms" in n or "bms" in all_specs_str for n in bom_names)
            if has_lithium and not has_bms:
                status = "fail"
                note = rule.get("fail_note", "")
        elif r_id == "READ-04":
            # Battery transport check
            has_lithium = any("lifepo4" in n or "lithium" in n for n in bom_names)
            if has_lithium:
                status = "needs_expert"
                note = rule.get("warn_note", "")
        elif r_id == "READ-06":
            # Beacon/buzzer warning
            has_warning = any(any(k in n for k in ["beacon", "strobe", "buzzer"]) for n in bom_names)
            if not has_warning:
                status = "warn"
                note = rule.get("warn_note", "")
        elif r_id == "READ-07":
            # Master battery switch
            has_switch = any("isolator" in n or "cut-off" in n or "disconnect" in n for n in bom_names)
            if not has_switch:
                status = "warn"
                note = rule.get("warn_note", "")
        elif r_id == "READ-08":
            # Single source parts
            has_rtk = any("rtk" in n or "zed-f9p" in n for n in bom_names)
            if has_rtk:
                status = "needs_expert"
                note = rule.get("warn_note", "")

        return {
            "rule_id": r_id,
            "name": rule["name"],
            "area": "readiness",
            "status": status,
            "note": note,
        }
