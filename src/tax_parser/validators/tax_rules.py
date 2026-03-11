"""Cross-field validation rules for tax forms.

Validates arithmetic relationships, required fields, and format constraints.
"""

from __future__ import annotations

import logging
import re
from typing import Any

from tax_parser.models.result import FormType, ReviewFlag, ReviewSeverity

logger = logging.getLogger(__name__)


def _get_nested(data: dict, dotted_path: str) -> Any:
    """Retrieve a value from nested dict using dotted path like 'income.line_6_total_income'."""
    parts = dotted_path.split(".")
    current = data
    for part in parts:
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None
        if current is None:
            return None
    return current


def _safe_float(val: Any) -> float | None:
    """Convert a value to float, returning None if not possible."""
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


class TaxValidator:
    """Validate extracted tax data using domain-specific rules."""

    def validate(self, form_type: FormType, data: dict[str, Any]) -> list[ReviewFlag]:
        """Run all applicable validation rules for the given form type.

        Returns a list of ReviewFlag objects for any issues found.
        """
        flags: list[ReviewFlag] = []

        # Universal validations
        flags.extend(self._validate_ein(data))
        flags.extend(self._validate_required_header(data))

        # Form-specific validations
        validators = {
            FormType.FORM_1120S: self._validate_1120s,
            FormType.FORM_1120: self._validate_1120,
            FormType.FORM_1065: self._validate_1065,
        }

        validator_fn = validators.get(form_type)
        if validator_fn:
            flags.extend(validator_fn(data))

        if flags:
            logger.info("Validation found %d issues for %s", len(flags), form_type.value)
        return flags

    # ------------------------------------------------------------------
    # Universal validations
    # ------------------------------------------------------------------

    def _validate_ein(self, data: dict) -> list[ReviewFlag]:
        """Validate EIN format (XX-XXXXXXX)."""
        ein = _get_nested(data, "taxpayer.ein")
        if ein is None:
            return []

        ein_str = str(ein).strip()
        if not re.match(r"^\d{2}-\d{7}$", ein_str):
            return [
                ReviewFlag(
                    field_name="taxpayer.ein",
                    severity=ReviewSeverity.WARNING,
                    message=f"EIN '{ein_str}' does not match expected format XX-XXXXXXX",
                )
            ]
        return []

    def _validate_required_header(self, data: dict) -> list[ReviewFlag]:
        """Check that basic header fields are present."""
        flags: list[ReviewFlag] = []
        name = _get_nested(data, "taxpayer.name")
        if not name:
            flags.append(
                ReviewFlag(
                    field_name="taxpayer.name",
                    severity=ReviewSeverity.ERROR,
                    message="Taxpayer name is missing",
                )
            )
        return flags

    # ------------------------------------------------------------------
    # Form 1120-S validations
    # ------------------------------------------------------------------

    def _validate_1120s(self, data: dict) -> list[ReviewFlag]:
        flags: list[ReviewFlag] = []

        # Line 1c = 1a - 1b
        flags.extend(
            self._check_arithmetic(
                data,
                result_path="income.line_1c_balance",
                addends=["income.line_1a_gross_receipts"],
                subtrahends=["income.line_1b_returns_allowances"],
                label="Income Line 1c",
            )
        )

        # Line 3 = 1c - 2
        flags.extend(
            self._check_arithmetic(
                data,
                result_path="income.line_3_gross_profit",
                addends=["income.line_1c_balance"],
                subtrahends=["income.line_2_cost_of_goods_sold"],
                label="Income Line 3 (Gross Profit)",
            )
        )

        # Line 6 = lines 3 + 4 + 5
        flags.extend(
            self._check_arithmetic(
                data,
                result_path="income.line_6_total_income",
                addends=[
                    "income.line_3_gross_profit",
                    "income.line_4_net_gain_loss_form_4797",
                    "income.line_5_other_income_loss",
                ],
                label="Income Line 6 (Total Income)",
            )
        )

        # Line 21 = line 6 - line 20
        flags.extend(
            self._check_arithmetic(
                data,
                result_path="tax_payments.line_21_ordinary_business_income",
                addends=["income.line_6_total_income"],
                subtrahends=["deductions.line_20_total_deductions"],
                label="Line 21 (Ordinary Business Income)",
            )
        )

        # Schedule K line 1 should match page 1 line 21
        k1_income = _safe_float(_get_nested(data, "schedule_k.line_1_ordinary_business_income"))
        p1_income = _safe_float(_get_nested(data, "tax_payments.line_21_ordinary_business_income"))
        if k1_income is not None and p1_income is not None:
            if abs(k1_income - p1_income) > 1.0:
                flags.append(
                    ReviewFlag(
                        field_name="schedule_k.line_1_ordinary_business_income",
                        severity=ReviewSeverity.ERROR,
                        message=(
                            f"Schedule K line 1 ({k1_income}) does not match "
                            f"Page 1 line 21 ({p1_income})"
                        ),
                    )
                )

        # Schedule L: total assets (end of year) should equal total liabilities + equity
        flags.extend(self._validate_balance_sheet(data))

        return flags

    # ------------------------------------------------------------------
    # Form 1120 validations
    # ------------------------------------------------------------------

    def _validate_1120(self, data: dict) -> list[ReviewFlag]:
        flags: list[ReviewFlag] = []

        # Line 3 = 1c - 2
        flags.extend(
            self._check_arithmetic(
                data,
                result_path="income.line_3_gross_profit",
                addends=["income.line_1c_balance"],
                subtrahends=["income.line_2_cost_of_goods_sold"],
                label="Income Line 3 (Gross Profit)",
            )
        )

        # Line 30 = 28 - 29a - 29b
        flags.extend(
            self._check_arithmetic(
                data,
                result_path="tax_payments.line_30_taxable_income",
                addends=["tax_payments.line_28_taxable_income_before_nol"],
                subtrahends=[
                    "tax_payments.line_29a_nol_deduction",
                    "tax_payments.line_29b_special_deductions",
                ],
                label="Line 30 (Taxable Income)",
            )
        )

        return flags

    # ------------------------------------------------------------------
    # Form 1065 validations
    # ------------------------------------------------------------------

    def _validate_1065(self, data: dict) -> list[ReviewFlag]:
        flags: list[ReviewFlag] = []

        # Line 22 = line 8 - line 21
        flags.extend(
            self._check_arithmetic(
                data,
                result_path="deductions.line_22_ordinary_business_income",
                addends=["income.line_8_total_income"],
                subtrahends=["deductions.line_21_total_deductions"],
                label="Line 22 (Ordinary Business Income)",
            )
        )

        return flags

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _check_arithmetic(
        self,
        data: dict,
        result_path: str,
        addends: list[str],
        subtrahends: list[str] | None = None,
        label: str = "",
        tolerance: float = 1.0,
    ) -> list[ReviewFlag]:
        """Verify that result_path ≈ sum(addends) - sum(subtrahends)."""
        result_val = _safe_float(_get_nested(data, result_path))
        if result_val is None:
            return []  # Can't validate if the result field is missing

        total = 0.0
        for path in addends:
            val = _safe_float(_get_nested(data, path))
            if val is not None:
                total += val

        for path in (subtrahends or []):
            val = _safe_float(_get_nested(data, path))
            if val is not None:
                total -= val

        if abs(result_val - total) > tolerance:
            return [
                ReviewFlag(
                    field_name=result_path,
                    severity=ReviewSeverity.ERROR,
                    message=(
                        f"{label}: extracted value {result_val} does not match "
                        f"computed value {total} (diff={result_val - total:.2f})"
                    ),
                )
            ]
        return []

    def _validate_balance_sheet(self, data: dict) -> list[ReviewFlag]:
        """For 1120-S Schedule L, verify total_assets == total_liabilities_equity."""
        flags: list[ReviewFlag] = []

        for period in ("beginning_of_year", "end_of_year"):
            assets = _safe_float(
                _get_nested(data, f"schedule_l.total_assets.{period}")
            )
            liabilities_equity = _safe_float(
                _get_nested(data, f"schedule_l.total_liabilities_equity.{period}")
            )

            if assets is not None and liabilities_equity is not None:
                if abs(assets - liabilities_equity) > 1.0:
                    flags.append(
                        ReviewFlag(
                            field_name=f"schedule_l.total_assets.{period}",
                            severity=ReviewSeverity.ERROR,
                            message=(
                                f"Schedule L {period}: Total assets ({assets}) ≠ "
                                f"Total liabilities + equity ({liabilities_equity})"
                            ),
                        )
                    )

        return flags
