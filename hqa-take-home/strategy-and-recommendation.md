# Strategy and recommendations

**Application:** https://qae-assignment-tau.vercel.app/?user-id=candidate-k5rNxtPos1Nn

1. **Test the money path first.** TP-01 checks a valid €10 bet. TP-02 checks a stake the user cannot cover. Filters, the error-modal buttons, and the in-progress `409` can wait.

2. **Keep API and UI in separate runs.** `pytest tests/api` checks what the service stores. `pytest tests/ui` checks the slip, receipt, and header. Run them one after the other. They share one balance.

3. **Trust `GET /api/balance`, not the reset body.** Reset says €125.50. The stored balance is €120.00. A valid €10 bet then drops it to €110.00, with payout `stake × odds`. The place-bet response labels that money **USD** while the balance stays **EUR**.

4. **Stop the balance going below zero.** Stake €125.51 is rejected as over the €100 cap, so it never tests “insufficient balance.” After the balance is €90, a stake of €90.01 is accepted and the stored balance becomes −€0.01. Reject that stake and leave the balance unchanged.

5. **Make the receipt match the slip.** The slip shows Manchester Utd first and payout €24.50. The receipt shows Chelsea vs Manchester Utd and calculates payout as stake × 2. Build the receipt from the place-bet response.
