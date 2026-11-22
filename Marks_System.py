


import os
import tkinter as tk
from tkinter import ttk, messagebox

# ----------------------------------------------------------------------
# Data layer (lists, tuples, dictionaries, file handling)
# ----------------------------------------------------------------------
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "marks_data.txt")
SUBJECTS = ["Maths", "Physics", "Chemistry", "Python", "Electrical"]   # list
MAX_MARKS = 100
PASS_MARKS = 35

students = {}   # dictionary: roll -> {"name": str, "marks": tuple}


def load_data():
    """Read students from the text file into the dictionary."""
    students.clear()
    if not os.path.exists(DATA_FILE):
        return
    block = {}                                # fields of the student being read

    def finish_block():
        """Turn the collected fields into a student entry (if complete)."""
        roll = block.get("Roll No")
        name = block.get("Name")
        if roll and name:
            try:
                marks = tuple(int(block[s]) for s in SUBJECTS)   # tuple of marks
            except (KeyError, ValueError):
                marks = None                  # skip corrupted block
            if marks is not None:
                students[roll] = {"name": name, "marks": marks}
        block.clear()

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if set(line) == {"-"}:            # separator line ends a student
                finish_block()
            elif ": " in line:                # "Key: value" line
                key, value = line.split(": ", 1)
                block[key.strip()] = value.strip()
            else:
                # old format support: roll,name,m1,m2,...
                parts = line.split(",")
                if len(parts) != 2 + len(SUBJECTS):
                    continue                  # skip corrupted lines
                try:
                    marks = tuple(int(x) for x in parts[2:])
                except ValueError:
                    continue
                students[parts[0]] = {"name": parts[1], "marks": marks}
    finish_block()                            # in case the last block has no separator


