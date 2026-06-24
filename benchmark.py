import json
import os
import shutil
from app import run_api_forge

def run_benchmark():
    # Clear previous log files
    if os.path.exists("repair_observability.log"):
        os.remove("repair_observability.log")
        
    benchmarks = {
        "Contact Management": {
            "requirement": "A contact management system that allows users to perform CRUD operations on contacts. Each contact has a first_name (string), last_name (string), email (string), phone (string), and a created_at (datetime) timestamp. No authentication is required.",
            "answers": "No additional database fields. The database should be SQLite."
        },
        "Library Management": {
            "requirement": "A library management system where librarians can manage books, members, and loans. Books have a title (string), author (string), isbn (string), and available (boolean). Members have a name (string), email (string), and registration_date (datetime). Loans associate a book with a member and track the loan_date (datetime), due_date (datetime), and returned (boolean). No authentication is required.",
            "answers": "The relationship should be ForeignKey between loan and book, and loan and member."
        },
        "Todo Management": {
            "requirement": "A todo application where users can create, read, update, and delete tasks. Each task has a title (string), description (string), completed (boolean), and a due_date (datetime). Authentication is required. Users can register and login.",
            "answers": "Tasks should belong to users via a foreign key user_id. Authentication should be enabled."
        },
        "Inventory Management": {
            "requirement": "An inventory management system to track products and suppliers. Products have a name (string), description (string), price (integer), quantity (integer), and supplier_id (integer). Suppliers have a name (string), contact_email (string), and phone (string). Users should be able to perform CRUD operations on both products and suppliers.",
            "answers": "Products have a foreign key to suppliers."
        },
        "Student Management": {
            "requirement": "A student management system to manage courses and student enrollments. Students have a name (string), email (string), and age (integer). Courses have a name (string), code (string), and description (string). Enrollments link students to courses with an enrollment_date (datetime) and grade (string).",
            "answers": "Enrollments link students and courses."
        }
    }
    
    results = {}
    
    for name, data in benchmarks.items():
        print(f"\n==========================================")
        print(f"RUNNING BENCHMARK: {name}")
        print(f"==========================================\n")
        
        # Clean generated project directory before each benchmark
        if os.path.exists("generated_project"):
            shutil.rmtree("generated_project")
            
        # Clean repair log for this specific run
        if os.path.exists("repair_observability.log"):
            os.remove("repair_observability.log")
            
        metrics = {
            "validation_success": False,
            "execution_success": False,
            "test_success": False,
            "repairs_triggered": False,
            "repair_success": None
        }
        
        try:
            success = run_api_forge(data["requirement"], answers=data["answers"])
            if success:
                metrics["validation_success"] = True
                metrics["execution_success"] = True
                metrics["test_success"] = True
        except Exception as e:
            err_str = str(e)
            print(f"\nBenchmark {name} failed: {err_str}")
            
            if "Validation failed" in err_str:
                metrics["validation_success"] = False
            elif "Execution" in err_str or "Test Execution" in err_str:
                metrics["validation_success"] = True
                metrics["execution_success"] = False
            else:
                metrics["validation_success"] = True
                metrics["execution_success"] = True
                metrics["test_success"] = False
                
        # Check if repairs were triggered and if they succeeded
        if os.path.exists("repair_observability.log"):
            with open("repair_observability.log", "r") as f:
                lines = f.readlines()
            if len(lines) > 0:
                metrics["repairs_triggered"] = True
                metrics["repair_success"] = metrics["test_success"]
                
        results[name] = metrics

    total = len(benchmarks)
    val_success_count = sum(1 for r in results.values() if r["validation_success"])
    exec_success_count = sum(1 for r in results.values() if r["execution_success"])
    test_success_count = sum(1 for r in results.values() if r["test_success"])
    
    repairs_needed_count = sum(1 for r in results.values() if r["repairs_triggered"])
    repairs_succeeded_count = sum(1 for r in results.values() if r["repairs_triggered"] and r["repair_success"])
    
    summary = {
        "validation_success_rate": val_success_count / total,
        "execution_success_rate": exec_success_count / total,
        "test_success_rate": test_success_count / total,
        "repair_success_rate": (repairs_succeeded_count / repairs_needed_count) if repairs_needed_count > 0 else 1.0,
        "details": results
    }
    
    with open("benchmark_results.json", "w") as f:
        json.dump(summary, f, indent=4)
        
    print("\n==========================================")
    print("BENCHMARK COMPLETED")
    print(f"Results stored in benchmark_results.json")
    print(json.dumps(summary, indent=4))
    print("==========================================\n")

if __name__ == "__main__":
    run_benchmark()
