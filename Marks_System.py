# Student Marks Management Application
# Uses: list, tuple, dictionary and file processing

FILE_NAME = "students.txt"

# Tuple: subjects are fixed, so they should not change
SUBJECTS = ("Maths", "Python", "AI")

# List: stores all student records (each record is a dictionary)
students = []


def load_students():
    """Read student records from the file into the list."""
    try:
        with open(FILE_NAME, "r") as f:
            student = None
            for line in f:
                if ":" not in line:
                    continue  # skip separator lines and blank lines
                key, value = line.strip().split(":", 1)
                value = value.strip()
                if key == "Roll No":
                    student = {"roll": value, "name": "", "marks": []}
                    students.append(student)
                elif key == "Name":
                    student["name"] = value
                elif key in SUBJECTS:
                    student["marks"].append(int(value))
    except FileNotFoundError:
        pass  # file does not exist yet, start with an empty list


def save_students():
    """Write all student records from the list to the file."""
    with open(FILE_NAME, "w") as f:
        for s in students:
            total = sum(s["marks"])
            percentage = total / len(SUBJECTS)
            f.write("Roll No: " + s["roll"] + "\n")
            f.write("Name: " + s["name"] + "\n")
            for i in range(len(SUBJECTS)):
                f.write(SUBJECTS[i] + ": " + str(s["marks"][i]) + "\n")
            f.write("Total: " + str(total) + "\n")
            f.write("Percentage: {:.2f}%\n".format(percentage))
            f.write("-" * 30 + "\n")


def add_student():
    roll = input("Enter roll number: ")
    for s in students:
        if s["roll"] == roll:
            print("Roll number already exists.")
            return
    name = input("Enter name: ")
    marks = []
    for subject in SUBJECTS:
        marks.append(int(input("Enter marks in " + subject + ": ")))
    students.append({"roll": roll, "name": name, "marks": marks})
    save_students()
    print("Student added successfully.")


def show_result(s):
    total = sum(s["marks"])
    percentage = total / len(SUBJECTS)
    print("-" * 30)
    print("Roll No :", s["roll"])
    print("Name    :", s["name"])
    for i in range(len(SUBJECTS)):
        print(SUBJECTS[i], ":", s["marks"][i])
    print("Total   :", total)
    print("Percent : {:.2f}%".format(percentage))


def display_all():
    if len(students) == 0:
        print("No records found.")
        return
    for s in students:
        show_result(s)


def search_student():
    roll = input("Enter roll number to search: ")
    for s in students:
        if s["roll"] == roll:
            show_result(s)
            return
    print("Student not found.")


def show_topper():
    if len(students) == 0:
        print("No records found.")
        return
    topper = students[0]
    for s in students:
        if sum(s["marks"]) > sum(topper["marks"]):
            topper = s
    print("Topper of the class:")
    show_result(topper)


def main():
    load_students()
    while True:
        print("\n===== Student Marks Management =====")
        print("1. Add student")
        print("2. Display all students")
        print("3. Search student by roll number")
        print("4. Show topper")
        print("5. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            add_student()
        elif choice == "2":
            display_all()
        elif choice == "3":
            search_student()
        elif choice == "4":
            show_topper()
        elif choice == "5":
            print("Thank you!")
            break
        else:
            print("Invalid choice. Try again.")


main()
