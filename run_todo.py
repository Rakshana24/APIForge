import os
import shutil
from app import run_api_forge

def main():
    requirement = "A todo application where users can create, read, update, and delete tasks. Each task has a title (string), description (string), completed (boolean), and a due_date (datetime). Authentication is required. Users can register and login."
    answers = "Tasks should belong to users via a foreign key user_id. Authentication should be enabled."

    if os.path.exists("generated_project"):
        shutil.rmtree("generated_project")
        
    if os.path.exists("repair_observability.log"):
        os.remove("repair_observability.log")

    print("Running APIForge for Todo Management...")
    try:
        success = run_api_forge(requirement, answers=answers)
        print(f"\nExecution finished! Success: {success}")
    except Exception as e:
        print(f"\nExecution failed with error: {e}")

if __name__ == "__main__":
    main()
