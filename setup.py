import subprocess
import sys
import os

# Configuration for the build
APP_NAME = "SiteMapGenerator"  # Name for the output executable (without .exe suffix)
SCRIPT_NAME = "main.py"       # The main Python script to package

def build_executable():
    """
    Builds a standalone executable from the specified Python script using PyInstaller.
    """
    print(f"Starting build for {APP_NAME} from {SCRIPT_NAME}...")
    print("Please ensure PyInstaller is installed (e.g., 'pip install pyinstaller').")

    # Construct the PyInstaller command
    # sys.executable ensures we use the python interpreter running this script
    pyinstaller_command = [
        sys.executable,      # Path to the current Python interpreter
        "-m", "PyInstaller", # Run PyInstaller as a module
        "--onefile",         # Create a single executable file
        "--windowed",        # Application is GUI based, no console window (use --noconsole on some systems)
        f"--name={APP_NAME}", # Specify the name of the executable
        SCRIPT_NAME          # The script to package
    ]

    # Add --add-data for assets if needed in the future, e.g.
    # For example, if you have icons or other data files main.py needs:
    # "--add-data=icon.png:."
    # "--add-data=resources/data.json:resources"

    # For PyQt6, it's often necessary to explicitly include the bindings.
    # PyInstaller usually auto-detects them, but if not, hooks might be needed or explicit imports.
    # Example of what might be added if auto-detection fails (though usually not needed for basic PyQt6):
    # "--hidden-import=PyQt6.sip"
    # "--collect-all=PyQt6"


    print(f"Running command: {' '.join(pyinstaller_command)}")

    try:
        # Execute the PyInstaller command
        # capture_output=True and text=True to get stdout/stderr as strings
        process = subprocess.run(pyinstaller_command, check=True, capture_output=True, text=True)
        
        print("\n-------------------- BUILD SUCCESSFUL --------------------")
        # Determine the executable extension based on the OS
        exe_suffix = ".exe" if sys.platform == "win32" else ""
        executable_path = os.path.join(os.getcwd(), "dist", APP_NAME + exe_suffix)
        print(f"Executable created at: {executable_path}")
        
        if process.stdout:
            print("\nPyInstaller Output (stdout):\n", process.stdout)
        
    except subprocess.CalledProcessError as e:
        print("\n-------------------- BUILD FAILED --------------------")
        print("PyInstaller encountered an error.")
        print(f"Return code: {e.returncode}")
        if e.stdout:
            print("\nPyInstaller Output (stdout):\n", e.stdout)
        if e.stderr:
            print("\nPyInstaller Output (stderr):\n", e.stderr)
        print("\nTroubleshooting tips:")
        print("1. Ensure PyInstaller is installed and up-to-date ('pip install --upgrade pyinstaller').")
        print("2. Check that all dependencies of main.py (e.g., PyQt6, requests, beautifulsoup4) are installed in the environment.")
        print("3. If you have specific PyQt6 plugins or data files, you might need to use --add-data or --collect-all options.")
        print("4. Review the full output above for specific error messages from PyInstaller.")
        
    except FileNotFoundError:
        print("\n-------------------- BUILD FAILED --------------------")
        print("Error: PyInstaller command not found.")
        print(f"Attempted to run: {pyinstaller_command[0]} -m PyInstaller ...")
        print("Please ensure PyInstaller is installed and that the Python environment (sys.executable) is correctly configured.")
        print(f"Python interpreter being used: {sys.executable}")

    except Exception as e:
        print("\n-------------------- AN UNEXPECTED ERROR OCCURRED --------------------")
        print(f"An error of type {type(e).__name__} occurred: {e}")


if __name__ == "__main__":
    # Create a 'dist' directory if it doesn't exist, as PyInstaller will output there.
    # This is not strictly necessary as PyInstaller creates it, but can be good practice.
    if not os.path.exists("dist"):
        os.makedirs("dist", exist_ok=True)
        
    build_executable()
