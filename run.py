#!/usr/bin/env python3
import sys
import subprocess

commands = {
    "dev": [
        "docker-compose",
        "-f",
        "docker-compose.yaml",
        "-f",
        "docker-compose.dev.yaml",
        "up",
    ],
    "prod": ["docker-compose", "up"],
    "down": ["docker-compose", "down"],
    "logs": ["docker-compose", "logs", "-f"],
    "build": ["docker-compose", "build"],
}

if len(sys.argv) < 2 or sys.argv[1] not in commands:
    print(f"Usage: python run.py [{' | '.join(commands.keys())}]")
    sys.exit(1)

subprocess.run(commands[sys.argv[1]])
