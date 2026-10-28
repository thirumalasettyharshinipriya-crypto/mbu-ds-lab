import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("students.csv")
summary = df.groupby("subject")["marks"].agg(["mean", "min", "max"]).round(2)
print(summary)
summary.to_csv("marks_summary.csv")

df.groupby("subject")["marks"].mean().plot(kind="bar", title="Average Marks by Subject")
plt.ylabel("Average marks")
plt.tight_layout()
plt.savefig("marks_plot.png")
print("Saved marks_summary.csv and marks_plot.png")
