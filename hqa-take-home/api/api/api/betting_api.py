{
  """HTTP access for the betting API.: RestUtils performs the call,
ApiManager exposes one method per endpoint, and the test only asserts.
"""

import requests

from config.constants import BASE_URL


class BettingApi:
    def __init__(self, user_id: str, base_url: str = BASE_URL):
        self.user_id = user_id
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update(
            {
    "x-user-id": user_id,
    "Accept": "application/json",
    "Content-Type": "application/json",
  }
        )

    def get_matches(self) -> requests.Response:
        return self._get("/api/matches")

    def get_balance(self) -> requests.Response:
        return self._get("/api/balance")

    def reset_balance(self) -> requests.Response:
        return self._post("/api/reset-balance",
  {})

    def place_bet(self, match_id: str, selection: str, stake) -> requests.Response:
        return self._post(
            "/api/place-bet",
  {
    "matchId": match_id,
    "selection": selection,
    "stake": stake
  },
        )

    def balance_amount(self) -> float:
        response = self.get_balance()
        self._require_ok(response,
  "GET /api/balance")
        body = response.json()
        assert body.get("currency") == "EUR", f"Expected EUR balance, got {body}"
        return body[
    "balance"
  ]

    def prepare_balance(self) -> float: """Reset, then read the persisted balance. The reset body is not the source of truth."""
        reset = self.reset_balance()
        self._require_ok(reset,
  "POST /api/reset-balance")
        return self.balance_amount()

    def _get(self, path: str) -> requests.Response:
        return self.session.get(f"{self.base_url}{path}", timeout=20)

    def _post(self, path: str, body: dict) -> requests.Response:
        return self.session.post(f"{self.base_url}{path}", json=body, timeout=20)

    def _require_ok(self, response: requests.Response, call: str) -> None:
        if response.status_code == 401:
            raise AssertionError(
                f"{call} rejected user id {self.user_id!r}: {response.text}. ""Set HQA_USER_ID to the user id from the assignment."
            )
        assert response.status_code == 200, (
            f"{call} expected 200, got {response.status_code}: {response.text}"
        )
}