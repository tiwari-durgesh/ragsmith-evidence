"""UI and API use one contract and redacted error path on synthetic inputs."""

import copy
import logging

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.checked_service import InputError, checked_answer
from app.contracts import AskRequest, AskResponse
from app.frontend.view import run_lookup
from app.main import app
from tests.test_demo_api import request


def test_api_and_frontend_share_complete_response_contract():
    payload = request()
    ui = run_lookup(payload)
    api = TestClient(app).post('/ask', json=payload)
    assert api.status_code == 200, api.text
    assert AskResponse.model_validate(api.json()) == AskResponse.model_validate(ui)
    schema = TestClient(app).get('/openapi.json').json()
    assert schema['paths']['/ask']['post']['responses']['200']['content']['application/json']['schema']['$ref'].endswith('/AskResponse')


@pytest.mark.parametrize('change', ['dangling', 'duplicate', 'abstain_values', 'budget'])
def test_response_contract_rejects_broken_links_or_unbounded_tokens(change):
    data = copy.deepcopy(run_lookup(request()))
    if change == 'dangling':
        data['values'][0]['citation_numbers'] = [999]
    elif change == 'duplicate':
        data['citations'].append(data['citations'][0])
    elif change == 'abstain_values':
        data['decision'] = 'abstain'
    else:
        data['packing']['input_tokens'] = 3201
    with pytest.raises(ValidationError):
        AskResponse.model_validate(data)


def test_ragged_table_rejected_in_both_transports_without_logging_contents(caplog):
    payload = request([['Metric', '2025'], ['DO-NOT-LOG-MY-CONTENT']])
    with caplog.at_level(logging.WARNING):
        response = TestClient(app).post('/ask', json=payload)
        with pytest.raises(InputError, match='rectangular'):
            run_lookup(payload)
    assert response.status_code == 422 and 'Header repair is unsupported' in response.text
    assert 'malformed_table' in caplog.text and 'DO-NOT-LOG' not in caplog.text


def test_request_only_overflow_is_clear_and_content_free(caplog):
    payload = AskRequest.model_validate(request() | {'question': 'CONFIDENTIAL ' * 300})
    with caplog.at_level(logging.WARNING), pytest.raises(InputError, match='3,200') as err:
        checked_answer(payload)
    assert err.value.code == 'input_budget_exceeded'
    assert 'input_budget_exceeded' in caplog.text and 'CONFIDENTIAL' not in caplog.text


def test_truncation_remains_visible_in_ui_and_api_contract(caplog):
    payload = request([['Metric', '2025']] + [['Revenue', str(x)] for x in range(20)])
    with caplog.at_level(logging.WARNING):
        result = run_lookup(payload)
    assert result['packing']['truncated']
    assert result['packing']['input_tokens'] <= 3200
    assert 'evidence_truncated' in caplog.text


def test_bad_internal_response_fails_closed(monkeypatch):
    import app.checked_service as service
    monkeypatch.setattr(service, 'answer', lambda *args: {'decision': 'full'})
    with pytest.raises(RuntimeError, match='shared transport contract'):
        checked_answer(AskRequest.model_validate(request()))
