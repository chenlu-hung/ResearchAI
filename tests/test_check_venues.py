import datetime as dt
import json

SCRIPT = "skills/paper-writer/scripts/check_venues.py"

TODAY = dt.date.today().isoformat()

PROFILES_TMPL = """# Venue Profiles

## TestConf

- **Reviewer profile**: balanced.

## Generic (used by `peer-reviewer`)

- Fallback persona.

---

## Defaults by venue (consumed by paper-writer)

```yaml
testconf:
  as_of: {as_of}
  sources:
    - https://testconf.org/cfp
  page_limit: 8
  bib_style: numeric
  must_include: [limitations, {extra_token}]
{patterns_block}{observed_block}  unverified: {unverified}
```
"""


def _setup(tmp_path, as_of=TODAY, extra_token="reproducibility",
           patterns=None, style=True, observed=None,
           unverified="[page_limit]"):
    tmp_path.mkdir(exist_ok=True)
    patterns_block = ""
    if patterns:
        entries = "".join(f"    {k}: '{v}'\n" for k, v in patterns.items())
        patterns_block = "  must_include_patterns:\n" + entries
    observed_block = ""
    for key in ("fields", "sample"):
        if observed and key in observed:
            observed_block += f"  observed_{key}: [{', '.join(observed[key])}]\n"
    profiles = tmp_path / "venue_profiles.md"
    profiles.write_text(
        PROFILES_TMPL.format(as_of=as_of, extra_token=extra_token,
                             patterns_block=patterns_block,
                             observed_block=observed_block,
                             unverified=unverified),
        encoding="utf-8",
    )
    style_dir = tmp_path / "style"
    style_dir.mkdir()
    if style:
        (style_dir / "testconf.md").write_text("# Style: TestConf\n", encoding="utf-8")
    return profiles, style_dir


def _run(run_script, profiles, style_dir, *extra):
    return run_script(SCRIPT, "--profiles", str(profiles),
                      "--style-dir", str(style_dir), "--json", *extra)


def test_consistent_profile_passes(tmp_path, run_script):
    profiles, style_dir = _setup(tmp_path)
    r = _run(run_script, profiles, style_dir)
    assert r.returncode == 0, r.stdout + r.stderr
    data = json.loads(r.stdout)
    assert data["venues_checked"] == ["testconf"]
    assert data["blocking"] == []


def test_unknown_token_without_pattern_blocks(tmp_path, run_script):
    # the AoS `proofs` bug class: token in must_include, no regex anywhere
    profiles, style_dir = _setup(tmp_path, extra_token="proofs")
    r = _run(run_script, profiles, style_dir)
    assert r.returncode == 1
    assert any("proofs" in b for b in json.loads(r.stdout)["blocking"])


def test_venue_pattern_resolves_custom_token(tmp_path, run_script):
    profiles, style_dir = _setup(
        tmp_path, extra_token="data_availability",
        patterns={"data_availability": "data\\s+availab"})
    r = _run(run_script, profiles, style_dir)
    assert r.returncode == 0, r.stdout + r.stderr


def test_missing_style_file_blocks(tmp_path, run_script):
    profiles, style_dir = _setup(tmp_path, style=False)
    r = _run(run_script, profiles, style_dir)
    assert r.returncode == 1
    assert any("style file missing" in b for b in json.loads(r.stdout)["blocking"])


def test_missing_as_of_blocks_and_stale_warns(tmp_path, run_script):
    profiles, style_dir = _setup(tmp_path, as_of="not-a-date")
    r = _run(run_script, profiles, style_dir)
    assert r.returncode == 1

    profiles, style_dir2 = _setup(tmp_path / "sub", as_of="2020-01-01")
    r = _run(run_script, profiles, style_dir2)
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert any("re-verify" in w for w in data["warnings"])


def test_observed_valid_pair_passes(tmp_path, run_script):
    profiles, style_dir = _setup(
        tmp_path, unverified="[page_limit, bib_style]",
        observed={"fields": ["bib_style"], "sample": ["arxiv:2501.01234"]})
    r = _run(run_script, profiles, style_dir)
    assert r.returncode == 0, r.stdout + r.stderr


def test_observed_field_must_stay_unverified(tmp_path, run_script):
    # sample evidence never verifies a field — bib_style not in unverified
    profiles, style_dir = _setup(
        tmp_path,
        observed={"fields": ["bib_style"], "sample": ["arxiv:2501.01234"]})
    r = _run(run_script, profiles, style_dir)
    assert r.returncode == 1
    assert any("missing from unverified" in b
               for b in json.loads(r.stdout)["blocking"])


def test_observed_policy_field_blocks(tmp_path, run_script):
    # camera-ready page count is not evidence for the submission limit
    profiles, style_dir = _setup(
        tmp_path,
        observed={"fields": ["page_limit"], "sample": ["arxiv:2501.01234"]})
    r = _run(run_script, profiles, style_dir)
    assert r.returncode == 1
    assert any("cannot rest on exemplars" in b
               for b in json.loads(r.stdout)["blocking"])


def test_observed_fields_without_sample_blocks(tmp_path, run_script):
    profiles, style_dir = _setup(
        tmp_path, unverified="[page_limit, bib_style]",
        observed={"fields": ["bib_style"]})
    r = _run(run_script, profiles, style_dir)
    assert r.returncode == 1
    assert any("observed_sample" in b for b in json.loads(r.stdout)["blocking"])


def test_repo_venue_knowledge_is_consistent(run_script):
    """Integration guard: the repo's real venue files must not drift."""
    r = run_script(SCRIPT)
    assert r.returncode == 0, r.stdout + r.stderr
    data_line = [ln for ln in r.stdout.splitlines() if ln.startswith("RESULT:")]
    assert data_line and "clean" in data_line[0]
