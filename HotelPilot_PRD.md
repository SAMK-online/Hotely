# Hotely PRD

**Tagline:** Hotely: The last piece of SaaS every hotel needs  
**Scope:** Agentic operations layer that automates pricing, voice and messaging, housekeeping and maintenance scheduling, billing and recovery, and daily ops reporting.  
**Target automation:** 70 to 80 percent of routine tasks with clear human approval gates.

---

## 1. Summary

Hotely sits on top of a hotel's PMS, payments, and channels. It watches demand signals like inbound flights and events, communicates with guests by voice and messaging, books and modifies reservations with pay links, balances staff schedules, and explains every action in a single audit trail.

---

## 2. Goals and non-goals

**Goals**
- Lift revenue with proactive pricing and upsells while respecting caps and parity.
- Cut manual work for messages, calls, scheduling, payment recovery.
- Improve guest satisfaction with fast, consistent, multilingual responses.
- Provide one cockpit for staff with transparent logs and rollbacks.

**Non-goals**
- Building a full PMS.
- Replacing humans for high risk decisions like walks or VIP comps.
- Deep building controls beyond basic status reads.

---

## 3. Users and personas

- **General Manager**: wants revenue and guest score gains with low risk.  
- **Revenue Manager**: wants explainable pricing that respects guardrails.  
- **Front Desk Lead**: wants faster check in, fewer repetitive questions.  
- **Housekeeping Supervisor**: wants clean daily plans and fewer reworks.  
- **Owner or Asset Manager**: wants portfolio metrics and compliance.

---

## 4. Success metrics

- RevPAR plus 5 to 8 percent in select service, ADR up without occupancy penalty.  
- Payment success plus 10 points on first failure cohort.  
- Messaging first response under 3 minutes, 60 to 70 percent containment.  
- Housekeeping minutes per clean down 10 to 15 percent.  
- Flight driven pricing uplift hit rate above 65 percent, regret rate under 10 percent.  
- Complaint rate on price swings not above baseline.

---

## 5. Agent topology

1. **Demand and Rate Manager**  
2. **Flight Signal Scout**  
3. **Guest Lifecycle Orchestrator**  
4. **Housekeeping and Maintenance Scheduler**  
5. **Billing and Revenue Recovery**  
6. **Comms and Concierge**  
Optional: **Channel and Inventory Optimizer**  
Overlay: **Ops Copilot** for status, metrics, audit trail.

Each agent plans, acts, explains. A lightweight supervisor coordinates order and escalation.

---

## 6. System architecture

**Data plane**
- Connectors: PMS and CRS, channel manager, payments, messaging, locks and IoT, POS.  
- Event bus with normalized events: reservation.created, payment.failed, room.cleaned.  
- Feature store: pace by segment, VIP flag, demand lift index, sentiment.  
- Storage: SQL for ops data, vector store for retrieval.

**Control plane**
- Policy engine: caps, cushions, quiet hours, approvals, parity rules.  
- Audit service: who, what, when, why, previous values, rollback handle.  
- Secrets and config per property.

**Serving**
- Action adapters: PMS, payments, messaging, voice gateway.  
- Web app for Ops Copilot and settings.  
- Voice gateway: Twilio or Retell AI for ASR, TTS, call control with PCI safe payment flow.

---

## 7. Integrations

- PMS and CRS: Mews or Cloudbeds as v1 targets.  
- Channel manager: SiteMinder or Cloudbeds.  
- Payments: Stripe first. Tokenization, pay links, 3DS, partial capture.  
- Messaging: WhatsApp Business Cloud, Twilio SMS, SMTP for email.  
- Voice: Twilio Programmable Voice or Retell AI.  
- IoT and locks: status reads, optional digital keys when supported.  
- Calendar: internal schedules for housekeeping and maintenance tasks.

---

## 8. Data model (minimal)

- **Guests**: guest_id, contact, language, preferences, consent, VIP flag  
- **Reservations**: res_id, guest_id, dates, room_type, status, channel, ADR, deposit_status, ETA, notes  
- **Rooms**: room_id, type, status, OOO_reason, attributes  
- **Housekeeping_task**: task_id, room_id, res_id, type, priority, assignee, due_at, status  
- **Payments**: payment_id, res_id, method, amount, status, last_attempt_at, code  
- **Messages**: msg_id, res_id or guest_id, channel, direction, intent, outcome  
- **Rates**: date, room_type, base_BAR, restrictions, last_change_source, reason  
- **Tickets**: ticket_id, room_id, issue, severity, SLA target, status  
- **Signals**: date, segment, demand_lift_index, seat_capacity_delta, event_weight, ops_disruption_risk, confidence  
- **Audit_log**: actor, object_type, object_id, change_set, timestamp, policy_id, approval, rollback_key

---

## 9. Policies and guardrails

- Rate change caps per room type per day and weekly net cap.  
- Overbooking cushion configured by property.  
- Quiet hours for outbound contact.  
- PCI safe paths only for cards: DTMF capture or pay link.  
- Group and corporate fences never overridden.  
- Parity protection for direct site and OTA rules.

