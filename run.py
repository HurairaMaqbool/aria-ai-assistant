"""Convenience launcher for Aria AI Pro."""

import subprocess
import sys


def main():
    print("=" * 50)
    print("Starting Aria AI Pro...")
    print("=" * 50)
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], check=True)
    except KeyboardInterrupt:
        print("\nStopping Aria AI Pro...")
    except subprocess.CalledProcessError as exc:
        print(f"Error starting Streamlit: {exc}")
        sys.exit(exc.returncode)


if __name__ == "__main__":
    main()
