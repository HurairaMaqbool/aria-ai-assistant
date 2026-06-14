import os
import subprocess
import sys

def main():
    print("=" * 50)
    print("🚀 STARTING ARIA AI PRO RUNNER...")
    print("=" * 50)
    
    # Run Streamlit app
    try:
        subprocess.run(["streamlit", "run", "app.py"])
    except KeyboardInterrupt:
        print("\nStopping Aria AI Pro...")
    except Exception as e:
        print(f"Error starting Streamlit: {e}")

if __name__ == "__main__":
    main()
