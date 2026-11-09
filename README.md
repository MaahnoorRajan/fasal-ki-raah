# Fasal Ki Raah — فصل کی راہ

Working Urdu name for ReturnRoad. A student project by Maahnoor Rajan exploring whether smallholder farmers in rural Sindh and Punjab can keep more of their crop earnings by sharing spare space in goods vehicles already heading to the same mandi or collection point.

**Stage: local demo and discovery.** The [Django trip planner](docs/RUN-DEMO.md) checks stop order, spare weight, and arrival time against fictional potato trips. It compares estimated sale proceeds after fees. No real shipments, customer interviews, validated demand, revenue, or environmental savings are claimed.

**Try it:** download [Open Fasal Ki Raah.html](Open%20Fasal%20Ki%20Raah.html) from GitHub and open the downloaded file in a browser. The offline demo works without Python. For the Django version, follow the [local setup instructions](docs/RUN-DEMO.md).

## Project constraints

- At least two hours of development/learning time per week.
- First delivery platform: a mobile-friendly website.
- Preferred backend language: Python.
- Intended geography: rural Sindh and Punjab. Begin with one village or collection point and one mandi in whichever province offers access to farmers and drivers.
- First cargo scope: one crop that can travel without refrigeration, if local research supports it. Packaging, handling and weight limits remain undecided.
- Build incrementally, understand the code, verify each improvement, and make meaningful commits.

## The problem hypothesis

A smallholder may sell at the farm gate or pay for freight, loading, and fees to reach another buyer. Sharing spare space on an existing trip may improve what the farmer takes home if the vehicle, schedule and buyer are suitable. The farmer's current arrangement may work better.

The [Pakistan Economic Survey 2025–26, Table 1.3](https://finance.gov.pk/survey/chapter_26/Complete_PES2025_26.pdf) reports agriculture, forestry and fishing at 23.44% of GDP. An [IFPRI assessment](https://hdl.handle.net/10568/179396) identifies high transport costs alongside post-harvest losses and market access constraints. Neither shows that freight is the main cause of high food prices or that farmers always earn the lowest margin.

These are assumptions to test. Existing options may already serve the need well. Interviews may lead us to narrow, change, or abandon the spare-capacity premise.

## First users to investigate

Talk to a smallholder or tenant farmer, a goods-vehicle driver or owner, and, if possible, a crop buyer or collection-point operator on the same route. Find out who arranges transport today and whether farmers want to book themselves or through a trusted coordinator. Urdu is the proposed brand language; Sindhi, Punjabi, Saraiki or other interface languages should follow the needs of the first users.

## Proposed first complete workflow

1. A driver posts a scheduled trip with ordered pickup/drop-off areas, departure time, and capacity.
2. A farmer or authorised coordinator posts the crop, sacks or crates, weight, pickup area, destination, and latest acceptable arrival.
3. The application shows compatible trips and explains why they qualify.
4. The request shows the total transport quote in PKR, who pays, and who handles loading and unloading. Both parties accept the same terms.
5. Driver acceptance reserves capacity. A second booking cannot take space already reserved.
6. Both parties see booking status: requested, accepted, collected, delivered, cancelled.
7. The recipient confirms delivery using a short-lived code. Invalid or reused codes cannot complete delivery.

The first prototype will use a fixed ordered list of stops for one corridor. It must not claim live road routing, traffic predictions, detour optimisation, or full offline functionality.

## Matching rules to define and test

- Pickup and drop-off are supported stops in the correct journey order.
- Timing meets both the trip and shipment constraints.
- Cargo type is accepted and fits the available weight AND declared package space.
- Acceptance checks capacity again inside a database transaction.
- Capacity must be available on every overlapping trip leg; shipments on separate legs may reuse space only if the model explicitly supports that.
- Cancellation releases a reservation exactly once.

For the earliest version, reserving capacity for the whole trip is a simpler conservative alternative. Choose and document one approach before implementation.

## Proposed technology, subject to a small learning exercise

- Python and Django for models, forms, accounts, permissions, and server-rendered pages.
- HTML/CSS and a small amount of JavaScript for mobile-friendly interaction.
- SQLite for the first local learning prototype.
- PostgreSQL for a multi-user pilot, with concurrency tests for booking acceptance.
- Hosting chosen later based on Django/database support, cost, and maintenance needs.

An Android app, React frontend, payment integration, live GPS, automated pricing, and route optimisation are outside the first version. No paid service is required during discovery.

## Learning and delivery milestones

These are outcomes, not a promise to finish a production service in a fixed number of weeks.

| Milestone | Deliverable | What I practise | Completion evidence |
| --- | --- | --- | --- |
| 1. Discover | Anonymised interview notes and problem definition | Customer research, questioning assumptions | Recent delivery examples from senders and drivers; a decision on whether to proceed |
| 2. Define | Requirements, user stories, workflow sketch, selected corridor | Scope, acceptance criteria, UX | Clear first user and one end-to-end scenario |
| 3. Model | Entity diagram and small Python matching exercise | OOP, dates, validation, tests | Compatible trips accepted; wrong direction, timing, and capacity rejected |
| 4. Build a local slice | Accounts, trip posting, shipment requests | Django, forms, relational data, permissions | Two different users complete a request workflow |
| 5. Complete bookings | Acceptance, capacity reservation, cancellation, delivery code | Transactions, state transitions, ownership checks | Automated checks for double booking, cancellation, and invalid transitions |
| 6. Test usability | Mobile interface tested with fictional data | Accessibility, feedback, debugging | A few people complete the scenario; issues documented and addressed |
| 7. Deploy a demo | Hosted demonstration with synthetic data | Configuration, HTTPS, migrations, logs, backups | Repeatable deployment and smoke checks |
| 8. Decide on a pilot | A small, supervised operational plan | Real-world service design | Willing participants, clear handover/support/cancellation arrangements, and a workable cost model |

## Weekly rhythm: two hours

- 15 minutes: review the previous task and choose one small outcome.
- 70 minutes: learn and implement or interview.
- 25 minutes: check the result, explain it in my own words, and document decisions.
- 10 minutes: commit completed work and record the next step.

Research and documentation count as meaningful work. Do not invent code changes to maintain a contribution streak.

## What to measure

During discovery: actual sale receipts, who arranged and paid for freight, transport and handling costs, loaded and sold weight, losses, and available vehicle space.

For a pilot, compare realised sale receipts minus transport, loading and market fees across comparable sales, including the farm-gate alternative where relevant. Divide by kg loaded so spoiled or rejected produce is reflected in the result. This measures net sale proceeds before production costs, not farm profit. Track freight cost per kg, on-time arrival, and rejected quantity separately.

Revenue and commissions are hypotheses until tested. No emissions savings will be claimed without a defensible comparison with what journey the shipment would otherwise require.

## Documentation

- [Run and learn from the local Django prototype](docs/RUN-DEMO.md)
- [Discovery and interview kit](docs/DISCOVERY.md)
- [Potato case study: Punjab, January–February 2026](docs/POTATO-CASE.md)
- [Decision log](docs/DECISIONS.md)

## Learning and attribution

This is a student-led project. AI assistance was used to prepare this initial discovery plan. Customer evidence and implementation will be recorded as the work happens, with sources and contributions credited accurately.
