import pandas as pd
from sklearn.linear_model import LogisticRegression

# Small demonstration dataset (study hours, attendance %, pass/fail)
data = pd.DataFrame({
    "study_hours": [1, 2, 2, 3, 4, 5, 6, 7, 8, 9],
    "attendance":  [45, 50, 60, 55, 65, 70, 75, 80, 90, 95],
    "passed":     [0, 0, 0, 0, 1, 1, 1, 1, 1, 1],
})

X = data[["study_hours", "attendance"]]
y = data["passed"]

model = LogisticRegression()
model.fit(X, y)

hours = float(input("Enter study hours per day: "))
attendance = float(input("Enter attendance percentage: "))
prediction = model.predict([[hours, attendance]])[0]
probability = model.predict_proba([[hours, attendance]])[0][1]

print("Prediction:", "Likely to pass" if prediction else "May need support")
print(f"Estimated pass probability: {probability:.1%}")
print("Note: Demonstration only; not a validated academic assessment.")
