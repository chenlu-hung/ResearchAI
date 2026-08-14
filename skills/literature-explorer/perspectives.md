# Perspective Archetypes for Stats/ML Surveys

A *perspective* is a viewpoint from which the topic is interrogated. Different
perspectives surface different prior art. Generate 3–5 perspectives per topic
by picking from the archetypes below and tailoring to the topic.

## Default archetypes

| Archetype | Asks | Example for "Conformal prediction" |
|---|---|---|
| **Theorist** | What are the formal guarantees? What assumptions are needed? | Finite-sample coverage proofs; minimax rates; exchangeability requirements |
| **Empiricist** | What works in practice? What datasets/benchmarks? | Calibration on CIFAR, ImageNet; conformal in vision/NLP |
| **Methodologist** | Algorithmic primitives, computational tricks. | Split conformal, full conformal, jackknife+, weighted, cross-validation+ |
| **Critic** | Failure modes, limitations, where the framework breaks. | Distribution shift, label noise, miscalibration under heavy tails |
| **Adjacent fields** | What does Statistics / Optimization / Bayesian community say? | Connection to PAC-Bayes, predictive distributions, scoring rules |
| **Applied** | High-stakes deployments; regulatory or domain requirements. | FDA-grade medical imaging; safety-critical robotics |
| **Historical** | Lineage, who introduced what when, paradigm shifts. | Vovk's foundational work; recent post-2018 revival |
| **Math skeleton** | Strip all application vocabulary: what is the bare mathematical structure, and who else has built it? | "Exchangeable rank statistic with a reweighted empirical quantile" searched in signal processing, survey sampling, ranking |

Pick perspectives that span at least *theorist + empiricist + one critic-style*.
For purely empirical topics, swap theorist for *Methodologist*.

## Mandatory set for `corpus-prefetch`

For a normal survey the archetypes above are a menu. For
`corpus-prefetch.md` four axes are **mandatory** and none may be dropped:
the application-field axis (built from the standard archetypes),
**Math skeleton**, **Adjacent fields**, and **Historical**. Math skeleton runs
across fields *and* across decades with explicit pre-2015 windows — a provider
default that favors recent work is a coverage failure, not an absence of prior
art.

## Generation prompt template

```
Topic: <topic>
Goal: produce 3–5 perspectives that collectively cover prior art exhaustively.

For each perspective:
- 1-line motivation: "What does this lens *uniquely* surface?"
- 5–10 search queries, each:
  - specific enough that a Semantic Scholar search returns <500 results
  - may include a recalled author/title only as an explicitly unverified query
  - mix of broad ("X under distribution shift") and narrow ("weighted exchangeable conformal Tibshirani")
- 2–3 seminal-work query seeds when useful. Model recall is never evidence,
  regardless of confidence: mark every recalled name/detail `[VERIFY]`, persist
  it as a query-run, and do not create a work/claim from it until retrieval.
```

## Anti-overlap rule

Two perspectives must not produce >40% overlapping search queries. If they
do, merge them or drop one. Run a quick mental dedup before retrieval.

Execute the resulting list under `shared/prompts/evidence_grounding.md`: query
the vault first, persist the run (including empty results), then use external
retrieval only for unresolved coverage. The generated perspective and seed list
cannot establish prior art or novelty.

## Output schema

```yaml
perspectives:
  - name: "Theorist"
    motivation: "What finite-sample guarantees hold and under what assumptions"
    queries:
      - "weighted conformal prediction Tibshirani 2019"
      - "exchangeability conformal coverage proof"
      - "conformal prediction beyond exchangeability"
      - ...
    seed_queries:
      - "Vovk 2005 Algorithmic Learning in a Random World [VERIFY]"
      - "Tibshirani et al. 2019 Conformal prediction under covariate shift [VERIFY]"
  - name: "Critic"
    ...
```
