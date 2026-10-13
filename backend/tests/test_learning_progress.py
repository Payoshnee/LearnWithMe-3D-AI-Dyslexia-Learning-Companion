from app.api.progress import ProgressData
from app.main import app
from app.services.lesson_service import advance_lesson
from fastapi.testclient import TestClient
from uuid import uuid4


def test_ipa_slashes_are_ignored_for_phoneme_answers():
    result = advance_lesson("cat", 1, " /K/ ")
    assert result["correct"] is True
    assert result["step"] == 2


def test_progress_defaults_never_include_negative_rewards():
    progress = ProgressData()
    assert progress.stars == 0
    assert progress.level == 1
    assert progress.wordsLearned == []


def test_authenticated_lesson_and_progress_flow():
    with TestClient(app) as client:
        email = f"learner-{uuid4().hex}@example.com"
        registered = client.post('/api/auth/register', json={
            'name': 'Test Learner', 'email': email, 'password': 'kind-test-password'
        })
        assert registered.status_code == 201
        assert client.get('/api/auth/session').status_code == 200
        step = client.post('/api/learning/answer', json={
            'lesson_id': 'cat', 'step': 1, 'response': '/k/'
        })
        assert step.status_code == 200
        assert step.json()['step'] == 2
        payload = {
            'stars': 2, 'completedLessons': ['cat'],
            'completedGames': ['trace-level-1'], 'level': 1,
            'wordsLearned': ['cat'], 'letterMastery': {'c': 1}
        }
        assert client.put('/api/progress', json=payload).json() == payload
        assert client.get('/api/progress').json() == payload
        client.post('/api/auth/logout')
        assert client.get('/api/progress').status_code == 401
