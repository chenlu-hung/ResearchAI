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

Pick perspectives that span at least *theorist + empiricist + one critic-style*.
For purely empirical topics, swap theorist for *Methodologist*.

## Generation prompt template

```
Topic: <topic>
Goal: produce 3–5 perspectives that collectively cover prior art exhaustively.

For each perspective:
- 1-line motivation: "What does this lens *uniquely* surface?"
- 5–10 search queries, each:
  - specific enough that a Semantic Scholar search returns <500 results
  - includes author names if a known seminal author exists
  - mix of broad ("X under distribution shift") and narrow ("weighted exchangeable conformal Tibshirani")
- 2–3 known seminal papers if you can recall them with high confidence
  (mark [VERIFY] if not 100% sure of details — retrieval will confirm)
```

## Anti-overlap rule

Two perspectives must not produce >40% overlapping search queries. If they
do, merge them or drop one. Run a quick mental dedup before retrieval.

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
    seed_papers:
      - "Vovk 2005 Algorithmic Learning in a Random World [VERIFY]"
      - "Tibshirani et al. 2019 Conformal prediction under covariate shift [VERIFY]"
  - name: "Critic"
    ...
```
