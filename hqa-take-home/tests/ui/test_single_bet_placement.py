"""TP-01 and TP-02 UI checks from test-plan.md.

Run this suite on its own with: pytest tests/ui
"""

from decimal import Decimal

import pytest

from config.constants import (
    INITIAL_BALANCE,
    INSUFFICIENT_BALANCE_COPY,
    STAKE_ABOVE_BALANCE,
    VALID_STAKE,
)
from utils.money import euro, money, parse_euro


@pytest.mark.ui
@pytest.mark.smoke
class TestSingleBetPlacementUi:
    def test_tp_01_place_valid_single_bet_updates_receipt_and_balance(self, ready_page):
        """A placed bet must show that same stake, odds, and payout on the receipt, then clear the slip."""
        ready_page.open()
        assert parse_euro(ready_page.header_balance_text()) == money(INITIAL_BALANCE)

        match = ready_page.first_match()
        odds = money(match["home_odds"])
        expected_payout = money(Decimal(VALID_STAKE) * odds)

        ready_page.select_home(match)
        assert "Home" in ready_page.selection_text()
        assert match["home_odds"] in ready_page.selection_odds_text()

        ready_page.enter_stake(VALID_STAKE)
        assert parse_euro(ready_page.potential_payout_text()) == expected_payout, (
            "Slip payout should be stake × home odds before the bet is placed"
        )

        ready_page.place_bet().wait_for_receipt()
        receipt = ready_page.receipt()

        assert receipt["bet_id"], "Receipt should show a bet id"
        assert receipt["match"] == f"{match['home_team']} vs {match['away_team']}", (
            "Receipt should list the home team first, matching the match card and the specification"
        )
        assert receipt["stake"] == euro(VALID_STAKE)
        assert receipt["odds"] == f"{odds:.2f}"
        assert receipt["payout"] == euro(expected_payout), (
            "Receipt payout should be the stake × odds shown on the slip, not a different price"
        )
        assert receipt["placed_at"], "Receipt should show when the bet was placed"

        ready_page.close_receipt()
        assert ready_page.slip_is_empty(), "Closing the receipt should clear the active selection"

        expected_balance = money(INITIAL_BALANCE) - money(VALID_STAKE)
        assert parse_euro(ready_page.header_balance_text()) == expected_balance, (
            "Header balance should drop by the stake only"
        )

    def test_tp_02_stake_above_balance_is_rejected_and_balance_stays(self, ready_page):
        """A stake the user cannot cover must stay blocked on the slip, with the header balance unchanged."""
        ready_page.open()
        assert parse_euro(ready_page.header_balance_text()) == money(INITIAL_BALANCE)

        ready_page.select_home(ready_page.first_match())
        ready_page.enter_stake(STAKE_ABOVE_BALANCE)

        warning = ready_page.stake_warning_text() or ""
        assert INSUFFICIENT_BALANCE_COPY in warning, (
            f"Slip should show '{INSUFFICIENT_BALANCE_COPY}', got {warning!r}"
        )
        assert ready_page.place_bet_enabled() is False, (
            "Place Bet should stay disabled when the stake is above the balance"
        )
        assert ready_page.success_modal_visible() is False
        assert parse_euro(ready_page.header_balance_text()) == money(INITIAL_BALANCE)