---

## 10. Core workflows

### 10.1 Flight aware pricing

**Objective**  
Use inbound flight and event signals to nudge rates on the correct dates with clear limits.

**Inputs**  
Scheduled and actual arrivals by hour for home and alternate airports, aircraft capacity class, holidays and events, pace, optional fare pressure proxy.

**Computation**  
`demand_lift_index = 0.7 * seat_capacity_delta + 0.3 * fare_pressure_proxy + event_weight`  
Confidence reflects data freshness and source agreement. Minimum sample size applies.

**Decision logic**  
- Index 0.2 to 0.4: propose ADR plus 5 to 8 percent.  
- Index 0.4 to 0.7: propose plus 9 to 15 percent.  
- Index above 0.7: propose up to cap, require approval on peak holidays.  
- If ops_disruption_risk is high: freeze tonight’s hikes, shift to next day.  
- Suggestions only when confidence under 0.6.

**Action**  
Push fenced rate plans or restrictions via PMS or channel manager. Never overwrite base BAR. Log dates, seats vs baseline, holiday or event flags, confidence, caps applied.

**Ops Copilot card**  
Seats plus 18 percent Fri evening. Proposed ADR plus 8 percent Fri and plus 5 percent Sat. Confidence 0.78. Within caps. Parity OK.

---

### 10.2 Automated voice bookings and changes

**Intents**  
New booking, modify, cancel, late check in or checkout, amenity request, billing question, directions and parking.

**Flow**  
Greet and record consent, detect language, classify intent, offer 2 to 3 inventory options with price and terms, capture guest details, take deposit via pay link or DTMF inside PCI scope, write to PMS, send confirmation, update housekeeping tasks, open tickets if needed. Handoff to staff when rules or confidence require it.

**Guardrails**  
Rate caps and cushions respected. VIP or group routes to human. No card data in transcripts.

---

### 10.3 Guest messaging

- Pre stay: ID, ETA, deposit, directions, upgrades.  
- In stay: welcome, digital key link when supported, service requests, recovery when sentiment dips.  
- Post stay: folio, feedback, public review reply draft, winback if low score.  
- Quiet hours respected. Multilingual. Opt out honored.

---

### 10.4 Housekeeping and maintenance

- Inputs: arrivals, departures, stayovers, roster, attributes, tickets.  
- Daily plan: priorities, VIPs, rush cleans for early check in, live reassignments.  
- Inspections when configured.  
- Maintenance: tickets with severity, block room only when required, auto release after pass.

---

### 10.5 Billing and recovery

- Detect failed cards and unpaid folios.  
- Smart retry schedule based on code.  
- Send 3DS pay links when required.  
- Partial captures when allowed.  
- Escalate after threshold.  
- Post success to PMS and close items quickly.

---

## 11. Functional requirements

**Demand and Rate Manager**
- Pull current rates and restrictions.  
- Accept demand_lift_index, output proposals by room type and date within caps.  
- Push changes and provide rollback.

**Flight Signal Scout**
- Poll airports every 30 to 60 minutes for next 21 days.  
- Aggregate by date and arrival bands.  
- Compute baselines and confidence.  
- Fail over to secondary source or nowcast.

**Guest Lifecycle Orchestrator**
- Orchestrate pre, in, post stay flows with consent and quiet hours.  
- Raise tickets on negative sentiment.

**Housekeeping and Maintenance Scheduler**
- Create and assign tasks, rebalance on late checkout or early check in.  
- Prevent assignment of occupied or out of order rooms.

**Billing and Revenue Recovery**
- Detect failures, run retry cadence, generate pay links, write back success.  
- Alert after thresholds and respect policy windows.

**Comms and Concierge**
- Answer FAQs with reservation context.  
- Offer upsells like late checkout, breakfast, room upgrades.  
- Draft public review replies for approval.

**Ops Copilot**
- Today board, metrics, alerts, daily digest to Slack or email.  
- Full audit trail with filters and rollbacks.

---

## 12. Events and API contracts

**Event names**
- reservation.created, reservation.modified, payment.failed, payment.succeeded, housekeeping.task.created, housekeeping.task.completed, flight.signal.updated, rate.change.proposed, rate.change.applied, voice.call.completed.

**Action adapters**
- PMS: create_reservation, update_reservation, cancel_reservation, attach_note, set_rate_plan, set_restrictions, set_room_status.  
- Payments: create_pay_link, tokenize, capture, refund.  
- Messaging: send_whatsapp, send_sms, send_email.  
- Voice: start_call_flow, warm_transfer, end_call.

Payloads are JSON, idempotent on writes, with compact fields and timestamps.

---

## 13. UX and copy

- Tone: warm, concise, service first.  
- Pricing cards: show percent change, dates, reason, cap, confidence.  
- Voice: short sentences, confirm all key fields and totals, capture explicit consent.  
- Messaging: avoid pressure, always include opt out.

---

## 14. Security and compliance

