import json
import csv
from dataclasses import dataclass, asdict
from typing import List, Optional
from pathlib import Path
from datetime import datetime
import customtkinter as ctk
from tkinter import messagebox

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

@dataclass
class Task:
    description: str
    completed: bool = False
    priority: str = "Medium"
    due_date: Optional[str] = None
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

class TodoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("To-Do List Pro Max")
        self.geometry("660x460")
        self.resizable(False, False)
        self.filename = "tasks.json"
        self.tasks: List[Task] = []
        self.last_action = None
        self.load_tasks()
        self.build_ui()

    def build_ui(self):
        self.configure(bg="#000000")

        self.task_entry = ctk.CTkEntry(self, width=420, placeholder_text="📝 Task description", fg_color="#101010", border_color="red", border_width=2)
        self.task_entry.place(x=20, y=20)

        self.priority_var = ctk.StringVar(value="Medium")
        self.priority_menu = ctk.CTkOptionMenu(self, values=["Low", "Medium", "High"], variable=self.priority_var, width=100, fg_color="#101010", button_color="#222")
        self.priority_menu.place(x=460, y=20)

        self.due_entry = ctk.CTkEntry(self, width=200, placeholder_text="📅 Due Date (YYYY-MM-DD)", fg_color="#101010", border_color="red", border_width=2)
        self.due_entry.place(x=20, y=60)

        self.tags_entry = ctk.CTkEntry(self, width=340, placeholder_text="🏷️ Tags (comma-separated)", fg_color="#101010", border_color="red", border_width=2)
        self.tags_entry.place(x=240, y=60)

        self.add_btn = ctk.CTkButton(self, text="➕ Add Task", width=100, fg_color="red", hover_color="#ff4d4d", text_color="white", corner_radius=20)
        self.add_btn.place(x=560, y=20)
        self.add_btn.configure(command=self.add_task)

        self.task_listbox = ctk.CTkTextbox(self, width=620, height=260, fg_color="#0a0a0a", text_color="#ffdddd", border_color="red", border_width=2)
        self.task_listbox.place(x=20, y=110)
        self.task_listbox.configure(state="disabled")

        self.complete_btn = ctk.CTkButton(self, text="✅ Complete", width=120, fg_color="#202020", hover_color="red", border_color="red", border_width=2, text_color="white")
        self.complete_btn.place(x=20, y=390)
        self.complete_btn.configure(command=self.mark_completed)

        self.delete_btn = ctk.CTkButton(self, text="🗑️ Delete", width=120, fg_color="#202020", hover_color="red", border_color="red", border_width=2, text_color="white")
        self.delete_btn.place(x=160, y=390)
        self.delete_btn.configure(command=self.delete_task)

        self.export_btn = ctk.CTkButton(self, text="📤 Export CSV", width=120, fg_color="#202020", hover_color="red", border_color="red", border_width=2, text_color="white")
        self.export_btn.place(x=300, y=390)
        self.export_btn.configure(command=self.export_to_csv)

        self.undo_btn = ctk.CTkButton(self, text="↩️ Undo", width=100, fg_color="#202020", hover_color="red", border_color="red", border_width=2, text_color="white")
        self.undo_btn.place(x=440, y=390)
        self.undo_btn.configure(command=self.undo)

        self.brand_label = ctk.CTkLabel(self, text="🔎 Powered by Y7X 💗", text_color="#ff4d4d")
        self.brand_label.place(x=500, y=430)

        self.update_task_display()

    def load_tasks(self):
        try:
            if Path(self.filename).exists():
                with open(self.filename, 'r') as f:
                    data = json.load(f)
                    self.tasks = [Task(**task_data) for task_data in data]
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load tasks: {e}")

    def save_tasks(self):
        try:
            with open(self.filename, 'w') as f:
                json.dump([asdict(task) for task in self.tasks], f, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save tasks: {e}")

    def add_task(self):
        desc = self.task_entry.get().strip()
        if not desc:
            return messagebox.showwarning("Warning", "Task description cannot be empty.")
        prio = self.priority_var.get()
        due = self.due_entry.get().strip() or None
        tags = [tag.strip() for tag in self.tags_entry.get().split(',')] if self.tags_entry.get().strip() else []

        new_task = Task(description=desc, priority=prio, due_date=due, tags=tags)
        self.tasks.append(new_task)
        self.last_action = ('add', new_task)
        self.save_tasks()
        self.clear_inputs()
        self.update_task_display()

    def clear_inputs(self):
        self.task_entry.delete(0, 'end')
        self.due_entry.delete(0, 'end')
        self.tags_entry.delete(0, 'end')
        self.priority_var.set("Medium")

    def update_task_display(self):
        self.task_listbox.configure(state="normal")
        self.task_listbox.delete("1.0", "end")
        for i, task in enumerate(self.tasks, 1):
            status = "✅" if task.completed else "⬜"
            line = f"{i}. {status} {task.description} [{task.priority}]"
            if task.due_date:
                line += f" | Due: {task.due_date}"
            if task.tags:
                line += f" | Tags: {', '.join(task.tags)}"
            self.task_listbox.insert("end", line + "\n")
        self.task_listbox.configure(state="disabled")

    def mark_completed(self):
        idx = self.get_selected_task_index()
        if idx is not None and 0 <= idx < len(self.tasks):
            task = self.tasks[idx]
            task.completed = True
            self.last_action = ('complete', task)
            self.save_tasks()
            self.update_task_display()

    def delete_task(self):
        idx = self.get_selected_task_index()
        if idx is not None and 0 <= idx < len(self.tasks):
            removed = self.tasks.pop(idx)
            self.last_action = ('delete', removed)
            self.save_tasks()
            self.update_task_display()

    def get_selected_task_index(self):
        try:
            line = self.task_listbox.get("insert linestart", "insert lineend")
            if not line:
                return None
            return int(line.split('.')[0]) - 1
        except:
            return None

    def undo(self):
        if not self.last_action:
            messagebox.showinfo("Undo", "Nothing to undo.")
            return
        action, data = self.last_action[0], self.last_action[1]
        if action == 'add':
            self.tasks.remove(data)
        elif action == 'delete':
            self.tasks.append(data)
        elif action == 'complete':
            data.completed = False
        self.last_action = None
        self.save_tasks()
        self.update_task_display()

    def export_to_csv(self):
        try:
            with open("tasks_export.csv", 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Description", "Completed", "Priority", "Due Date", "Tags"])
                for task in self.tasks:
                    writer.writerow([task.description, task.completed, task.priority, task.due_date, ','.join(task.tags)])
            messagebox.showinfo("Export", "Tasks exported to tasks_export.csv")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

if __name__ == "__main__":
    app = TodoApp()
    app.mainloop()