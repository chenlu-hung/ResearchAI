import json

SCRIPT = "skills/paper-writer/scripts/check_prose.py"

CLEAN_SECTION = """\\section{Method}\\label{sec:method}
Our estimator combines cross-fitting with a projection step. The projection
removes the component of the nuisance error that is orthogonal to the score,
which is what drives the first-order bias term in the classical analysis, and
the cross-fitting removes the own-observation bias that remains.

Consider the linear case first. Here the projection reduces to a ridge
correction whose penalty is fixed by the sample-splitting ratio, so no tuning
parameter is introduced at this stage of the construction.

The general case follows by applying the same argument conditionally on each
fold. Because each fold's nuisance estimate is independent of the evaluation
points, the conditional expectation of the correction term vanishes, and the
remainder is controlled by the product-rate condition stated in Assumption
A2. A full statement appears in Theorem 4.1, whose proof also covers the
misspecified regime.

The contribution list is conventional here:
\\begin{itemize}
\\item A projection-corrected estimator.
\\item A product-rate consistency guarantee.
\\end{itemize}
"""

LISTY_SECTION = """\\section{Related Work}
We delve into the crucial prior work on this topic below.

\\begin{itemize}
\\item Method A studies the linear case with fixed designs and derives the
parametric rate under a moment condition on the noise terms.
\\item Method B extends the analysis to random designs under sparsity and
gives a matching lower bound for the dense regime as well.
\\item Method C considers the semiparametric regime with cross-fitting and
characterizes the second-order behaviour of the plug-in estimator.
\\end{itemize}

It is worth noting that these lines of work are closely related to ours.

\\begin{itemize}
\\item A second list whose first line carries several more words for the
ratio check of the linter to count here.
\\item A second list whose second line carries several more words for the
ratio check of the linter to count here.
\\end{itemize}

These threads motivate the construction that we analyze in the next section.
"""

PSEUDO_LIST_SECTION = """\\section{Discussion}
The estimator behaves well across the regimes we tested, and the theory
explains the transition point between them in terms of the effective rank.

\\paragraph{Efficiency.} The estimator attains the semiparametric bound.

\\paragraph{Scalability.} Each fold is fit independently and in parallel.

\\paragraph{Robustness.} Misspecification costs a second-order term only.
"""

UNIFORM_SECTION = """\\section{Experiments}
We evaluate the estimator on three synthetic designs with growing dimension
and report coverage and interval length over two hundred replications per
configuration, holding the nuisance learner fixed across all of the designs
so that differences reflect the correction alone and not the learner.

We compare against the uncorrected plug-in and the classical one-step
correction, using the same folds and the same nuisance estimates for every
method, so that the comparison isolates the projection step itself rather
than differences in sample splitting or in the learner configuration.

We observe nominal coverage for the corrected estimator in all designs while
the plug-in undercovers severely at the largest dimension, and the one-step
correction recovers only part of the gap, which matches the second-order
expansion given in the appendix and the constants computed there.
"""


def test_listy_ai_section_blocks(tmp_path, run_script):
    f = tmp_path / "related.tex"
    f.write_text(LISTY_SECTION, encoding="utf-8")
    r = run_script(SCRIPT, str(f), "--json")
    assert r.returncode == 1, r.stdout + r.stderr
    data = json.loads(r.stdout)
    rep = data["files"][str(f)]
    assert rep["blocking"]["lists_over_budget"]["count"] == 2
    assert "list_word_ratio" in rep["blocking"]
    tells = {b["tell"] for b in rep["blocking"]["banned_phrases"]}
    assert {"delve", "crucial", "it is worth noting"} <= tells
    assert all(b["line"] >= 1 for b in rep["blocking"]["banned_phrases"])


def test_clean_section_passes(tmp_path, run_script):
    f = tmp_path / "method.tex"
    f.write_text(CLEAN_SECTION, encoding="utf-8")
    r = run_script(SCRIPT, str(f))
    assert r.returncode == 0, r.stdout + r.stderr
    assert "RESULT: clean" in r.stdout


