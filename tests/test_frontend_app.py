"""Streamlit interaction tests on six synthetic fixtures, not private pilot files."""

import copy
import json
from pathlib import Path

import pytest

from app.frontend import view
from streamlit.testing.v1 import AppTest


APP = Path(__file__).resolve().parents[1] / "app/frontend/streamlit_app.py"


@pytest.fixture
def ui(monkeypatch):
    facts = [{"requirement_id": "r", "metric": "Revenue", "year": 2025},
             {"requirement_id": "c", "metric": "Cash", "year": 2025}]
    tables = [
        [["Metric", "2025"], ["Revenue", "10"], ["Cash", "4"]],
        [["Metric", "2025"], ["Revenue", "20"], ["Cash", "8"]],
        [["Metric", "2025"], ["Revenue", "10"]],
        [["Metric", "2025"], ["Cash", "4"]],
        [["Metric", "2025"], ["Revenue", "10"], ["Revenue", "20"], ["Cash", "4"]],
        [["Metric", "2025"]],
    ]
    categories = ["full", "full", "partial", "partial", "controlled_conflict", "abstain"]
    packet = {"cases": [{"sample_id": f"synthetic-{i}", "demo_category": category,
        "request": {"question": "Give synthetic Revenue and Cash in 2025.", "requested_facts": facts,
                    "table": table, "source_unit": "USD", "answerer": "lookup"}}
        for i, (category, table) in enumerate(zip(categories, tables))]}
    monkeypatch.setattr(view, "load_samples", lambda: copy.deepcopy(packet))
    return AppTest.from_file(str(APP), default_timeout=20).run()


def test_initial_view_has_six_options_banner_and_no_auto_inference(ui):
    assert not ui.exception
    assert len(ui.selectbox[0].options) == 6
    assert any(view.BANNER == item.value for item in ui.warning)
    assert "pilot_result" not in ui.session_state
    assert [t.label for t in ui.tabs] == ["Prepared pilot cases", "Paste your own table", "Limitations"]


@pytest.mark.parametrize("index,decision", [(0, "full"), (1, "full"), (2, "partial"), (3, "partial"), (4, "abstain"), (5, "abstain")])
def test_six_interactions_render_decision_cells_and_baselines(ui, index, decision):
    ui.selectbox[0].select_index(index).run()
    ui.button(key="run_pilot").click().run()
    assert not ui.exception
    assert ui.session_state["pilot_result"]["result"]["decision"] == decision
    assert any(f'<strong>{decision.upper()}</strong>' in m.value for m in ui.markdown)
    assert any("Three-baseline comparison" == s.value for s in ui.subheader)
    assert any("#### Extraction-only" == m.value for m in ui.markdown)
    assert any("#### Binary" == m.value for m in ui.markdown)
    assert any("#### Graded" == m.value for m in ui.markdown)
    if decision != "abstain":
        assert any('class="verified-cell"' in m.value for m in ui.markdown)
        assert any('href="#pilot-cell-' in m.value for m in ui.markdown)
    if index == 4:
        assert any("Controlled test case" in item.value for item in ui.info)


def test_switching_case_hides_stale_result_and_highlights(ui):
    ui.button(key="run_pilot").click().run()
    ui.selectbox[0].select_index(2).run()
    assert not ui.exception
    assert not any(s.value == "Result" for s in ui.subheader)
    assert not any('class="verified-cell"' in m.value for m in ui.markdown)


def test_paste_error_is_plain_message_not_traceback(ui):
    ui.text_area(key="custom_table").set_value("{broken").run()
    ui.button(key="run_custom").click().run()
    assert not ui.exception
    assert any("Cannot parse table" in e.value and "Header repair is unsupported" in e.value for e in ui.error)
    assert "custom_result" not in ui.session_state


def test_custom_changes_hide_stale_results(ui):
    ui.button(key="run_custom").click().run()
    assert ui.session_state["custom_result"]["result"]["decision"] == "full"
    ui.text_area(key="custom_table").set_value("{broken").run()
    assert not ui.exception
    assert not any(s.value == "Result" for s in ui.subheader)


def test_missing_samples_still_allows_custom_and_limitations(monkeypatch):
    def missing():
        raise FileNotFoundError("not prepared")
    monkeypatch.setattr(view, "load_samples", missing)
    ui = AppTest.from_file(str(APP), default_timeout=20).run()
    assert not ui.exception
    assert any("six local pilot samples are unavailable" in e.value for e in ui.error)
    ui.button(key="run_custom").click().run()
    assert ui.session_state["custom_result"]["result"]["decision"] == "full"
