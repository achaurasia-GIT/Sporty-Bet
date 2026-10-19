# Test Plan — Single Bet Placement

**Application:** https://qae-assignment-tau.vercel.app/?user-id=candidate-k5rNxtPos1Nn
**Scope:** Desktop web, football, upcoming matches, single bet only
**Out of scope:** Live betting, accumulators, other sports, mobile-specific UX

## Setup

- Open the app with a stable `user-id` query parameter. The same value must be sent as the `x-user-id` header on every API call.
- Before each scenario, reset funds with `POST /api/reset-balance`, then confirm the balance with `GET /api/balance`. Do not trust the reset response alone: that payload returns **€125.50**, while the persisted balance is **€120.00**.
- Use the first match returned by `GET /api/matches` unless a scenario says otherwise. Record its id, home team, away team, and the three odds before you click anything.
- Payout is `stake × odds` and includes the original stake. Compare money values to 2 decimal places.

## Spec note used while writing expected results

The business rules and the minimum UI copy say the smallest stake is **€1.00**. The validation table in the same specification says **€1.01**. The OpenAPI schema sets `minimum: 1` and `maximum: 100`. Scenarios below treat **€1.00 and €100.00 as the inclusive limits**. A rejection of exactly €1.00 is a defect against the business rule and the API contract.

## Scenarios

### TP-01 — Place a valid single bet and confirm payout, receipt, and balance

| | |
|---|---|
| **Priority** | Critical |
| **Type** | Happy path |

**Risk rationale:** This is the only path that takes the customer's money. A wrong payout, a receipt that does not match the slip, or a balance that does not drop by the stake is a direct financial and trust failure.

**Steps:**

1. Reset and confirm the balance is €120.00 in the header and in the bet slip.
2. On the first match, click the **1** (home) odds button.
3. Confirm the bet slip shows that match, selection **1** / home, and the same decimal odds shown on the button.
4. Enter stake `10`.
5. Confirm the slip shows potential payout `10 × displayed odds`, rounded to 2 decimal places (example from the domain notes: odds 2.45 → €24.50).
6. Click **Place Bet**.
7. Wait until the button leaves the **Placing...** state.
8. Read the success receipt, then close it.
9. check that potential payout is stake*odd
10. Read the header balance it should be original-stake and `GET /api/balance`.

**Expected result:**

- The button shows an in-progress state, then one final success outcome. No error modal appears.
- The receipt shows a bet id, the same match (home team listed first), selection, stake €10.00, the odds captured at click time, potential payout equal to stake × those odds, and a placement timestamp.
- Header balance, slip balance, and `GET /api/balance` all show €110.00.
- Closing the receipt returns to the match list with no active selection and an empty stake.
- on reciept check that potential payout is stake*odd 10*odd

---

### TP-02 — Reject a stake above the available balance without debiting funds

| | |
|---|---|
| **Priority** | Critical |
| **Type** | Negative / business rule |

**Risk rationale:** Accepting a stake the user cannot cover creates a bet the book cannot settle, or it can drive the balance negative. The balance must stay unchanged on every rejected attempt, on both UI and API.

**Steps:**

1. Reset and confirm the balance is €120.00.
2. Select any odds button so the slip is active.
3. Enter stake `125.51`.
4. Attempt **Place Bet**.
5. Repeat the same request with `POST /api/place-bet` using that match id, selection `HOME`, and stake `125.51`.
6. Read the on-screen balance and `GET /api/balance`.

**Expected result:**

- The UI blocks placement and shows **Insufficient balance**. No success receipt appears.
- The API returns **422** with an insufficient-balance error. It does not return 200.
- Balance remains €120.00 in the header, the slip, and `GET /api/balance`.

---

### TP-03 — Accept the inclusive stake limits and reject the values just outside them

| | |
|---|---|
| **Priority** | High |
| **Type** | Boundary |

**Risk rationale:** Off-by-one limits either block a legal minimum bet or let a user exceed the €100 per-bet cap. These four values define the whole accepted range.

**Steps:**

1. Reset the balance before each attempt so earlier stakes do not affect the result.
2. Select any valid outcome.
3. Attempt stakes `0.99`, `1.00`, `100.00`, and `100.01` as four separate placements.
4. For `1.00` and `100.00`, also send the same body to `POST /api/place-bet`.
5. After each attempt, record whether a receipt appeared and what `GET /api/balance` returns.

**Expected result:**

- `0.99` is blocked in the UI with **Minimum stake is €1.00**, and the API returns **422**. Balance is unchanged.
- `1.00` is accepted. Payout equals `1.00 × odds`. Balance decreases by exactly €1.00.
- `100.00` is accepted. Payout equals `100.00 × odds`. Balance decreases by exactly €100.00 (from €120.00 to €20.00 when this is the only bet).
- `100.01` is blocked in the UI with **Maximum stake is €100.00**, and the API returns **422**. Balance is unchanged.
- If the product rejects `1.00` because it implemented the €1.01 row in the validation table, log that as a spec-conflict defect. The business rule, UI copy, and OpenAPI schema all allow €1.00.

