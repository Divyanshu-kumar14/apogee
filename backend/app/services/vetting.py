"""
ML-Based Transit Vetting Service
Uses Random Forest classifier to distinguish real transits from false positives.
"""
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import numpy as np
from typing import Dict, Optional, Tuple
import pickle
import os
import logging

logger = logging.getLogger(__name__)

# Model storage directory
MODEL_DIR = os.path.join(os.path.dirname(__file__), "../../../models")
os.makedirs(MODEL_DIR, exist_ok=True)

class TransitVettingClassifier:
    """
    Random Forest classifier for transit candidate vetting.
    
    Distinguishes between:
    - Real planetary transits
    - Eclipsing binaries
    - Instrumental artifacts
    - Stellar variability false positives
    """
    
    def __init__(self):
        """Initialize transit vetting classifier."""
        self.model: Optional[RandomForestClassifier] = None
        self.scaler: Optional[StandardScaler] = None
        self.feature_names = [
            "bls_power",
            "bls_snr",
            "period",
            "depth",
            "duration",
            "flux_std",
            "flux_mad",
            "flux_skew",
            "flux_kurtosis",
            "transit_depth_ratio",
            "duration_ratio",
            "secondary_depth",
            "odd_even_diff"
        ]
        self.is_trained = False
        
        # Try to load pre-trained model
        self._load_model()
        
        # If no model exists, train on synthetic data
        if not self.is_trained:
            logger.info("No pre-trained model found. Training on synthetic data...")
            self._train_on_synthetic_data()
    
    def _load_model(self) -> bool:
        """
        Load pre-trained model from disk.
        
        Returns:
            True if model loaded successfully, False otherwise
        """
        model_path = os.path.join(MODEL_DIR, "transit_vetting_rf.pkl")
        scaler_path = os.path.join(MODEL_DIR, "transit_vetting_scaler.pkl")
        
        if os.path.exists(model_path) and os.path.exists(scaler_path):
            try:
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                self.is_trained = True
                logger.info("Pre-trained model loaded successfully")
                return True
            except Exception as e:
                logger.error(f"Error loading model: {e}")
                return False
        
        return False
    
    def _save_model(self):
        """Save trained model to disk."""
        model_path = os.path.join(MODEL_DIR, "transit_vetting_rf.pkl")
        scaler_path = os.path.join(MODEL_DIR, "transit_vetting_scaler.pkl")
        
        try:
            with open(model_path, 'wb') as f:
                pickle.dump(self.model, f)
            with open(scaler_path, 'wb') as f:
                pickle.dump(self.scaler, f)
            logger.info("Model saved successfully")
        except Exception as e:
            logger.error(f"Error saving model: {e}")
    
    def _train_on_synthetic_data(self):
        """
        Train classifier on synthetic training data.
        In production, this would use labeled TESS data.
        """
        logger.info("Generating synthetic training data...")
        
        # Generate 1000 synthetic examples
        n_samples = 1000
        X_train = []
        y_train = []
        
        for i in range(n_samples):
            # 40% real transits, 60% false positives
            is_real_transit = np.random.random() < 0.4
            
            if is_real_transit:
                # Real planetary transit characteristics
                features = self._generate_real_transit_features()
                label = 1
            else:
                # False positive characteristics
                features = self._generate_false_positive_features()
                label = 0
            
            X_train.append([features[name] for name in self.feature_names])
            y_train.append(label)
        
        X_train = np.array(X_train)
        y_train = np.array(y_train)
        
        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        
        # Train Random Forest
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            class_weight='balanced'
        )
        
        self.model.fit(X_train_scaled, y_train)
        self.is_trained = True
        
        # Save model
        self._save_model()
        
        # Log training accuracy
        train_accuracy = self.model.score(X_train_scaled, y_train)
        logger.info(f"Model trained. Training accuracy: {train_accuracy:.3f}")
    
    def _generate_real_transit_features(self) -> Dict:
        """Generate features for a real planetary transit."""
        return {
            "bls_power": np.random.uniform(0.15, 0.4),  # Strong signal
            "bls_snr": np.random.uniform(8, 20),  # High SNR
            "period": np.random.uniform(1.5, 15),  # Typical planet period
            "depth": np.random.uniform(0.002, 0.02),  # 0.2-2% depth
            "duration": np.random.uniform(0.05, 0.15),  # 1-4 hours
            "flux_std": np.random.uniform(0.0005, 0.002),  # Low noise
            "flux_mad": np.random.uniform(0.0003, 0.0015),
            "flux_skew": np.random.uniform(-0.5, 0.5),  # Symmetric
            "flux_kurtosis": np.random.uniform(-0.5, 1.0),
            "transit_depth_ratio": np.random.uniform(5, 15),  # Deep relative to noise
            "duration_ratio": np.random.uniform(0.01, 0.05),  # Short relative to period
            "secondary_depth": np.random.uniform(0, 0.001),  # No/weak secondary
            "odd_even_diff": np.random.uniform(0, 0.002)  # Consistent transits
        }
    
    def _generate_false_positive_features(self) -> Dict:
        """Generate features for a false positive."""
        fp_type = np.random.choice(['eclipsing_binary', 'artifact', 'variability'])
        
        if fp_type == 'eclipsing_binary':
            # Eclipsing binary characteristics
            return {
                "bls_power": np.random.uniform(0.2, 0.5),  # Very strong
                "bls_snr": np.random.uniform(10, 30),  # Very high SNR
                "period": np.random.uniform(0.5, 10),
                "depth": np.random.uniform(0.05, 0.3),  # Deep eclipses
                "duration": np.random.uniform(0.1, 0.5),  # Longer duration
                "flux_std": np.random.uniform(0.001, 0.005),
                "flux_mad": np.random.uniform(0.0008, 0.004),
                "flux_skew": np.random.uniform(-1.5, 1.5),  # Asymmetric
                "flux_kurtosis": np.random.uniform(1.0, 5.0),  # High kurtosis
                "transit_depth_ratio": np.random.uniform(15, 50),  # Very deep
                "duration_ratio": np.random.uniform(0.05, 0.2),  # Long relative to period
                "secondary_depth": np.random.uniform(0.01, 0.1),  # Strong secondary
                "odd_even_diff": np.random.uniform(0.01, 0.05)  # Different depths
            }
        
        elif fp_type == 'artifact':
            # Instrumental artifact
            return {
                "bls_power": np.random.uniform(0.05, 0.15),  # Weak signal
                "bls_snr": np.random.uniform(3, 8),  # Low SNR
                "period": np.random.uniform(0.5, 30),  # Any period
                "depth": np.random.uniform(0.001, 0.01),
                "duration": np.random.uniform(0.01, 0.3),
                "flux_std": np.random.uniform(0.002, 0.01),  # High noise
                "flux_mad": np.random.uniform(0.0015, 0.008),
                "flux_skew": np.random.uniform(-2, 2),  # Very asymmetric
                "flux_kurtosis": np.random.uniform(2, 10),  # Very high kurtosis
                "transit_depth_ratio": np.random.uniform(1, 5),  # Shallow
                "duration_ratio": np.random.uniform(0.001, 0.1),
                "secondary_depth": np.random.uniform(0, 0.005),
                "odd_even_diff": np.random.uniform(0.005, 0.02)  # Inconsistent
            }
        
        else:  # variability
            # Stellar variability
            return {
                "bls_power": np.random.uniform(0.08, 0.2),  # Moderate signal
                "bls_snr": np.random.uniform(4, 10),
                "period": np.random.uniform(5, 30),  # Longer periods
                "depth": np.random.uniform(0.005, 0.05),
                "duration": np.random.uniform(0.2, 1.0),  # Very long
                "flux_std": np.random.uniform(0.003, 0.015),  # High variability
                "flux_mad": np.random.uniform(0.002, 0.01),
                "flux_skew": np.random.uniform(-1, 1),
                "flux_kurtosis": np.random.uniform(0, 3),
                "transit_depth_ratio": np.random.uniform(2, 8),
                "duration_ratio": np.random.uniform(0.1, 0.4),  # Very long
                "secondary_depth": np.random.uniform(0, 0.01),
                "odd_even_diff": np.random.uniform(0, 0.01)
            }
    
    def predict(self, features: Dict) -> Tuple[bool, float, str]:
        """
        Predict if a transit candidate is real or false positive.
        
        Args:
            features: Dictionary of extracted features
            
        Returns:
            Tuple of (is_planet, confidence, disposition)
        """
        if not self.is_trained:
            logger.error("Model not trained!")
            return False, 0.0, "ERROR"
        
        # Prepare feature vector
        X = np.array([[features[name] for name in self.feature_names]])
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Predict
        prediction = self.model.predict(X_scaled)[0]
        probabilities = self.model.predict_proba(X_scaled)[0]
        
        is_planet = bool(prediction == 1)
        confidence = float(probabilities[1] if is_planet else probabilities[0])
        
        # Determine disposition
        if is_planet:
            if confidence > 0.8:
                disposition = "CONFIRMED"
            elif confidence > 0.6:
                disposition = "CANDIDATE"
            else:
                disposition = "LIKELY"
        else:
            if confidence > 0.8:
                disposition = "FALSE_POSITIVE"
            elif confidence > 0.6:
                disposition = "LIKELY_FP"
            else:
                disposition = "UNCERTAIN"
        
        logger.info(f"Vetting result: is_planet={is_planet}, confidence={confidence:.3f}, disposition={disposition}")
        
        return is_planet, confidence, disposition
    
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Get feature importance scores from the trained model.
        
        Returns:
            Dictionary mapping feature names to importance scores
        """
        if not self.is_trained or self.model is None:
            return {}
        
        importances = self.model.feature_importances_
        return {
            name: float(importance) 
            for name, importance in zip(self.feature_names, importances)
        }


# Global classifier instance
_classifier: Optional[TransitVettingClassifier] = None

def get_vetting_classifier() -> TransitVettingClassifier:
    """
    Get or create global transit vetting classifier instance.
    
    Returns:
        TransitVettingClassifier instance
    """
    global _classifier
    if _classifier is None:
        _classifier = TransitVettingClassifier()
    return _classifier
