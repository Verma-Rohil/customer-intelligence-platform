import unittest
import pandas as pd
import numpy as np
from src.data_processing import sanitize_transaction_data

class TestFeatureEngineering(unittest.TestCase):
    def setUp(self):
        # Build simulated transactional data
        self.raw_data = pd.DataFrame({
            'customer_id': ['C001', 'C001', 'C002'],
            'quantity': [2, -1, 5],
            'unit_price': [100.0, 50.0, 10.0],
            'discount_applied': [0.0, 10.0, 5.0]
        })

    def test_sanitize_transaction_data(self):
        # Runs sanitization engine
        clean_df = sanitize_transaction_data(self.raw_data)
        
        # Verify negative quantity row was dropped
        self.assertEqual(len(clean_df), 2)
        
        # Verify custom total_amount calculations
        # Row 1: 2 * 100 - 0 = 200
        # Row 3: 5 * 10 - 5 = 45
        total_amounts = clean_df['total_amount'].tolist()
        self.assertIn(200.0, total_amounts)
        self.assertIn(45.0, total_amounts)

if __name__ == '__main__':
    unittest.main()
