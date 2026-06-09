import subprocess

from app.config import CMD_BINARY


def run_command_code(prompt: str):

    result = subprocess.run(
        [
            CMD_BINARY,
            "-p",
            prompt
        ],
        capture_output=True,
        text=True
    )

    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode
    }