def save_data():
    """Write the dictionary back to the text file (one block per student)."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        for roll, info in sorted(students.items()):
            marks = info["marks"]
            f.write(f"Roll No: {roll}\n")
            f.write(f"Name: {info['name']}\n")
            for subject, mark in zip(SUBJECTS, marks):
                f.write(f"{subject}: {mark}\n")
            f.write(f"Total: {total_of(marks)}\n")
            f.write(f"Percentage: {percentage_of(marks):.2f}%\n")
            f.write("-" * 32 + "\n")


def total_of(marks):
    return sum(marks)


def percentage_of(marks):
    return total_of(marks) / (len(marks) * MAX_MARKS) * 100


def grade_of(marks):
    """Return (grade, result) as a tuple."""
    if min(marks) < PASS_MARKS:
        return ("F", "Fail")
    pct = percentage_of(marks)
    if pct >= 90:
        return ("A+", "Pass")
    if pct >= 80:
        return ("A", "Pass")
    if pct >= 70:
        return ("B", "Pass")
    if pct >= 60:
        return ("C", "Pass")
    if pct >= 50:
        return ("D", "Pass")
    return ("E", "Pass")


# ----------------------------------------------------------------------
# GUI layer
# ----------------------------------------------------------------------
BG = "#F4F7FB"
CARD = "#FFFFFF"
ACCENT = "#4F8EF7"
GREEN = "#5CC49A"
RED = "#F28B82"
TEXT = "#2D3748"
MUTED = "#8A94A6"


class MarksApp:
    def __init__(self, root):
        self.root = root
        root.title("Student Marks Manager")
        root.geometry("1020x680")
        root.minsize(900, 600)
        root.configure(bg=BG)

        self.entries = {}
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *a: self.refresh())

        self.setup_style()
        self.build_header()
        self.build_form()
        self.build_table()
        self.build_chart()

        load_data()
        self.refresh()

    # ---------- look & feel ----------
    def setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=CARD, fieldbackground=CARD,
                        foreground=TEXT, rowheight=26, borderwidth=0,
                        font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background="#E8EEF8", foreground=TEXT,
                        font=("Segoe UI", 10, "bold"), relief="flat")
        style.map("Treeview", background=[("selected", "#DCE8FD")],
                  foreground=[("selected", TEXT)])

    def make_button(self, parent, text, color, command):
        return tk.Button(parent, text=text, command=command, bg=color, fg="white",
                         activebackground=color, activeforeground="white",
                         relief="flat", bd=0, padx=10, pady=6, cursor="hand2",
                         font=("Segoe UI", 10, "bold"))

    # ---------- layout ----------
    def build_header(self):
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=20, pady=(16, 6))
        tk.Label(header, text="🎓  Student Marks Manager", bg=BG, fg=TEXT,
                 font=("Segoe UI", 18, "bold")).pack(side="left")
        self.stats_label = tk.Label(header, text="", bg=BG, fg=MUTED,
                                    font=("Segoe UI", 10))
        self.stats_label.pack(side="right")

    def build_form(self):
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=20, pady=6)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)
        self.body = body

        form = tk.Frame(body, bg=CARD, padx=16, pady=14)
        form.grid(row=0, column=0, sticky="ns", padx=(0, 14))
        tk.Label(form, text="Student details", bg=CARD, fg=TEXT,
                 font=("Segoe UI", 12, "bold")).grid(row=0, column=0,
                                                     columnspan=2, sticky="w", pady=(0, 8))
        fields = ["Roll No", "Name"] + SUBJECTS
        for i, label in enumerate(fields, start=1):
            tk.Label(form, text=label, bg=CARD, fg=MUTED,
                     font=("Segoe UI", 10)).grid(row=i, column=0, sticky="w", pady=4)
            entry = tk.Entry(form, width=18, relief="flat", bg="#EEF2F9", fg=TEXT,
                             font=("Segoe UI", 10), insertbackground=TEXT)
            entry.grid(row=i, column=1, padx=(10, 0), pady=4, ipady=4)
            self.entries[label] = entry

        row = len(fields) + 1
        self.make_button(form, "Add student", ACCENT, self.add_student).grid(
            row=row, column=0, columnspan=2, sticky="ew", pady=(12, 4))
        self.make_button(form, "Update selected", GREEN, self.update_student).grid(
            row=row + 1, column=0, columnspan=2, sticky="ew", pady=4)
        self.make_button(form, "Delete selected", RED, self.delete_student).grid(
            row=row + 2, column=0, columnspan=2, sticky="ew", pady=4)
        self.make_button(form, "Clear form", MUTED, self.clear_form).grid(
            row=row + 3, column=0, columnspan=2, sticky="ew", pady=4)

    def build_table(self):
        right = tk.Frame(self.body, bg=BG)
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)

        bar = tk.Frame(right, bg=BG)
        bar.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        tk.Label(bar, text="🔍 Search", bg=BG, fg=MUTED,
                 font=("Segoe UI", 10)).pack(side="left")
        tk.Entry(bar, textvariable=self.search_var, relief="flat", bg=CARD, fg=TEXT,
                 font=("Segoe UI", 10)).pack(side="left", padx=8, ipady=4,
                                             fill="x", expand=True)

        columns = ["Roll", "Name"] + SUBJECTS + ["Total", "%", "Grade", "Result"]
        self.tree = ttk.Treeview(right, columns=columns, show="headings",
                                 selectmode="browse")
        for col in columns:
            width = 140 if col == "Name" else 62
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="w" if col == "Name" else "center")
        self.tree.grid(row=1, column=0, sticky="nsew")
        self.tree.tag_configure("fail", foreground="#D9534F")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        scroll = ttk.Scrollbar(right, orient="vertical", command=self.tree.yview)
        scroll.grid(row=1, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scroll.set)

    def build_chart(self):
        card = tk.Frame(self.root, bg=CARD)
        card.pack(fill="x", padx=20, pady=(6, 16))
        tk.Label(card, text="Percentage by student", bg=CARD, fg=TEXT,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=14, pady=(10, 0))
        self.canvas = tk.Canvas(card, height=170, bg=CARD, highlightthickness=0)
        self.canvas.pack(fill="x", padx=14, pady=(0, 10))
        self.canvas.bind("<Configure>", lambda e: self.draw_chart())

    # ---------- form helpers ----------
    def read_form(self):
        """Validate the form and return (roll, name, marks_tuple)."""
        roll = self.entries["Roll No"].get().strip()
        name = self.entries["Name"].get().strip().replace(",", " ")
        if not roll or not name:
            raise ValueError("Roll No and Name cannot be empty.")
        if "," in roll:
            raise ValueError("Roll No cannot contain commas.")

        marks_list = []
        for subject in SUBJECTS:
            text = self.entries[subject].get().strip()
            try:
                value = int(text)
            except ValueError:
                raise ValueError(f"Marks for {subject} must be a whole number.")
            if not 0 <= value <= MAX_MARKS:
                raise ValueError(f"Marks for {subject} must be between 0 and {MAX_MARKS}.")
            marks_list.append(value)
        return roll, name, tuple(marks_list)

    def clear_form(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.tree.selection_remove(self.tree.selection())
        self.entries["Roll No"].focus_set()

    def on_select(self, _event=None):
        selected = self.tree.selection()
        if not selected:
            return
        roll = self.tree.item(selected[0])["values"][0]
        roll = str(roll)
        info = students.get(roll)
        if info is None:
            return
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.entries["Roll No"].insert(0, roll)
        self.entries["Name"].insert(0, info["name"])
        for subject, mark in zip(SUBJECTS, info["marks"]):
            self.entries[subject].insert(0, str(mark))

    # ---------- actions ----------
    def add_student(self):
        try:
            roll, name, marks = self.read_form()
        except ValueError as err:
            messagebox.showerror("Invalid input", str(err))
            return
        if roll in students:
            messagebox.showerror("Duplicate", f"Roll No {roll} already exists. Use Update instead.")
            return
        students[roll] = {"name": name, "marks": marks}
        self.save_and_refresh()
        self.clear_form()

    def update_student(self):
        try:
            roll, name, marks = self.read_form()
        except ValueError as err:
            messagebox.showerror("Invalid input", str(err))
            return
        if roll not in students:
            messagebox.showerror("Not found", f"Roll No {roll} does not exist. Use Add instead.")
            return
        students[roll] = {"name": name, "marks": marks}
        self.save_and_refresh()

    def delete_student(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Delete", "Select a student in the table first.")
            return
        roll = str(self.tree.item(selected[0])["values"][0])
        if messagebox.askyesno("Confirm delete", f"Delete Roll No {roll}?"):
            students.pop(roll, None)
            self.save_and_refresh()
            self.clear_form()

    def save_and_refresh(self):
        try:
            save_data()
        except OSError as err:
            messagebox.showerror("File error", f"Could not save data:\n{err}")
        self.refresh()

    # ---------- display ----------
    def visible_rolls(self):
        """Return a list of roll numbers matching the search box."""
        query = self.search_var.get().strip().lower()
        rolls = []
        for roll, info in sorted(students.items()):
            if query in roll.lower() or query in info["name"].lower():
                rolls.append(roll)
        return rolls

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for roll in self.visible_rolls():
            info = students[roll]
            marks = info["marks"]
            grade, result = grade_of(marks)
            values = [roll, info["name"], *marks, total_of(marks),
                      f"{percentage_of(marks):.1f}", grade, result]
            tag = ("fail",) if result == "Fail" else ()
            self.tree.insert("", "end", values=values, tags=tag)
        self.update_stats()
        self.draw_chart()

    def update_stats(self):
        if not students:
            self.stats_label.config(text="No students yet - add one!")
            return
        pcts = {roll: percentage_of(i["marks"]) for roll, i in students.items()}
        average = sum(pcts.values()) / len(pcts)
        topper = max(pcts, key=pcts.get)
        passed = sum(1 for i in students.values() if grade_of(i["marks"])[1] == "Pass")
        self.stats_label.config(
            text=f"Students: {len(students)}   |   Class avg: {average:.1f}%   |   "
                 f"Topper: {students[topper]['name']} ({pcts[topper]:.1f}%)   |   "
                 f"Passed: {passed}/{len(students)}")

    def draw_chart(self):
        c = self.canvas
        c.delete("all")
        rolls = self.visible_rolls()
        width = max(c.winfo_width(), 300)
        height = int(c["height"])
        base_y = height - 24
        top_y = 14
        if not rolls:
            c.create_text(width / 2, height / 2, text="Chart will appear here",
                          fill=MUTED, font=("Segoe UI", 10))
            return

        # light grid lines at 0 / 50 / 100 %
        for pct in (0, 50, 100):
            y = base_y - (base_y - top_y) * pct / 100
            c.create_line(36, y, width - 8, y, fill="#E6EBF3")
            c.create_text(30, y, text=str(pct), fill=MUTED, anchor="e",
                          font=("Segoe UI", 8))

        slot = (width - 50) / len(rolls)
        bar_w = min(46, slot * 0.6)
        for i, roll in enumerate(rolls):
            marks = students[roll]["marks"]
            pct = percentage_of(marks)
            colour = GREEN if grade_of(marks)[1] == "Pass" else RED
            x_mid = 40 + slot * i + slot / 2
            y = base_y - (base_y - top_y) * pct / 100
            c.create_rectangle(x_mid - bar_w / 2, y, x_mid + bar_w / 2, base_y,
                               fill=colour, outline="")
            c.create_text(x_mid, y - 7, text=f"{pct:.0f}%", fill=TEXT,
                          font=("Segoe UI", 8))
            label = roll if len(roll) <= 8 else roll[:7] + "…"
            c.create_text(x_mid, base_y + 11, text=label, fill=MUTED,
                          font=("Segoe UI", 8))


def main():
    root = tk.Tk()
    MarksApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
