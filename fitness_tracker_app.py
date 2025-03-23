import streamlit as st
st.set_page_config(page_title="Personal Fitness Tracker", layout="wide")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt  # Added import for plotting
import seaborn as sns  # Added import for seaborn
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import time

# Suppress warnings
import warnings
warnings.filterwarnings('ignore')

# Header Section
st.title("🏋️ Personal Fitness Tracker")
st.markdown(
    "This app predicts **calories burned** based on fitness parameters like `Age`, `Gender`, `BMI`, and more. "
    "Adjust the sliders on the sidebar to get your personalized prediction."
)

# Sidebar - User Inputs
st.sidebar.header("📊 Set Your Fitness Goals")
goal = st.sidebar.selectbox("Select Your Fitness Goal", ("Weight Loss", "Muscle Gain", "Maintenance"))

def workout_recommendations(goal):
    if goal == "Weight Loss":
        return "Recommended workouts: Cardio exercises (running, cycling) for at least 30 minutes, 5 times a week."
    elif goal == "Muscle Gain":
        return "Recommended workouts: Strength training (weight lifting) 4-5 times a week, focusing on major muscle groups."
    elif goal == "Maintenance":
        return "Recommended workouts: A balanced mix of cardio and strength training, 3-4 times a week."
    else:
        return "No recommendations available."

st.sidebar.subheader("Workout Recommendations")
st.sidebar.write(workout_recommendations(goal))

st.sidebar.header("📊 Enter Your Fitness Profile")
st.sidebar.text_input("Name")
st.sidebar.text_input("Age")
st.sidebar.text_input("Weight (kg)")
st.sidebar.header("📊 Enter Your Daily Activity")

st.sidebar.header("📊 Enter Your Daily Exercise Duration (min)")
exercise_duration = st.sidebar.slider("Daily Exercise Duration (min)", 0, 120, 30, key="exercise_duration")
step_count = st.sidebar.number_input("Daily Step Count", min_value=0, value=5000, key="step_count")
st.sidebar.button("Reset Daily Activity", on_click=lambda: (st.session_state.update({"exercise_duration": 0, "step_count": 0})))


def user_input_features():
    age = st.sidebar.slider("Age", 10, 100, 30)
    bmi = st.sidebar.slider("BMI", 15, 40, 20)
    duration = st.sidebar.slider("Exercise Duration (min)", 0, 60, 20)
    heart_rate = st.sidebar.slider("Heart Rate (bpm)", 60, 150, 80)
    body_temp = st.sidebar.slider("Body Temperature (°C)", 35, 42, 37)
    blood_level = st.sidebar.slider("Blood Level (g/dL)", 10, 20, 15)  # New slider for blood level
    oxygen_level = st.sidebar.slider("Oxygen Level (%)", 80, 100, 95)  # New slider for oxygen level
    hydration_level = st.sidebar.slider("Hydration Level (liters)", 0.0, 5.0, 2.0)  # New slider for hydration level
    weight = st.sidebar.slider("Weight (kg)", 30, 200, 70)  # New slider for weight
    sleep_duration = st.sidebar.slider("Sleep Duration (hours)", 0, 24, 8)  # Existing slider for sleep duration

    gender = st.sidebar.radio("Gender", ("Male", "Female"))

    gender_encoded = 1 if gender == "Male" else 0
    
    return pd.DataFrame({
        "Age": [age], "BMI": [bmi], "Duration": [duration], 
        "Heart_Rate": [heart_rate], "Body_Temp": [body_temp], 
        "Blood_Level": [blood_level], "Oxygen_Level": [oxygen_level], 
        "Gender_male": [gender_encoded]
    })

df = user_input_features()
st.sidebar.subheader("Your Daily Activity Summary")
st.sidebar.write(f"Daily Exercise Duration: {exercise_duration} minutes")
st.sidebar.write(f"Daily Step Count: {step_count} steps")

# Display User Inputs
st.subheader("Your Input Parameters")
st.dataframe(df.style.set_properties(**{'background-color': '#30B6E4', 'color': 'black'}))

# Loading and Preprocessing Data
@st.cache_data
def load_data():
    calories = pd.read_csv("calories.csv")
    exercise = pd.read_csv("exercise.csv")
    df = exercise.merge(calories, on="User_ID").drop(columns="User_ID")
    df["BMI"] = round(df["Weight"] / ((df["Height"] / 100) ** 2), 2)
    return df

dataset = load_data()
X = dataset[["Gender", "Age", "BMI", "Duration", "Heart_Rate", "Body_Temp"]]

y = dataset["Calories"]
X = pd.get_dummies(X, drop_first=True)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)
model = RandomForestRegressor(n_estimators=500, max_depth=6)
model.fit(X_train, y_train)

# Predict Calories
st.subheader("🔥 Predicted Calories Burned")
df = df.reindex(columns=X_train.columns, fill_value=0)
prediction = model.predict(df)[0]
st.metric(label="Estimated Calories Burned", value=f"{round(prediction, 2)} kcal", delta_color="inverse")

# Display Similar Results
st.subheader("📌 Similar Results Based on Your Input")
calorie_range = [prediction - 10, prediction + 10]
similar_data = dataset[(dataset["Calories"] >= calorie_range[0]) & (dataset["Calories"] <= calorie_range[1])]
st.dataframe(similar_data.sample(n=min(5, len(similar_data)), random_state=1).style.set_properties(
    **{'background-color': '#D1F2EB', 'color': 'black'}
))

# Insights Section
st.subheader("📈 General Insights")
st.write(f"You are older than **{round((dataset['Age'] < df['Age'].values[0]).mean() * 100, 2)}%** of people in the dataset.")
st.write(f"Your exercise duration is longer than **{round((dataset['Duration'] < df['Duration'].values[0]).mean() * 100, 2)}%** of users.")
st.write(f"Your heart rate is higher than **{round((dataset['Heart_Rate'] < df['Heart_Rate'].values[0]).mean() * 100, 2)}%** of users.")
st.write(f"Your body temperature is higher than **{round((dataset['Body_Temp'] < df['Body_Temp'].values[0]).mean() * 100, 2)}%** of users.")

# Graphs Section for Daily Reports and Activity Tracker
st.subheader("📊 Daily Activity Tracker")
activity_data = [exercise_duration, step_count]
activity_labels = ['Exercise Duration (min)', 'Step Count']
plt.figure(figsize=(4, 4))  # Adjusted figure size

plt.pie(activity_data, labels=activity_labels, autopct='%1.1f%%', startangle=90, pctdistance=0.85)
centre_circle = plt.Circle((0, 0), 0.60, fc='white')  # Adjusted center circle radius
fig = plt.gcf()
fig.gca().add_artist(centre_circle)
plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

fig = plt.gcf()
fig.gca().add_artist(centre_circle)
plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
st.pyplot(plt)

st.subheader("📈 Daily Reports")
# Create mock daily report data
daily_report_data = {
    "Date": pd.date_range(start="2023-01-01", periods=30, freq='D'),
    "Calories Burned": np.random.randint(200, 500, size=30)  # Random calories burned
}
daily_report_df = pd.DataFrame(daily_report_data)

# Plotting the daily report data
plt.figure(figsize=(10, 5))  # Corrected the figure size with a comma

sns.lineplot(data=daily_report_df, x="Date", y="Calories Burned", marker="o", color='green')
plt.title("Daily Calories Burned Over the Last 30 Days")
plt.xlabel("Date")
plt.ylabel("Calories Burned")
plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(plt)

st.markdown("---")
st.markdown("*Built with ❤️ using Streamlit*")
