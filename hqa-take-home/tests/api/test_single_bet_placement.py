"""TP-01 and TP-02 API checks from test-plan.md.

Run this suite on its own with: pytest tests/api
"""

from decimal import Decimal

import pytest

from config.constants import (
    HOME_SELECTION,
    INITIAL_BALANCE,
    INSUFFICIENT_BALANCE_ERROR,
    STAKE_ABOVE_BALANCE,
    VALID_STAKE,
)
from utils.money import money


@pytest.mark.api
@pytest.mark.smoke
class TestSingleBetPlacementApi:
    def test_tp_01_place_valid_single_bet_debits_balance(self, betting_api):
        """A placed bet must return stake × odds and persist a balance lower by the stake only."""
        balance = betting_api.prepare_balance()
        assert money(balance) == money(INITIAL_BALANCE), (
            f"Reset should persist €{INITIAL_BALANCE}, GET /api/balance returned {balance}"
        )

        matches = betting_api.get_matches()
        assert matches.status_code == 200, matches.text
        match_id = matches.json()[0]["id"]

        response = betting_api.place_bet(match_id, HOME_SELECTION, float(VALID_STAKE))
        assert response.status_code == 200, response.text
        body = response.json()

        odds = money(body["odds"])
        expected_payout = money(Decimal(VALID_STAKE) * odds)
        expected_balance = money(INITIAL_BALANCE) - money(VALID_STAKE)

        assert body.get("matchId") == match_id
        assert body.get("selection") == HOME_SELECTION
        assert money(body["stake"]) == money(VALID_STAKE)
        assert money(body["payout"]) == expected_payout, (
            "Payout should be the stake × the odds returned for this bet"
        )
        assert money(body["balance"]) == expected_balance
        assert body.get("currency") == "EUR"
        assert money(betting_api.balance_amount()) == expected_balance, (
            "GET /api/balance should drop by the stake only"
        )

    def test_tp_02_stake_above_balance_is_rejected(self, betting_api):
        """A stake the user cannot cover must be rejected, and the persisted balance must stay put."""
        balance = betting_api.prepare_balance()
        assert money(balance) == money(INITIAL_BALANCE), (
            f"Reset should persist €{INITIAL_BALANCE}, GET /api/balance returned {balance}"
        )
        matches = betting_api.get_matches()
        assert matches.status_code == 200, matches.text
        match_id = matches.json()[0]["id"]

        response = betting_api.place_bet(match_id, HOME_SELECTION, float(STAKE_ABOVE_BALANCE))
        assert response.status_code == 422, (
            f"Expected 422 for stake above balance, got {response.status_code}: {response.text}"
        )
        body = response.json()
        assert body.get("error") == INSUFFICIENT_BALANCE_ERROR, (
            f"Expected error '{INSUFFICIENT_BALANCE_ERROR}', got {body}"
        )
        assert "payout" not in body, "A rejected bet must not return a payout"

        assert money(betting_api.balance_amount()) == money(INITIAL_BALANCE), (
            "A rejected bet must not change the persisted balance"
        )
