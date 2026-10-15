import unittest
from fastapi.testclient import TestClient

from app.main import app
from app.services.prediction_service import get_model


class TestHousePricePredictionAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        get_model()
        cls.client = TestClient(app)

    def test_home_endpoint(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)
        self.assertEqual(data["status"], "online")

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertTrue(data["model_loaded"])

    def test_predict_success(self):
        payload = {
            "MedInc": 5.0,
            "HouseAge": 25.0,
            "AveRooms": 6.0,
            "AveBedrms": 1.0,
            "Population": 1200.0,
            "AveOccup": 3.0,
            "Latitude": 34.05,
            "Longitude": -118.25,
        }
        response = self.client.post("/predict/", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("predicted_value", data)
        self.assertIn("estimated_price_usd", data)
        self.assertGreater(data["estimated_price_usd"], 0)
        self.assertIsNotNone(data["prediction_id"])

    def test_predict_validation_error(self):
        # Invalid payload: negative rooms and out-of-bounds latitude
        payload = {
            "MedInc": -1.0,  # Must be > 0
            "HouseAge": 25.0,
            "AveRooms": -5.0,  # Must be > 0.5
            "AveBedrms": 1.0,
            "Population": 1200.0,
            "AveOccup": 3.0,
            "Latitude": 95.0,  # Invalid latitude
            "Longitude": -118.25,
        }
        response = self.client.post("/predict/", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_prediction_history(self):
        response = self.client.get("/predict/history?limit=10")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("total", data)
        self.assertIn("items", data)
        self.assertIsInstance(data["items"], list)
        self.assertGreaterEqual(data["total"], 1)

    def test_get_prediction_by_id_not_found(self):
        response = self.client.get("/predict/999999999")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
