import unittest
import pandas as pd
import numpy as np
from src.clustering.rfm_scoring import apply_rfm_scoring
from src.clustering.kmeans_baseline import preprocess_features

class TestClustering(unittest.TestCase):
    def setUp(self):
        # Create a mock feature matrix
        self.mock_data = pd.DataFrame({
            'customer_id': [1, 2, 3, 4, 5],
            'recency_days': [5, 10, 50, 100, 300],
            'frequency_total': [50, 40, 20, 5, 1],
            'monetary_value_total': [1000, 800, 300, 50, 10],
            'avg_order_value': [20, 20, 15, 10, 10],
            'spend_last_30d': [500, 400, 0, 0, 0]
        })
        
    def test_apply_rfm_scoring(self):
        """Test that RFM scoring assigns correct segments based on quantiles."""
        result_df = apply_rfm_scoring(self.mock_data)
        
        self.assertIn('rfm_segment', result_df.columns)
        self.assertIn('rfm_score_concat', result_df.columns)
        
        # Ensure we have some valid labels
        valid_segments = ['Champions', 'Loyal Customers', 'At Risk', 'New Customers', 'Lost', 'Regular']
        for segment in result_df['rfm_segment']:
            self.assertIn(segment, valid_segments)
            
        # Top customer should be Champion
        self.assertEqual(result_df.loc[0, 'rfm_segment'], 'Champions')
        
    def test_preprocess_features(self):
        """Test that missing values are imputed and scaling is applied."""
        # Inject NaN
        self.mock_data.loc[0, 'avg_order_value'] = np.nan
        
        X_scaled, features = preprocess_features(self.mock_data, is_training=True)
        
        self.assertEqual(X_scaled.shape[0], 5)
        # 5 numeric features excluding customer_id
        self.assertEqual(X_scaled.shape[1], 5) 
        
        # Check no NaNs
        self.assertFalse(np.isnan(X_scaled).any())

if __name__ == '__main__':
    unittest.main()
