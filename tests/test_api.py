import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_answer_question():
    response = client.post(
        "/api/",
        json={"question": "Should I use gpt4o-mini or gpt3.5?"}
    )
    assert response.status_code == 200
    assert "answer" in response.json()
    assert "links" in response.json()

def test_answer_question_with_image():
    # Base64 encoded test image
    test_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
    response = client.post(
        "/api/",
        json={
            "question": "What does this image show?",
            "image": test_image
        }
    )
    assert response.status_code == 200
    assert "answer" in response.json()
    assert "links" in response.json() 