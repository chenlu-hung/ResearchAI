import json

SCRIPT = "skills/literature-explorer/scripts/dedupe_rank.py"


def _write_jsonl(path, records):
    path.write_text("\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8")


def test_merges_across_sources_and_ranks(tmp_path, run_script):
    _write_jsonl(
        tmp_path / "theorist.jsonl",
        [
            {
                "source": "arxiv",
                "id": "1904.06019v2",
                "title": "Conformal Prediction Under Covariate Shift",
                "authors": ["Ryan J. Tibshirani", "Rina Foygel Barber"],
                "year": "2019",
                "abstract": "short",
                "url": "https://arxiv.org/abs/1904.06019",
            },
            {
                "source": "openalex",
                "id": "W1",
                "title": "An Ancient Obscure Method",
                "authors": ["A. Nobody"],
                "year": "1998",
                "citation_count": 2,
                "url": "https://openalex.org/W1",
            },
        ],
    )
    _write_jsonl(
        tmp_path / "critic.jsonl",
        [
            {
                "source": "semantic_scholar",
                "id": "s2id",
                "external_ids": {"ArXiv": "1904.06019"},
                "title": "Conformal prediction under covariate shift.",
                "authors": ["R. Tibshirani"],
                "year": "2019",
                "citation_count": 900,
                "venue": "NeurIPS",
                "abstract": "a much longer abstract text here",
                "url": "https://semanticscholar.org/paper/s2id",
            }
        ],
    )
    out = tmp_path / "ranked.jsonl"
    md = tmp_path / "ranked.md"
    r = run_script(
        SCRIPT,
        str(tmp_path / "theorist.jsonl"),
        str(tmp_path / "critic.jsonl"),
        "--out", str(out), "--md", str(md),
    )
    assert r.returncode == 0, r.stderr
    rows = [json.loads(line) for line in out.read_text().splitlines()]
    assert len(rows) == 2
    top = rows[0]
    assert top["rank"] == 1
    assert top["citation_count"] == 900
    assert top["arxiv_id"] == "1904.06019"
    assert top["perspectives"] == ["critic", "theorist"]
    assert set(top["sources"]) == {"arxiv", "semantic_scholar"}
    assert top["url"] == "https://arxiv.org/abs/1904.06019"  # arxiv url preferred
    assert top["abstract"].startswith("a much longer")
    assert "merged 3 records -> 2 unique papers" in r.stderr
    assert "| 1 |" in md.read_text()


def test_same_title_far_apart_years_not_merged(tmp_path, run_script):
    _write_jsonl(
        tmp_path / "q.jsonl",
        [
            {"source": "openalex", "id": "W2", "title": "On Estimation",
             "authors": ["J. Smith"], "year": "1995", "citation_count": 10},
            {"source": "openalex", "id": "W3", "title": "On Estimation",
             "authors": ["J. Smith"], "year": "2024", "citation_count": 5},
        ],
    )
    r = run_script(SCRIPT, str(tmp_path / "q.jsonl"))
    assert r.returncode == 0, r.stderr
    rows = [json.loads(line) for line in r.stdout.splitlines() if line.strip()]
    assert len(rows) == 2


def test_top_limit_and_bad_lines_skipped(tmp_path, run_script):
    f = tmp_path / "x.jsonl"
    f.write_text(
        json.dumps({"source": "arxiv", "id": "1", "title": "A", "authors": ["X Y"],
                    "year": "2024"})
        + "\nnot json\n"
        + json.dumps({"error": "rate limited"})
        + "\n"
        + json.dumps({"source": "arxiv", "id": "2", "title": "B", "authors": ["Z W"],
                      "year": "2024"})
        + "\n",
        encoding="utf-8",
    )
    r = run_script(SCRIPT, str(f), "--top", "1")
    assert r.returncode == 0
    rows = [json.loads(line) for line in r.stdout.splitlines() if line.strip()]
    assert len(rows) == 1
    assert "bad JSON" in r.stderr
