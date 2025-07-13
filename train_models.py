"""
Model Training Script for Digital Twin Platform
"""
import pandas as pd
import numpy as np
from pathlib import Path
import logging
import sys
import os

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from models.predictive_maintenance import PredictiveMaintenanceModel
from training.data_generator import HVACDataGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main training function"""
    logger.info("Starting model training process")
    
    # Create directories
    data_dir = Path("../data")
    data_dir.mkdir(exist_ok=True)
    
    model_dir = Path("../models")
    model_dir.mkdir(exist_ok=True)
    
    # Generate synthetic training data
    logger.info("Generating synthetic training data")
    generator = HVACDataGenerator(seed=42)
    
    telemetry_data, failure_labels = generator.generate_training_dataset(
        num_assets=20,
        days_per_asset=60,
        failure_probability=0.12
    )
    
    # Generate health scores
    health_scores = generator.generate_health_scores(telemetry_data)
    
    # Save dataset
    dataset_path = data_dir / "hvac_training_data.csv"
    generator.save_dataset(telemetry_data, failure_labels, health_scores, dataset_path)
    
    # Initialize ML model
    logger.info("Initializing predictive maintenance model")
    pm_model = PredictiveMaintenanceModel(model_path=str(model_dir))
    
    # Train anomaly detection model
    logger.info("Training anomaly detection model")
    anomaly_results = pm_model.train_anomaly_detector(telemetry_data)
    logger.info(f"Anomaly detection results: {anomaly_results}")
    
    # Train failure prediction model
    logger.info("Training failure prediction model")
    failure_results = pm_model.train_failure_predictor(
        telemetry_data, failure_labels['failure']
    )
    logger.info(f"Failure prediction results: {failure_results}")
    
    # Train health scoring model
    logger.info("Training health scoring model")
    health_results = pm_model.train_health_scorer(telemetry_data, health_scores)
    logger.info(f"Health scoring results: {health_results}")
    
    # Test predictions on sample data
    logger.info("Testing predictions on sample data")
    
    # Generate test data
    test_data = generator.generate_normal_data(
        "TEST_001", 
        pd.Timestamp.now(), 
        duration_hours=2, 
        interval_minutes=15
    )
    
    # Load models and make predictions
    pm_model.load_models()
    
    # Test anomaly detection
    try:
        anomaly_predictions = pm_model.predict_anomaly(test_data)
        logger.info(f"Anomaly predictions: {len(anomaly_predictions)} results")
        for pred in anomaly_predictions[:3]:  # Show first 3
            logger.info(f"  Anomaly: {pred.prediction:.3f}, Confidence: {pred.confidence:.3f}")
    except Exception as e:
        logger.error(f"Error in anomaly prediction: {e}")
    
    # Test failure prediction
    try:
        failure_predictions = pm_model.predict_failure(test_data)
        logger.info(f"Failure predictions: {len(failure_predictions)} results")
        for pred in failure_predictions[:3]:  # Show first 3
            logger.info(f"  Failure prob: {pred.prediction:.3f}, Confidence: {pred.confidence:.3f}")
    except Exception as e:
        logger.error(f"Error in failure prediction: {e}")
    
    # Test health scoring
    try:
        health_predictions = pm_model.predict_health_score(test_data)
        logger.info(f"Health predictions: {len(health_predictions)} results")
        for pred in health_predictions[:3]:  # Show first 3
            logger.info(f"  Health score: {pred.prediction:.1f}, Confidence: {pred.confidence:.3f}")
    except Exception as e:
        logger.error(f"Error in health prediction: {e}")
    
    # Generate maintenance recommendations
    try:
        all_predictions = []
        if 'anomaly_predictions' in locals():
            all_predictions.extend(anomaly_predictions)
        if 'failure_predictions' in locals():
            all_predictions.extend(failure_predictions)
        if 'health_predictions' in locals():
            all_predictions.extend(health_predictions)
        
        recommendations = pm_model.generate_maintenance_recommendations(all_predictions)
        logger.info(f"Generated {len(recommendations)} maintenance recommendations")
        
        for rec in recommendations:
            logger.info(f"  {rec.priority}: {rec.action} - {rec.description}")
    
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
    
    logger.info("Model training completed successfully")

if __name__ == "__main__":
    main()

