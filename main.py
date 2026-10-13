
import json
from datetime import date, datetime
from pathlib import Path

# Store tasks.txt in the same folder as this Python file.
FILE_PATH = Path(__file__).with_name("tasks.txt")


def load_tasks():
    """Load tasks saved from a previous session."""
    if not FILE_PATH.exists():
        return []

    try:
        with FILE_PATH.open("r", encoding="utf-8") as file:
            tasks = json.load(file)

        if not isinstance(tasks, list):
            print("Warning: Invalid task data. Starting with an empty list.")
            return []

        # Keep older tasks compatible with this version.
        valid_tasks = []
        for task in tasks:
            if isinstance(task, dict) and isinstance(task.get("name"), str):
                task.setdefault("completed", False)
                task.setdefault("due_date", "")
                valid_tasks.append(task)

        return valid_tasks

    except (json.JSONDecodeError, OSError):
        print("Warning: Could not read saved tasks. Starting with an empty list.")
        return []


def save_tasks(tasks):
    """Save all tasks to the file."""
    try:
        with FILE_PATH.open("w", encoding="utf-8") as file:
            json.dump(tasks, file, indent=4, ensure_ascii=False)
        return True
    except OSError:
        print("Error: Your tasks could not be saved.")
        return False


def get_task_number(tasks, action):
    """Ask for a task number and validate it."""
    try:
        number = int(input(f"Enter the task number to {action}: ").strip())

        if 1 <= number <= len(tasks):
            return number - 1

        print("That task number does not exist.")
    except ValueError:
        print("Please enter a whole number.")

    return None


def add_task(tasks):
    """Create a task with an optional due date."""
    task_name = input("Enter the task name: ").strip()

    if not task_name:
        print("Task name cannot be empty.")
        return

    due_date = input(
        "Enter the due date (YYYY-MM-DD), or press Enter to skip: "
    ).strip()

    if due_date:
        try:
            datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            print("Invalid date. Use YYYY-MM-DD, for example 2026-12-31.")
            return

    task = {
        "name": task_name,
        "completed": False,
        "due_date": due_date
    }

    tasks.append(task)

    if save_tasks(tasks):
        print("Task added and saved successfully!")


def view_tasks(tasks):
    """Display all tasks."""
    print("\n========== YOUR TASKS ==========")

    if not tasks:
        print("You have no tasks yet.")
        return

    today = date.today()

    for number, task in enumerate(tasks, start=1):
        status = "Completed" if task["completed"] else "Pending"
        due_date = task.get("due_date", "")

        if due_date:
            try:
                parsed_date = date.fromisoformat(due_date)

                if not task["completed"] and parsed_date < today:
                    status = "Overdue"
            except ValueError:
                pass

            date_text = f"Due: {due_date}"
        else:
            date_text = "No due date"

        print(f"{number}. {task['name']} | {status} | {date_text}")


def complete_task(tasks):
    """Mark a task as completed."""
    if not tasks:
        print("There are no tasks to complete.")
        return

    view_tasks(tasks)
    index = get_task_number(tasks, "complete")

    if index is None:
        return

    if tasks[index]["completed"]:
        print("This task is already completed.")
        return

    tasks[index]["completed"] = True

    if save_tasks(tasks):
        print(f"Completed: {tasks[index]['name']}")


def delete_task(tasks):
    """Delete a task selected by the user."""
    if not tasks:
        print("There are no tasks to delete.")
        return

    view_tasks(tasks)
    index = get_task_number(tasks, "delete")

    if index is None:
        return

    task_name = tasks[index]["name"]
    confirmation = input(
        f"Are you sure you want to delete '{task_name}'? (y/n): "
    ).strip().lower()

    if confirmation == "y":
        removed_task = tasks.pop(index)

        if save_tasks(tasks):
            print(f"Deleted: {removed_task['name']}")
        else:
            # Restore the task if saving fails.
            tasks.insert(index, removed_task)
    else:
        print("Deletion cancelled.")


def search_tasks(tasks):
    """Search for tasks by name."""
    keyword = input("Enter a word to search for: ").strip().lower()

    if not keyword:
        print("Please enter a search word.")
        return

    matches = [
        (number, task)
        for number, task in enumerate(tasks, start=1)
        if keyword in task["name"].lower()
    ]

    print("\n========== SEARCH RESULTS ==========")

    if not matches:
        print("No matching tasks found.")
        return

    for number, task in matches:
        status = "Completed" if task["completed"] else "Pending"
        due_date = task.get("due_date", "") or "No due date"
        print(f"{number}. {task['name']} | {status} | Due: {due_date}")


def show_overdue_tasks(tasks):
    """Display unfinished tasks whose due dates have passed."""
    today = date.today()
    overdue = []

    for number, task in enumerate(tasks, start=1):
        due_date = task.get("due_date", "")

        if task["completed"] or not due_date:
            continue

        try:
            if date.fromisoformat(due_date) < today:
                overdue.append((number, task))
        except ValueError:
            continue

    print("\n========== OVERDUE TASKS ==========")

    if not overdue:
        print("You have no overdue tasks. Great job!")
        return

    for number, task in overdue:
        print(f"{number}. {task['name']} | Due: {task['due_date']}")


def show_summary(tasks):
    """Show a quick overview of task progress."""
    total = len(tasks)
    completed = sum(1 for task in tasks if task["completed"])
    pending = total - completed

    print("\n========== TASK SUMMARY ==========")
    print(f"Total tasks: {total}")
    print(f"Completed: {completed}")
    print(f"Not completed: {pending}")


def main():
    print("=" * 40)
    print("       DAILY TASK TRACKER")
    print("=" * 40)

    name = input("Enter your name: ").strip()

    if not name:
        name = "User"

    tasks = load_tasks()

    print(f"\nWelcome, {name}!")
    print(f"Loaded {len(tasks)} saved task(s).")

    while True:
        print("\n========== MAIN MENU ==========")
        print("1. Add Task")
        print("2. View Tasks")
        print("3. Mark Task as Complete")
        print("4. Delete Task")
        print("5. Search Tasks")
        print("6. View Overdue Tasks")
        print("7. View Task Summary")
        print("8. Exit")

        choice = input("Choose an option (1-8): ").strip()

        if choice == "1":
            add_task(tasks)
        elif choice == "2":
            view_tasks(tasks)
        elif choice == "3":
            complete_task(tasks)
        elif choice == "4":
            delete_task(tasks)
        elif choice == "5":
            search_tasks(tasks)
        elif choice == "6":
            show_overdue_tasks(tasks)
        elif choice == "7":
            show_summary(tasks)
        elif choice == "8":
            print(f"\nGoodbye, {name}! Keep making progress.")
            break
        else:
            print("Invalid choice. Please choose a number from 1 to 8.")


if __name__ == "__main__":
    main()