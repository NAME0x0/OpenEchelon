# 0003. Quality estimation is the load-bearing component

**Status:** Accepted
**Date:** 2026-09-09

## Context

OpenEchelon's economic argument is Principle 8: use the cheapest intelligence that can reliably complete the task, and escalate when it cannot. The measured problem this attacks is real. Orchestrator-worker systems buy their quality with roughly an order of magnitude more tokens than a single agent, and that multiplier compounds through every handoff.

Published cascade routing shows the savings are attainable in principle — reported reductions range from most of the cost to nearly all of it, at close to frontier quality. But those results share a dependency that is easy to miss when reading the headline numbers: every cascade needs something that decides whether the cheap answer was good enough. Pre-router, quality estimator, escalation policy. The first and third are engineering. The second is not.

Recent unified evaluations of routing methods find that router performance is strongly benchmark-dependent, and that under fair comparison most routing methods converge to similar performance. Read plainly: routers work well on the distribution they were tuned for, and the advantage largely disappears off it. A general-purpose organizational runtime is, by construction, off-distribution.

This makes the estimator the single point on which the entire Resource Governor rests. If it is well calibrated, the escalation ladder in Principle 8 works and the cost thesis holds. If it is not, the ladder either escalates everything — in which case OpenEchelon is an expensive way to use frontier models — or escalates nothing, and returns confident wrong answers cheaply, which is worse.

Two failure directions, asymmetric in cost:

```text
                     estimator says GOOD
                              |
        actually good --------+-------- actually bad
              |                              |
        correct accept                 FALSE ACCEPT
        (cost saved)                   (wrong answer ships)

                     estimator says INSUFFICIENT
                              |
        actually good --------+-------- actually bad
              |                              |
        FALSE ESCALATE                 correct escalate
        (cost wasted)                  (recovered)
```

A false escalate costs money. A false accept costs correctness, and by Principle 19 it also defeats the review chain, because nothing downstream knows to look.

## Decision

Treat quality estimation as a first-class, independently evaluated component with an explicit interface, not as a helper inside the routing code.

Specifically:

1. The estimator is defined by an interface returning a **calibrated sufficiency probability plus an abstention option**, not a boolean. The escalation policy — not the estimator — owns the threshold, so the cost/correctness trade-off is a policy decision the organization can set per task class and per risk level.
2. **Asymmetric defaults.** Because a false accept is more expensive than a false escalate, the default threshold favours escalation, and any task class may raise or lower it with recorded justification.
3. **Estimators are per task class, and calibration is measured, not assumed.** A shipped estimator must carry evaluation evidence on the task class it claims to serve. An estimator with no evidence for a task class abstains, and abstention escalates.
4. **The Governor is validated before the organization is built on top of it.** The first implementation milestone is a spike that measures cost and quality on one task class with two tiers, reporting false-accept and false-escalate rates — not a working organization that happens to route.
5. **Every routing decision is recorded** with its estimator score, threshold, outcome, and later verification result, so estimators can be re-scored against ground truth as it arrives. Principle 26 requires the organization to learn which resources work for which tasks; that learning is impossible without this record.

## Consequences

The Resource Governor gains a hard, measurable success criterion, and the project gains an early answer to the question that decides whether its economics work at all.

Development order changes. The cost thesis gets tested before the organizational runtime is built on it, which is uncomfortable — the organization is the interesting part — but building the interesting part first and discovering the estimator does not generalize would waste the larger investment.

The project takes on an evaluation burden. Estimators need labelled outcomes per task class, and producing those is ongoing work, not a one-off.

There is a real possibility the answer is negative for general task classes. If calibrated estimation only works on narrow, well-specified task classes, the honest response is to narrow Principle 8's claim — cheapest sufficient intelligence *within task classes the organization has evidence for*, frontier-by-default elsewhere — rather than to keep the general claim and route badly.

## Revisit if

A general-purpose estimator demonstrates calibration across task classes it was not tuned on, which would let the Governor drop per-class evidence requirements. Or the opposite: repeated evaluation shows calibration does not transfer at all, in which case the escalation ladder should be replaced by explicit per-task-class model assignment, and Principle 8 restated to match what is actually achievable.
