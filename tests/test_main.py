import os
import uuid
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

# It's important to set the environment variables before importing the app
os.environ['GCP_PROJECT_ID'] = 'test-project'
os.environ['IMAGE_GENERATION_MODEL'] = 'test-image-model'
os.environ['VIDEO_GENERATION_MODEL'] = 'test-video-model'

# Now, import the app
from app.main import app, TEMP_DIR

client = TestClient(app)

# Ensure the temporary directory exists for testing
os.makedirs(TEMP_DIR, exist_ok=True)


def test_health_check():
    """
    Tests the /health endpoint.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@patch('uuid.uuid4')
@patch('app.main.ImageGenerationModel.from_pretrained')
def test_generate_image_success(mock_from_pretrained, mock_uuid):
    """
    Tests the /generate/image endpoint with a mocked Vertex AI call.
    This test now creates a dummy file to avoid FileNotFoundError.
    """
    # Arrange: Set up the mocks
    mock_image = MagicMock()
    # The image.save() method doesn't need to do anything in the mock
    mock_image.save.return_value = None

    mock_model_instance = MagicMock()
    mock_model_instance.generate_images.return_value = [mock_image]
    mock_from_pretrained.return_value = mock_model_instance

    # Arrange: Mock UUID to have a predictable filename
    test_uuid = "1234-5678"
    mock_uuid.return_value = test_uuid
    expected_filename = f"img_{test_uuid}.png"
    expected_filepath = os.path.join(TEMP_DIR, expected_filename)

    # Arrange: Create a dummy file that the FileResponse can find
    with open(expected_filepath, "w") as f:
        f.write("dummy image content")

    # Act: Call the endpoint
    try:
        response = client.post("/generate/image", json={"prompt": "a test prompt"})

        # Assert: Check the results
        assert response.status_code == 200
        assert response.headers['content-type'] == 'image/png'
        assert response.content == b"dummy image content"
        mock_from_pretrained.assert_called_with('test-image-model')
        mock_model_instance.generate_images.assert_called_with(prompt="a test prompt", number_of_images=1)
        mock_image.save.assert_called_with(location=expected_filepath)
    finally:
        # Clean up the dummy file
        if os.path.exists(expected_filepath):
            os.remove(expected_filepath)


@patch('uuid.uuid4')
def test_generate_video_placeholder(mock_uuid):
    """
    Tests the placeholder /generate/video endpoint.
    This test now checks for 'content-type' and creates a dummy file.
    """
    # Arrange: Mock UUID for a predictable filename
    test_uuid = "video-1234"
    mock_uuid.return_value = test_uuid
    expected_filename = f"vid_{test_uuid}.mp4"
    expected_filepath = os.path.join(TEMP_DIR, expected_filename)

    # Act: Call the endpoint
    try:
        response = client.post("/generate/video", json={"prompt": "a test video prompt"})

        # Assert
        assert response.status_code == 200
        assert response.headers['content-type'] == 'video/mp4'
        # The app should have created this file
        assert os.path.exists(expected_filepath)
    finally:
        # Clean up the file created by the app
        if os.path.exists(expected_filepath):
            os.remove(expected_filepath)


@patch('app.main.ImageGenerationModel.from_pretrained')
def test_generate_image_handles_exception(mock_from_pretrained):
    """
    Tests that the /generate/image endpoint handles exceptions from the AI model gracefully.
    """
    # Arrange: Configure the mock to raise an exception
    mock_from_pretrained.side_effect = Exception("Vertex AI is unavailable")

    # Act: Call the endpoint
    response = client.post("/generate/image", json={"prompt": "a prompt that will fail"})

    # Assert: Check that the response is a 500 Internal Server Error
    assert response.status_code == 500
    assert "Vertex AI is unavailable" in response.json()['detail']