---

### TP-04 — Reject an empty, non-numeric, or over-precise stake

| | |
|---|---|
| **Priority** | High |
| **Type** | Negative / validation |

**Risk rationale:** The stake field is the only amount the user types. Accepting blank, text, or a third decimal can persist a stake the user did not intend, or let the client and API disagree on the amount charged.

**Steps:**

1. Select a valid outcome.
2. Leave the stake empty and click **Place Bet**.
3. Enter `abc` and click **Place Bet**.
4. Enter `10.999` and click **Place Bet**.
5. Enter `10.5` and click **Place Bet** only after the three failures above, as a control that a legal 1-decimal stake still works. Then reset the balance.
6. Call `POST /api/place-bet` three times with stake omitted, stake `"10"`, and stake `10.999`. Use a real match id and selection `HOME`.
7. Confirm the balance after the rejected calls.

**Expected result:**

- Empty stake: placement is blocked. UI indicates the stake is required. No receipt.
- `abc`: the field accepts only a numeric value with one decimal separator, or the UI rejects it. The API, given a non-numeric stake, returns **400** or **422** and does not place the bet.
- `10.999`: UI and API reject more than 2 decimal places. No receipt, balance unchanged.
- `10.50` (entered as `10.5`) is a valid stake and can be placed after the negative checks.
- None of the rejected API calls change `GET /api/balance`.

---

### TP-05 — Keep only one selection, and make the receipt match the selection that was actually placed

| | |
|---|---|
| **Priority** | High |
| **Type** | Happy path / state |

**Risk rationale:** The slip holds one bet. If a second click does not replace the first, the user can be charged for the wrong team or the wrong price. The receipt is the customer's proof, so every field must match the slip at the moment of placement, not an earlier selection.

**Steps:**

1. Reset and confirm the balance.
2. On match A, click **1** (home). Note the team names and home odds.
3. On the same match, click **2** (away).
4. Confirm the slip now shows away, the away odds, and no leftover home selection.
5. On a different match, click **X** (draw). Confirm the slip replaces match A entirely with this match and the draw odds.
6. Enter stake `10` and place the bet.
7. Compare the receipt with what the slip showed immediately before submit.
8. Close the receipt and look at the slip.

**Expected result:**

- Each new odds click replaces the previous selection. The slip never shows two matches or two outcomes.
- The receipt match name lists the home team first, then the away team, even though the selection is draw.
- Receipt selection, stake €10.00, odds, and payout match the slip at submit time. Odds are the odds shown when the user clicked, not a refreshed price.
- Payout is `10 × draw odds` for the match that was on the slip.
- Balance decreases by €10.00 only.
- Closing the receipt clears the active selection and the stake.

---

### TP-06 — API rejects an invalid selection or an unknown match and does not move the balance

| | |
|---|---|
| **Priority** | High |
| **Type** | Negative / API business rule |

**Risk rationale:** The UI only offers 1 / X / 2, so a bad selection or a made-up match id will not be caught by clicking through the list. A client or a retry can still send one. Placing that bet would record a wager on a market that does not exist.

**Steps:**

1. Reset and confirm the balance with `GET /api/balance`.
2. `POST /api/place-bet` with a real `matchId`, selection `WIN`, and stake `10`.
3. `POST /api/place-bet` with `matchId` `does-not-exist`, selection `HOME`, and stake `10`.
4. `POST /api/place-bet` with the `x-user-id` header omitted, a real match id, selection `HOME`, and stake `10`.
5. Call `GET /api/balance` again with the original user id.

**Expected result:**

- `WIN` returns **422**. The selection must be `HOME`, `DRAW`, or `AWAY`.
- An unknown match id returns **422**. A blank match id is also rejected.
- A missing `x-user-id` returns **401** and does not create a bet for any user.
- After all three calls, the balance is still the post-reset value. No success payload (`message`, `odds`, `payout`) is returned for any of them.

## Coverage map

| Scenario | Happy path | Negative / validation | Boundary | Layer |
|---|---|---|---|---|
| TP-01 Valid bet, payout, receipt, balance | Yes | | | UI + API |
| TP-02 Stake above balance | | Yes | | UI + API |
| TP-03 €0.99 / €1.00 / €100.00 / €100.01 | | | Yes | UI + API |
| TP-04 Empty, non-numeric, 3 decimals | | Yes | | UI + API |
| TP-05 One active selection and receipt match | Yes | | | UI |
| TP-06 Invalid selection, unknown match, no user | | Yes | | API |

## Not in this plan, on purpose

Date and odds filters, the error-modal **Rebet** / **Close** / **X** behavior, and `409` when a bet is already in progress are real risks, but they are secondary to taking the wrong amount or booking the wrong selection. They belong in exploratory testing and in the follow-up bug report if they fail, not in the first six scenarios.
