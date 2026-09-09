# Resource Governor spike

ADR [0003](../../docs/adr/0003-quality-estimation-is-the-load-bearing-component.md) requires the cascade to be measured before an organization runtime is built on top of it. This is that measurement.

```bash
uv run python spikes/resource_governor/run.py              # schema-compliance estimator
uv run python spikes/resource_governor/run.py --control    # no-signal baseline
uv run python spikes/resource_governor/run.py --threshold 0.90
```

## What it measures

Seven labelled scenarios, each carrying ground truth about which rungs of the ladder produce a genuinely acceptable answer. That label is what makes the two failure directions countable:

- **false accept** — a wrong answer accepted at a cheap rung and shipped
- **false escalate** — a good cheap answer rejected, and paid for again higher up

A cascade with no ground truth looks free, because every accept counts as a saving.

The provider is scripted. This measures the **estimator and the policy**, not any model — mixing real model variance into the first measurement would make it impossible to tell which component moved.

## Results

| Configuration | Cost saved | False accepts | False escalates | Unresolved |
|---|---|---|---|---|
| schema-compliance, threshold 0.75 | 85.7% | 1 | 1 | 1 |
| schema-compliance, threshold 0.90 | 0% | 0 | 15 | 7 |
| control (always abstains) | 0% | 0 | 15 | 7 |

Baseline is sending every task straight to the frontier resource.

## What this tells us

**The mechanism works, and the saving is real.** At the default threshold the cascade avoided the frontier on six of seven scenarios, for an 85.7% cost reduction against frontier-always. That is in the range published cascade routing reports, which is a sanity check on the implementation rather than a claim about models.

**A structural estimator cannot catch a confident fabrication.** The `structurally-complete-but-wrong` scenario produces output with every required field present and all of it invented. The estimator scores it 0.85 and accepts. This is the false accept in the table, and it is not a bug to be fixed by tuning — it is the boundary of what structural checking can see. Any estimator that only inspects form will accept well-formed lies.

**The estimator's calibration ceiling caps the usable threshold range.** `SchemaComplianceEstimator` never scores above 0.85, because structure passing does not prove content correct. Raising the policy threshold to 0.90 therefore makes *every* answer insufficient, and the cascade collapses to the control: no savings, everything escalates, nothing resolves. That is correct behaviour, and it is worth seeing explicitly — an estimator whose ceiling sits below a policy's threshold contributes nothing but latency. Pairing a threshold with an estimator that cannot reach it is a configuration error the runtime should reject rather than silently degrade.

**Abstention behaves as designed.** The `unsupported-task-class` scenario has no estimator with evidence for it. Every rung abstains, the task climbs the whole ladder, and it ends unresolved rather than accepting an unjudged answer. Expensive, and correct: the system declines to guess.

**The control is the honest comparison.** With no signal, the cascade costs exactly the frontier-always baseline plus wasted local calls. Any estimator that does not beat this is not earning its complexity.

## What this does not tell us

These numbers come from hand-written scenarios and a scripted provider. They validate the mechanism and the accounting; they say nothing about how a real small model behaves on a real corpus.

The open question ADR 0003 raises is unanswered here: **does calibrated sufficiency estimation generalize across task classes?** Published work suggests it largely does not — routers do well on their training distribution and converge to similar performance under fair unified evaluation. This spike is consistent with that pessimism, since its one working estimator covers exactly two narrow task classes and abstains everywhere else.

## Next step

Point the same harness at real providers:

1. Implement a provider adapter against local inference and one hosted API.
2. Collect 100–200 real task instances in `structured_extraction`, with human-labelled acceptability.
3. Re-run and report the same four numbers.
4. If false accepts stay low and savings hold, extend to a second task class and check whether calibration transfers. If it does not transfer, ADR 0003 says to narrow the Principle 8 claim rather than route badly.

Only step 3 answers whether the economic thesis holds.
