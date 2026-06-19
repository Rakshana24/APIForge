import subprocess
import sys

def test_execution_agent():

    try:

        process = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "tests"
            ],
            cwd="generated_project",
            capture_output=True,
            text=True,
            timeout=30
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