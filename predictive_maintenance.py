"""
Predictive Maintenance ML Models for Digital Twin Platform
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import joblib
import logging
from pathlib import Path

from sklearn.ensemble import IsolationForest, RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import classification_report, mean_squared_error, r2_score
from sklearn.cluster import DBSCAN
import xgboost as xgb
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class PredictionResult(BaseModel):
    """Prediction result model"""
    asset_id: str
    prediction_type: str  # 'anomaly', 'failure', 'health_score'
    prediction: float
    confidence: float
    timestamp: datetime
    features_used: List[str]
    model_version: str

class MaintenanceRecommendation(BaseModel):
    """Maintenance recommendation model"""
    asset_id: str
    priority: str  # 'low', 'medium', 'high', 'critical'
    action: str
    description: str
    estimated_cost: Optional[float] = None
    estimated_downtime: Optional[float] = None  # hours
    due_date: Optional[datetime] = None

class PredictiveMaintenanceModel:
    """Main predictive maintenance model class"""
    
    def __init__(self, model_path: str = "./ml/models/"):
        self.model_path = Path(model_path)
        self.model_path.mkdir(parents=True, exist_ok=True)
        
        # Models
        self.anomaly_detector = None
        self.failure_predictor = None
        self.health_scorer = None
        
        # Preprocessors
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        
        # Model metadata
        self.model_version = "1.0.0"
        self.last_trained = None
        self.feature_columns = [
            'temperature', 'humidity', 'pressure', 'vibration', 
            'power_consumption', 'operating_hours', 'age_days'
        ]
        
        logger.info("Predictive Maintenance Model initialized")
    
    def prepare_features(self, telemetry_data: pd.DataFrame) -> pd.DataFrame:
        """Prepare features from raw telemetry data"""
        try:
            df = telemetry_data.copy()
            
            # Convert timestamp to datetime if needed
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.sort_values('timestamp')
            
            # Calculate derived features
            df['hour_of_day'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            df['month'] = df['timestamp'].dt.month
            
            # Rolling statistics (if enough data)
            if len(df) > 10:
                for col in ['temperature', 'humidity', 'pressure', 'vibration', 'power_consumption']:
                    if col in df.columns:
                        df[f'{col}_rolling_mean'] = df[col].rolling(window=5, min_periods=1).mean()
                        df[f'{col}_rolling_std'] = df[col].rolling(window=5, min_periods=1).std()
                        df[f'{col}_diff'] = df[col].diff()
            
            # Operating hours (cumulative)
            df['operating_hours'] = range(len(df))
            
            # Age in days (from first record)
            if len(df) > 0:
                first_timestamp = df['timestamp'].min()
                df['age_days'] = (df['timestamp'] - first_timestamp).dt.total_seconds() / 86400
            
            # Fill missing values
            df = df.fillna(method='ffill').fillna(0)
            
            return df
            
        except Exception as e:
            logger.error(f"Error preparing features: {e}")
            raise
    
    def train_anomaly_detector(self, training_data: pd.DataFrame) -> Dict[str, Any]:
        """Train anomaly detection model"""
        try:
            logger.info("Training anomaly detection model")
            
            # Prepare features
            features_df = self.prepare_features(training_data)
            
            # Select feature columns that exist
            available_features = [col for col in self.feature_columns if col in features_df.columns]
            X = features_df[available_features]
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train Isolation Forest
            self.anomaly_detector = IsolationForest(
                contamination=0.1,  # Expect 10% anomalies
                random_state=42,
                n_estimators=100
            )
            
            self.anomaly_detector.fit(X_scaled)
            
            # Calculate anomaly scores for training data
            anomaly_scores = self.anomaly_detector.decision_function(X_scaled)
            predictions = self.anomaly_detector.predict(X_scaled)
            
            # Save model
            model_file = self.model_path / "anomaly_detector.joblib"
            joblib.dump({
                'model': self.anomaly_detector,
                'scaler': self.scaler,
                'features': available_features,
                'version': self.model_version
            }, model_file)
            
            self.last_trained = datetime.now()
            
            results = {
                'model_type': 'anomaly_detection',
                'training_samples': len(X),
                'features_used': available_features,
                'anomalies_detected': len(predictions[predictions == -1]),
                'anomaly_rate': len(predictions[predictions == -1]) / len(predictions),
                'model_file': str(model_file)
            }
            
            logger.info(f"Anomaly detection model trained: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Error training anomaly detector: {e}")
            raise
    
    def train_failure_predictor(self, training_data: pd.DataFrame, failure_labels: pd.Series) -> Dict[str, Any]:
        """Train failure prediction model"""
        try:
            logger.info("Training failure prediction model")
            
            # Prepare features
            features_df = self.prepare_features(training_data)
            
            # Select feature columns that exist
            available_features = [col for col in self.feature_columns if col in features_df.columns]
            X = features_df[available_features]
            y = failure_labels
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train XGBoost classifier
            self.failure_predictor = xgb.XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            )
            
            self.failure_predictor.fit(X_train_scaled, y_train)
            
            # Evaluate model
            train_score = self.failure_predictor.score(X_train_scaled, y_train)
            test_score = self.failure_predictor.score(X_test_scaled, y_test)
            
            # Predictions for detailed metrics
            y_pred = self.failure_predictor.predict(X_test_scaled)
            
            # Save model
            model_file = self.model_path / "failure_predictor.joblib"
            joblib.dump({
                'model': self.failure_predictor,
                'scaler': self.scaler,
                'features': available_features,
                'version': self.model_version
            }, model_file)
            
            results = {
                'model_type': 'failure_prediction',
                'training_samples': len(X_train),
                'test_samples': len(X_test),
                'features_used': available_features,
                'train_accuracy': train_score,
                'test_accuracy': test_score,
                'classification_report': classification_report(y_test, y_pred, output_dict=True),
                'model_file': str(model_file)
            }
            
            logger.info(f"Failure prediction model trained: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Error training failure predictor: {e}")
            raise
    
    def train_health_scorer(self, training_data: pd.DataFrame, health_scores: pd.Series) -> Dict[str, Any]:
        """Train health scoring model"""
        try:
            logger.info("Training health scoring model")
            
            # Prepare features
            features_df = self.prepare_features(training_data)
            
            # Select feature columns that exist
            available_features = [col for col in self.feature_columns if col in features_df.columns]
            X = features_df[available_features]
            y = health_scores
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train Random Forest regressor
            self.health_scorer = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            
            self.health_scorer.fit(X_train_scaled, y_train)
            
            # Evaluate model
            train_pred = self.health_scorer.predict(X_train_scaled)
            test_pred = self.health_scorer.predict(X_test_scaled)
            
            train_r2 = r2_score(y_train, train_pred)
            test_r2 = r2_score(y_test, test_pred)
            test_mse = mean_squared_error(y_test, test_pred)
            
            # Save model
            model_file = self.model_path / "health_scorer.joblib"
            joblib.dump({
                'model': self.health_scorer,
                'scaler': self.scaler,
                'features': available_features,
                'version': self.model_version
            }, model_file)
            
            results = {
                'model_type': 'health_scoring',
                'training_samples': len(X_train),
                'test_samples': len(X_test),
                'features_used': available_features,
                'train_r2': train_r2,
                'test_r2': test_r2,
                'test_mse': test_mse,
                'model_file': str(model_file)
            }
            
            logger.info(f"Health scoring model trained: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Error training health scorer: {e}")
            raise
    
    def load_models(self) -> bool:
        """Load trained models from disk"""
        try:
            # Load anomaly detector
            anomaly_file = self.model_path / "anomaly_detector.joblib"
            if anomaly_file.exists():
                anomaly_data = joblib.load(anomaly_file)
                self.anomaly_detector = anomaly_data['model']
                logger.info("Anomaly detector loaded")
            
            # Load failure predictor
            failure_file = self.model_path / "failure_predictor.joblib"
            if failure_file.exists():
                failure_data = joblib.load(failure_file)
                self.failure_predictor = failure_data['model']
                logger.info("Failure predictor loaded")
            
            # Load health scorer
            health_file = self.model_path / "health_scorer.joblib"
            if health_file.exists():
                health_data = joblib.load(health_file)
                self.health_scorer = health_data['model']
                logger.info("Health scorer loaded")
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            return False
    
    def predict_anomaly(self, telemetry_data: pd.DataFrame) -> List[PredictionResult]:
        """Predict anomalies in telemetry data"""
        try:
            if self.anomaly_detector is None:
                raise ValueError("Anomaly detector not trained or loaded")
            
            # Prepare features
            features_df = self.prepare_features(telemetry_data)
            available_features = [col for col in self.feature_columns if col in features_df.columns]
            X = features_df[available_features]
            
            # Scale features
            X_scaled = self.scaler.transform(X)
            
            # Predict
            predictions = self.anomaly_detector.predict(X_scaled)
            scores = self.anomaly_detector.decision_function(X_scaled)
            
            results = []
            for i, (pred, score) in enumerate(zip(predictions, scores)):
                result = PredictionResult(
                    asset_id=telemetry_data.iloc[i].get('asset_id', 'unknown'),
                    prediction_type='anomaly',
                    prediction=1.0 if pred == -1 else 0.0,  # 1 = anomaly, 0 = normal
                    confidence=abs(score),
                    timestamp=datetime.now(),
                    features_used=available_features,
                    model_version=self.model_version
                )
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error predicting anomalies: {e}")
            raise
    
    def predict_failure(self, telemetry_data: pd.DataFrame) -> List[PredictionResult]:
        """Predict failure probability"""
        try:
            if self.failure_predictor is None:
                raise ValueError("Failure predictor not trained or loaded")
            
            # Prepare features
            features_df = self.prepare_features(telemetry_data)
            available_features = [col for col in self.feature_columns if col in features_df.columns]
            X = features_df[available_features]
            
            # Scale features
            X_scaled = self.scaler.transform(X)
            
            # Predict probabilities
            probabilities = self.failure_predictor.predict_proba(X_scaled)
            
            results = []
            for i, prob in enumerate(probabilities):
                result = PredictionResult(
                    asset_id=telemetry_data.iloc[i].get('asset_id', 'unknown'),
                    prediction_type='failure',
                    prediction=prob[1] if len(prob) > 1 else prob[0],  # Probability of failure
                    confidence=max(prob),
                    timestamp=datetime.now(),
                    features_used=available_features,
                    model_version=self.model_version
                )
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error predicting failures: {e}")
            raise
    
    def predict_health_score(self, telemetry_data: pd.DataFrame) -> List[PredictionResult]:
        """Predict health score (0-100)"""
        try:
            if self.health_scorer is None:
                raise ValueError("Health scorer not trained or loaded")
            
            # Prepare features
            features_df = self.prepare_features(telemetry_data)
            available_features = [col for col in self.feature_columns if col in features_df.columns]
            X = features_df[available_features]
            
            # Scale features
            X_scaled = self.scaler.transform(X)
            
            # Predict health scores
            health_scores = self.health_scorer.predict(X_scaled)
            
            results = []
            for i, score in enumerate(health_scores):
                result = PredictionResult(
                    asset_id=telemetry_data.iloc[i].get('asset_id', 'unknown'),
                    prediction_type='health_score',
                    prediction=max(0, min(100, score)),  # Clamp to 0-100
                    confidence=0.8,  # Default confidence for regression
                    timestamp=datetime.now(),
                    features_used=available_features,
                    model_version=self.model_version
                )
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error predicting health scores: {e}")
            raise
    
    def generate_maintenance_recommendations(self, predictions: List[PredictionResult]) -> List[MaintenanceRecommendation]:
        """Generate maintenance recommendations based on predictions"""
        recommendations = []
        
        for pred in predictions:
            if pred.prediction_type == 'anomaly' and pred.prediction > 0.5:
                recommendations.append(MaintenanceRecommendation(
                    asset_id=pred.asset_id,
                    priority='high',
                    action='investigate_anomaly',
                    description=f"Anomaly detected with confidence {pred.confidence:.2f}. Investigate sensor readings and equipment condition.",
                    due_date=datetime.now() + timedelta(days=1)
                ))
            
            elif pred.prediction_type == 'failure' and pred.prediction > 0.7:
                recommendations.append(MaintenanceRecommendation(
                    asset_id=pred.asset_id,
                    priority='critical',
                    action='immediate_maintenance',
                    description=f"High failure probability ({pred.prediction:.2f}). Schedule immediate maintenance.",
                    estimated_downtime=4.0,
                    due_date=datetime.now() + timedelta(hours=24)
                ))
            
            elif pred.prediction_type == 'failure' and pred.prediction > 0.4:
                recommendations.append(MaintenanceRecommendation(
                    asset_id=pred.asset_id,
                    priority='medium',
                    action='scheduled_maintenance',
                    description=f"Moderate failure risk ({pred.prediction:.2f}). Schedule maintenance within a week.",
                    estimated_downtime=2.0,
                    due_date=datetime.now() + timedelta(days=7)
                ))
            
            elif pred.prediction_type == 'health_score' and pred.prediction < 30:
                recommendations.append(MaintenanceRecommendation(
                    asset_id=pred.asset_id,
                    priority='high',
                    action='health_assessment',
                    description=f"Low health score ({pred.prediction:.1f}). Conduct comprehensive health assessment.",
                    due_date=datetime.now() + timedelta(days=3)
                ))
        
        return recommendations

