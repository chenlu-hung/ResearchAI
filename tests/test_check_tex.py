import json

SCRIPT = "skills/paper-writer/scripts/check_tex.py"

BIB = """@article{good2020,
  title = {A Fine Paper},
  author = {Good, Alice},
  year = {2020},
}
@article{unused2019,
  title = {Never Cited},
  author = {Idle, Bob},
  year = {2019},
}
"""


def _paper(tmp_path, intro_body):
    (tmp_path / "sections").mkdir()
    (tmp_path / "figures").mkdir()
    (tmp_path / "figures" / "plot.pdf").write_bytes(b"%PDF-1.4 fake")
    (tmp_path / "main.tex").write_text(
        "\\documentclass{article}\n"
        "% \\cite{commentedout9999} should be ignored\n"
        "\\begin{document}\n"
        "\\input{sections/01-intro}\n"
        "\\end{document}\n",
        encoding="utf-8",
    )
    (tmp_path / "sections" / "01-intro.tex").write_text(intro_body, encoding="utf-8")
    bib = tmp_path / "refs.bib"
    bib.write_text(BIB, encoding="utf-8")
    return tmp_path / "main.tex", bib


def test_blocking_findings_detected(tmp_path, run_script):
    main, bib = _paper(
        tmp_path,
        "\\section{Intro}\\label{sec:intro}\\label{sec:intro}\n"
        "As shown by \\citet{good2020} and \\cite{missing2021,good2020}.\n"
        "See Section~\\ref{sec:nolabel}.\n"
        "\\includegraphics[width=\\linewidth]{figures/plot}\n"
        "\\includegraphics{figures/ghost}\n"
        "We discuss limitations of the approach.\n",
    )
    r = run_script(
        SCRIPT, str(main), "--bib", str(bib),
        "--must-include", "limitations", "broader_impact",
        "--json",
    )
    assert r.returncode == 1, r.stdout + r.stderr
    data = json.loads(r.stdout)
    assert data["undefined_citations"] == ["missing2021"]
    assert "commentedout9999" not in json.dumps(data)
    assert data["undefined_refs"] == ["sec:nolabel"]
    assert data["duplicate_labels"] == ["sec:intro"]
    assert data["missing_graphics"] == ["figures/ghost"]
    assert data["must_include_found"] == ["limitations"]
    assert data["must_include_missing"] == ["broader_impact"]
    assert data["unused_bib_entries"] == ["unused2019"]


def test_clean_paper_exits_zero(tmp_path, run_script):
    main, bib = _paper(
        tmp_path,
        "\\section{Intro}\\label{sec:intro}\n"
        "As shown by \\citet{good2020}, see \\ref{sec:intro}.\n"
        "\\includegraphics{figures/plot}\n"
        "We discuss limitations honestly.\n",
    )
    r = run_script(SCRIPT, str(main), "--bib", str(bib), "--must-include", "limitations")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "RESULT: clean" in r.stdout


def test_unknown_must_include_token_blocks(tmp_path, run_script):
    main, bib = _paper(tmp_path, "\\cite{good2020} and \\label{a} \\ref{a}\n")
    r = run_script(SCRIPT, str(main), "--bib", str(bib), "--must-include", "no_such_token")
    assert r.returncode == 1
    assert "no_such_token" in r.stdout


def test_pattern_flag_supplies_new_token(tmp_path, run_script):
    body = "\\cite{good2020} \\label{a} \\ref{a}\nData and code are available.\n"
    main, bib = _paper(tmp_path, body)
    # without --pattern the custom token is unknown → blocking
    r = run_script(SCRIPT, str(main), "--bib", str(bib),
                   "--must-include", "data_availability")
    assert r.returncode == 1
    # with --pattern it resolves and is found in the source
    r = run_script(
        SCRIPT, str(main), "--bib", str(bib),
        "--must-include", "data_availability",
        "--pattern", r"data_availability=data\s+and\s+code\s+are\s+available",
        "--json",
    )
    assert r.returncode == 0, r.stdout + r.stderr
    assert "data_availability" in json.loads(r.stdout)["must_include_found"]


def test_pattern_flag_rejects_bad_spec(tmp_path, run_script):
    main, bib = _paper(tmp_path, "\\cite{good2020} \\label{a} \\ref{a}\n")
    r = run_script(SCRIPT, str(main), "--bib", str(bib), "--pattern", "no-equals-sign")
    assert r.returncode == 2
    r = run_script(SCRIPT, str(main), "--bib", str(bib), "--pattern", "tok=([bad")
    assert r.returncode == 2
