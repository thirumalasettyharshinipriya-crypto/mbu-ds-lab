# Sample Matplotlib file
import matplotlib.pyplot as plt
subjects = ["DS", "LRRE", "CRDT", "CAO", "IoT"]
marks = [85, 90, 78, 92, 88]
plt.bar(subjects, marks)
plt.title("Sample Subject Marks")
plt.xlabel("Subject")
plt.ylabel("Marks")
plt.tight_layout()
plt.show()