- PCI DSS: card data only through payment provider. Pay links or DTMF capture.  
- PII encryption at rest with per tenant keys, strict roles.  
- Data residency options for EU properties.  
- Incident response: initial SLA 4 hours, postmortem within 24 hours.

---

## 15. Rollout plan

- **Phase 1**: Messaging plus Billing plus Ops Copilot in read only.  
- **Phase 2**: Housekeeping Scheduler plus flight aware pricing in suggest mode.  
- **Phase 3**: Channel and Inventory Optimizer and full demand forecasting.  
- **Voice**: enable after PCI flow is verified.

---

## 16. QA and acceptance tests

**Pricing**
- Price change never exceeds caps.  
- Parity fence respected.  
- Suggestions only when confidence is low.  
- Regret rate under 10 percent in first 30 days.

**Voice**
- 60 to 70 percent containment for routine calls.  
- Recordings tagged with outcome.  
- No PAN in transcripts.  
- Handoff includes whisper summary.

**Messaging**
- No messages during quiet hours.  
- Correct language detected with safe fallback.  
- Upsell acceptance updates reservation and folio.

**Housekeeping**
- No task on occupied or out of order rooms.  
- Late checkout rebalances within 5 minutes.

**Billing**
- Retry cadence follows code map.  
- Pay link success writes back within 60 seconds.

---

## 17. Monitoring and alerts

- Connectors health, latency, failure rate.  
- Pricing jobs: proposals, applied, reverted.  
- Voice: ASR confidence, containment, abandoned pay links.  
- Messaging: delivery, response, opt outs.  
- Housekeeping: backlog, average clean time.  
- Billing: aged balances, recovery rate.

Each alert links to a runbook.

---

## 18. Risks and mitigations

- External data errors: use confidence thresholds and minimum sample sizes.  
- Staff trust: start in shadow mode, keep explainable cards, easy rollbacks.  
- Over messaging: frequency caps, quiet hours, suppression lists.  
- Integration drift: contract tests and sandbox checks before updates.

---

## 19. Open questions

- PMS and channel manager for v1.  
- Home and alternate airports for flight signals.  
- Approval thresholds for pricing and comps.  
- Languages for voice and messaging.  
- Parity policy details per channel.

---

## 20. Northern Virginia addendum

**Property scope**: 60 to 150 keys in Arlington, Alexandria, Tysons, Reston, Fairfax.  
**Airports**: DCA and IAD primary, BWI backup.  
**Weights**  
- Near DCA: DCA 0.6, IAD 0.3, BWI 0.1.  
- West of 495 and Reston or Tysons: IAD 0.6, DCA 0.3, BWI 0.1.  
**Arrival bands**: morning 05:00 to 11:00, midday 11:00 to 17:00, evening 17:00 to 23:00, late 23:00 to 02:00.  
**Events**: federal holidays, cherry blossoms, GMU graduations, DC races, fall conferences.  
**Caps**  
- Weekdays: max daily move 10 percent.  
- Weekends: max daily move 12 percent.  
- Weekly net cap: 18 percent.  
**Rollbacks**  
- If pickup drops below trailing median for 24 hours after a lift: recommend rollback by half of last uplift.  
**Quiet hours**: 21:00 to 08:00 Eastern for outbound messages.  
**Voice**: 703 or 571 numbers, pay links during call, handoff for VIP or groups.  
**Billing retries**: T plus 1 hour, T plus 6 hours, T plus 24 hours with 3DS links when needed.

---

## 21. Four week build plan

**Week 1 foundations**
- Connect PMS in read only. Map rooms, rate plans, taxes, fees.  
- Connect Stripe and messaging. Provision local numbers.  
- Stand up event bus, policy engine, audit log.  
- Ops Copilot read only with arrivals, departures, OOO, failed payments.

**Week 2 messaging and billing**
- Pre stay, check in, checkout, FAQ flows on WhatsApp and SMS.  
- Deposits and recovery via pay links with write back.  
- Housekeeping plan v1 from arrivals and departures.  
- Voice shadow mode. Record intents, no actions.

**Week 3 voice actions and HK v2**
- Enable voice for bookings and simple changes with pay links.  
- Late checkout and early check in rebalance within 5 minutes.  
- Sentiment routing to service recovery.  
- Flight Signal Scout in suggest mode.

**Week 4 pricing go live**
- Safe uplifts on shoulder dates, human approval on peaks.  
- Add upsells: late checkout, breakfast, higher floor or view.  
- Daily digest to Slack or email with wins and flags.

---

## 22. Build guidance for Cursor or Claude Code

- Generate typed client scaffolds for PMS, payments, messaging, voice.  
- Implement event schemas and contract tests first.  
- Ship Ops Copilot read only in Week 1 to create feedback loop.  
- Add policy engine unit tests for caps, cushions, quiet hours.  
- Keep configuration per property in one file for fast rollout.  
- Gate each automation behind feature flags for safe ramp.

---

**Status:** ready to convert into tasks and repos.
