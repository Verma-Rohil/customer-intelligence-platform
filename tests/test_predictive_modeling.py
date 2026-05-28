import unittest
import pandas as pd
import numpy as np
from src.models.label_generation import generate_churn_labels
from src.models.autoencoder import train_autoencoder
from src.models.churn_prediction import train_xgboost_model

class TestPredictiveModeling(unittest.TestCase):
    def setUp(self):
        # Create a mock feature matrix
        self.mock_data = pd.DataFrame({
            'customer_id': range(100),
            'recency_days': np.random.randint(1, 100, 100),
            'frequency_total': np.random.randint(1, 50, 100),
            'monetary_value_total': np.random.lognormal(mean=5, sigma=1, size=100),
            'avg_order_value': np.random.lognormal(mean=3, sigma=0.5, size=100),
            'spend_last_30d': np.random.randint(0, 500, 100)
        })
        
    def test_label_generation(self):
        """Test that churn labels are correctly generated based on 60-day threshold."""
        result_df = generate_churn_labels(self.mock_data, churn_threshold_days=60)
        
        self.assertIn('is_churned', result_df.columns)
        
        # Verify logic
        churned_samples = result_df[result_df['recency_days'] > 60]
        active_samples = result_df[result_df['recency_days'] <= 60]
        
        self.assertTrue((churned_samples['is_churned'] == 1).all())
        self.assertTrue((active_samples['is_churned'] == 0).all())
        
    def test_xgboost_pipeline_execution(self):
        """Test that XGBoost model trains without crashing."""
        # Setup labels first
        df = generate_churn_labels(self.mock_data, churn_threshold_days=60)
        
        # Train model
        model, metrics, features = train_xgboost_model(df)
        
        # Verify model object is created
        self.assertIsNotNone(model)
        # Verify metrics exist
        self.assertIn('roc_auc', metrics)
        self.assertIn('recall', metrics)
        self.assertIn('f1', metrics)
        
    def test_autoencoder_execution(self):
        """Test that PyTorch autoencoder trains without crashing and returns anomaly scores."""
        df = generate_churn_labels(self.mock_data, churn_threshold_days=60)
        
        result_df = train_autoencoder(df, epochs=2, batch_size=16) # low epochs for quick test
        
        self.assertIn('anomaly_score', result_df.columns)
        self.assertFalse(np.isnan(result_df['anomaly_score']).any())

if __name__ == '__main__':
    unittest.main()
