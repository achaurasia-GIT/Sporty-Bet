"""Fixed values from the single-bet specification and the OpenAPI contract."""

BASE_URL = "https://qae-assignment-tau.vercel.app"
USER_ID = "candidate-k5rNxtPos1Nn"

# Reset JSON shows 125.50, but GET /api/balance persists 120.00 for this user.
INITIAL_BALANCE = "120.00"
VALID_STAKE = "10"
STAKE_ABOVE_BALANCE = "125.51"

INSUFFICIENT_BALANCE_COPY = "Insufficient balance"
INSUFFICIENT_BALANCE_ERROR = "insufficient_balance"

HOME_SELECTION = "HOME"
EMPTY_SLIP_COPY = "Select odds to place a bet"
