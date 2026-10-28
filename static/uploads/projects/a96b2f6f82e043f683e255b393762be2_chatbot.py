FAQ = {
    "library": "The library provides academic books, journals, and study resources. Check your university portal for timings.",
    "attendance": "For attendance rules, consult your department or the official student handbook.",
    "project": "Choose a problem, define objectives, build a prototype, test it, and document the results.",
    "exam": "Check the official academic calendar and department notices for exam dates."
}

print("Campus FAQ Assistant (type 'exit' to quit)")
while True:
    question = input("You: ").strip().lower()
    if question == "exit":
        print("Assistant: Goodbye!")
        break
    answer = next((value for key, value in FAQ.items() if key in question), None)
    print("Assistant:", answer or "I don't know yet. Try asking about library, attendance, project, or exam.")
