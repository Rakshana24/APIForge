import subprocess
import os
import sys

def execution_agent(project_path="generated_project"):

    main_file = os.path.join(
        project_path,
        "main.py"
    )

    try:
        print("Using Python:", sys.executable)
        process = subprocess.run(
            [sys.executable, main_file],
            capture_output=True,
            text=True,
            timeout=20
        )

        return {
            "success": process.returncode == 0,
            "stdout": process.stdout,
            "stderr": process.stderr
        }

    except Exception as e:

        return {
            "success": False,
            "stdout": "",
            "stderr": str(e)
        }