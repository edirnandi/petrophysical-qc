import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score

# Load WELL_1 and WELL_2 data
data_well_1 = pd.read_csv("well_log_data_WELL_1.csv")  # Replace with your actual file paths
data_well_2 = pd.read_csv("well_log_data_WELL_2.csv")

# Add WellName to distinguish between the two wells
data_well_1['WellName'] = 'WELL_1'
data_well_2['WellName'] = 'WELL_2'

# Combine the data into a single DataFrame
data = pd.concat([data_well_1, data_well_2], axis=0)

# Extract rows where Sonic DT is missing for WELL_2
missing_sonic_dt = data[(data['WellName'] == 'WELL_2') & data['SonicDT'].isna()]

# Extract rows where Sonic DT is available for WELL_1 (training data)
training_data = data[data['WellName'] == 'WELL_1']

# Define features (excluding SonicDT)
features = ['GammaRay', 'Resistivity', 'Density', 'NeutronPorosity']
#features = ['Depth','GammaRay', 'Resistivity', 'Density', 'NeutronPorosity']

# Prepare the training data (features and target)
X = training_data[features]
y = training_data['SonicDT']

# Normalize the features (optional)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Initialize the RandomForestRegressor model
model = RandomForestRegressor(n_estimators=100, random_state=42)

# Perform cross-validation (e.g., 5-fold cross-validation)
cv_scores = cross_val_score(model, X_scaled, y, cv=5, scoring='neg_mean_squared_error')

# The negative mean squared error needs to be converted to positive
cv_scores = -cv_scores

# Output the cross-validation results
print(f"Cross-Validation Mean Squared Errors: {cv_scores}")
print(f"Average Cross-Validation MSE: {cv_scores.mean()}")

# Train the model on the entire training data (since cross-validation is just for evaluation)
model.fit(X_scaled, y)

# Prepare the missing data from WELL_2 for prediction
X_missing = missing_sonic_dt[features]
X_missing_scaled = scaler.transform(X_missing)

# Predict the missing Sonic DT values for WELL_2
predicted_sonic_dt = model.predict(X_missing_scaled)

# Fill in the missing values in the original data for WELL_2
data.loc[data['SonicDT'].isna() & (data['WellName'] == 'WELL_2'), 'SonicDT'] = predicted_sonic_dt

# Extract only the rows for WELL_2 with the filled Sonic DT values
well_2_filled = data[data['WellName'] == 'WELL_2']

# Save the updated WELL_2 data to a new CSV file
well_2_filled.to_csv("well_log_data_WELL_2_SonicDT_added.csv", index=False)

# Optional: You can also print out a message indicating the CSV file was saved
print("CSV file with added Sonic DT values for WELL_2 has been saved as 'well_log_data_WELL_2_SonicDT_added.csv'")