def test_pseudo_list_run_blocks(tmp_path, run_script):
    f = tmp_path / "discussion.tex"
    f.write_text(PSEUDO_LIST_SECTION, encoding="utf-8")
    r = run_script(SCRIPT, str(f), "--json")
    assert r.returncode == 1, r.stdout + r.stderr
    data = json.loads(r.stdout)
    runs = data["files"][str(f)]["blocking"]["pseudo_list_runs"]
    assert runs and runs[0]["length"] >= 3


def test_rhythm_warnings_do_not_block(tmp_path, run_script):
    f = tmp_path / "experiments.tex"
    f.write_text(UNIFORM_SECTION, encoding="utf-8")
    r = run_script(SCRIPT, str(f), "--json")
    assert r.returncode == 0, r.stdout + r.stderr
    data = json.loads(r.stdout)
    warnings = data["files"][str(f)]["warnings"]
    assert "same_opener_runs" in warnings
    assert warnings["same_opener_runs"][0]["word"] == "we"
    assert warnings["same_opener_runs"][0]["paragraphs"] == 3
    assert "uniform_length_runs" in warnings


def test_comments_math_and_envs_ignored(tmp_path, run_script):
    f = tmp_path / "setup.tex"
    f.write_text(
        "% we delve into crucial commented-out territory\n"
        "\\begin{equation}\n\\mathrm{crucial}(x) = 0\n\\end{equation}\n"
        "The design matrix is fixed and the noise is sub-Gaussian with a known\n"
        "proxy, which is all the analysis of the first regime requires here.\n\n"
        "Assumption A1 bounds the leverage of each observation, and A2 is the\n"
        "product-rate condition on the two nuisance errors described above.\n",
        encoding="utf-8",
    )
    r = run_script(SCRIPT, str(f), "--json")
    assert r.returncode == 0, r.stdout + r.stderr
    data = json.loads(r.stdout)
    rep = data["files"][str(f)]
    assert "banned_phrases" not in rep["blocking"]
    # "leverage" in live prose still surfaces as a warning, not blocking
    tells = {w["tell"] for w in rep["warnings"].get("phrases_and_patterns", [])}
    assert any("leverage" in t for t in tells)


def test_follows_inputs_and_reports_per_file(tmp_path, run_script):
    (tmp_path / "sections").mkdir()
    (tmp_path / "main.tex").write_text(
        "\\documentclass{article}\n\\begin{document}\n"
        "\\input{sections/01-related}\n\\end{document}\n",
        encoding="utf-8",
    )
    (tmp_path / "sections" / "01-related.tex").write_text(
        LISTY_SECTION, encoding="utf-8")
    r = run_script(SCRIPT, str(tmp_path / "main.tex"), "--json")
    assert r.returncode == 1, r.stdout + r.stderr
    data = json.loads(r.stdout)
    section_key = str(tmp_path / "sections" / "01-related.tex")
    assert "lists_over_budget" in data["files"][section_key]["blocking"]
    assert "skipped" in data["files"][str(tmp_path / "main.tex")]


def test_markdown_lists_and_phrases(tmp_path, run_script):
    f = tmp_path / "draft.md"
    f.write_text(
        "## Related work\n\n"
        "Prior approaches fall into two camps, which we showcase below in a\n"
        "crucial comparison of their assumptions and their guarantees.\n\n"
        "- Method A assumes fixed designs and proves a parametric rate.\n"
        "- Method B allows random designs under a sparsity condition.\n\n"
        "1. First enumerated point about the estimators considered here.\n"
        "2. Second enumerated point about the guarantees they provide.\n",
        encoding="utf-8",
    )
    r = run_script(SCRIPT, str(f), "--json")
    assert r.returncode == 1, r.stdout + r.stderr
    rep = json.loads(r.stdout)["files"][str(f)]
    assert rep["blocking"]["lists_over_budget"]["count"] == 2
    assert any(b["tell"] == "crucial" for b in rep["blocking"]["banned_phrases"])
