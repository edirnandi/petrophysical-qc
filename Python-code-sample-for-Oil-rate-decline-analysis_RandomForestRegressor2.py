import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

# Generate synthetic production data
np.random.seed(42)
months = np.arange(1, 121)  # 120 months of production
initial_rate = 1000  # Initial production rate in barrels/day
decline_rate = 0.05  # Initial decline rate (D)
hyperbolic_b = 0.5  # Hyperbolic exponent (b)

def hyperbolic_decline(t, q0, D, b):
    return q0 / ((1 + b * D * t) ** (1 / b))

# Generate production data with noise
production_data = hyperbolic_decline(months, initial_rate, decline_rate, hyperbolic_b)
production_data += np.random.normal(0, 20, len(months))

data = pd.DataFrame({'Month': months, 'Production_Rate': production_data})

# Fit hyperbolic model
popt, _ = curve_fit(hyperbolic_decline, data['Month'], data['Production_Rate'],
                    p0=(initial_rate, decline_rate, hyperbolic_b), 
                    bounds=([0, 0, 0], [np.inf, 1, 1]))

# Machine Learning Model (Random Forest)
X = data[['Month']]
y = data['Production_Rate']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

# Evaluate ML model
ml_predictions = rf_model.predict(X_test)
mae = mean_absolute_error(y_test, ml_predictions)
print(f"Machine Learning Model MAE: {mae:.2f} barrels/day")

# Predict future production (next 20 months)
future_months = np.arange(121, 141)
predicted_hyperbolic = hyperbolic_decline(future_months, *popt)
predicted_ml = rf_model.predict(future_months.reshape(-1, 1))

# Plot results
plt.figure(figsize=(12, 6))
plt.scatter(data['Month'], data['Production_Rate'], color='blue', label='Actual Data')
plt.plot(data['Month'], hyperbolic_decline(data['Month'], *popt), color='orange', label='Fitted Hyperbolic')
plt.plot(future_months, predicted_hyperbolic, color='red', linestyle='--', label='Hyperbolic Prediction')
plt.plot(future_months, predicted_ml, color='green', linestyle='-.', label='ML Prediction')
plt.title('Oil Rate Decline Analysis: Hyperbolic vs Machine Learning')
plt.xlabel('Month')
plt.ylabel('Production Rate (Barrels/Day)')
plt.legend()
plt.grid()
plt.show()
