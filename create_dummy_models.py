import pickle
import os

# Create models directory
os.makedirs("models", exist_ok=True)

# Create dummy models
models = {
    "demand_forecaster.pkl": {"type": "demand_forecaster", "version": "1.0", "status": "mock"},
    "price_predictor.pkl": {"type": "price_predictor", "version": "1.0", "status": "mock"},
    "fraud_detector.pkl": {"type": "fraud_detector", "version": "1.0", "status": "mock"},
    "merchant_matcher.pkl": {"type": "merchant_matcher", "version": "1.0", "status": "mock"},
    "recommendation_engine.pkl": {"type": "recommendation_engine", "version": "1.0", "status": "mock"}
}

for filename, data in models.items():
    filepath = os.path.join("models", filename)
    with open(filepath, 'wb') as f:
        pickle.dump(data, f)
    print(f"✅ Created {filepath}")

print("\n✅ All dummy models created successfully!")
