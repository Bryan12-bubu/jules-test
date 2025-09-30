import os
import uuid
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

# Import the app
from app.main import app

client = TestClient(app)

def test_health_check():
    """Tests the /health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@patch('uuid.uuid4')
@patch('app.main.ImageGenerationModel.from_pretrained')
def test_generate_image_success(mock_from_pretrained, mock_uuid, tmp_path, monkeypatch):
    """
    Tests the /generate/image endpoint with a mocked Vertex AI call.
    The mock 'save' method now creates a dummy file to be found by FileResponse.
    """
    # Arrange: Use monkeypatch to set the TEMP_DIR for this test only
    monkeypatch.setattr('app.main.TEMP_DIR', str(tmp_path))

    # This function will be the replacement for the real 'save' method
    def mock_save_method(location):
        with open(location, "w") as f:
            f.write("dummy image")

    # Arrange: Set up the model mocks
    mock_image = MagicMock()
    mock_image.save.side_effect = mock_save_method

    mock_model_instance = MagicMock()
    mock_model_instance.generate_images.return_value = [mock_image]
    mock_from_pretrained.return_value = mock_model_instance

    # Act: Call the endpoint
    response = client.post("/generate/image", json={"prompt": "a test prompt"})

    # Assert: Check the results
    assert response.status_code == 200
    assert response.headers['content-type'] == 'image/png'
    assert response.content == b"dummy image"
    mock_from_pretrained.assert_called_with("test-image-model-from-config")
    mock_model_instance.generate_images.assert_called_with(prompt="a test prompt", number_of_images=1)
    mock_image.save.assert_called_once()


def test_generate_video_placeholder(tmp_path, monkeypatch):
    """
    Tests the placeholder /generate/video endpoint.
    The placeholder now successfully creates a file, so we expect a 200 OK.
    """
    # Arrange: Use monkeypatch to set the TEMP_DIR for this test only
    monkeypatch.setattr('app.main.TEMP_DIR', str(tmp_path))

    # Act
    response = client.post("/generate/video", json={"prompt": "a test video prompt"})

    # Assert
    assert response.status_code == 200
    assert response.headers['content-type'] == 'video/mp4'


@patch('app.main.ImageGenerationModel.from_pretrained')
def test_generate_image_handles_exception(mock_from_pretrained, monkeypatch, tmp_path):
    """
    Tests that the /generate/image endpoint handles exceptions from the AI model gracefully.
    """
    # Arrange
    monkeypatch.setattr('app.main.TEMP_DIR', str(tmp_path))
    mock_from_pretrained.side_effect = Exception("Vertex AI is unavailable")

    # Act
    response = client.post("/generate/image", json={"prompt": "a prompt that will fail"})

    # Assert
    assert response.status_code == 500
    assert "Vertex AI is unavailable" in response.json()['detail']
