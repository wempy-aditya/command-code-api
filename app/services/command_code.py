# app/services/command_code.py

import subprocess

from app.config import CMD_BINARY


def ask_command_code(prompt: str):

    result = subprocess.run(
        [
            CMD_BINARY,
            "-p",
            prompt
        ],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise Exception(result.stderr)

    return result.stdout.strip()