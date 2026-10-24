# Synthetic policy v1

Fictional demonstration policy. Not payment-network or legal guidance.

Effective from 2026-01-01T00:00:00Z (inclusive) to 2026-10-01T00:00:00Z (exclusive if present). Select by dispute opened_at.

Evaluate in ascending priority. The first applicable terminal action wins. Only use records visible at evaluation_at. Non-refund outcomes have amount zero.

## 10. DATA_INTEGRITY

Escalate missing or inconsistent capture data, negative balance, currency mismatch, or a pending movement.

Action: escalate. Parameters: `{}`.

## 20. FILING_WINDOW

Reject filing later than the allowed elapsed days. Exactly the limit remains eligible.

Action: reject. Parameters: `{"filing_window_days": 30}`.

## 30. ALREADY_REFUNDED

Reject an additional refund when the validated remaining balance is zero.

Action: reject. Parameters: `{}`.

## 40. CONFLICTING_EVIDENCE

Escalate unresolved material contradictions. A full refund promise and a partial actual refund are compatible.

Action: escalate. Parameters: `{}`.

## 50. MISSING_EVIDENCE

Request required evidence that is missing, unusable or unavailable at the evaluation cutoff.

Action: request_evidence. Parameters: `{"duplicate_charge": ["receipt", "two_completed_captures_same_order"], "not_received": ["receipt", "delivery_record"], "refund_missing": ["refund_confirmation"]}`.

## 60. UNSUPPORTED

Reject a claim contradicted by complete, unambiguous evidence; conflicts have already been escalated.

Action: reject. Parameters: `{}`.

## 70. REVIEW_THRESHOLD

Escalate an otherwise eligible refund above 20000 SGD cents; exactly 20000 is allowed.

Action: escalate. Parameters: `{"review_threshold_minor": 20000}`.

## 80. APPROVE

Recommend min(claimed amount, completed captures minus completed refunds and reversals).

Action: recommend_refund. Parameters: `{}`.

