#!/usr/bin/env python3
import os
import sys
import venv
import subprocess
import platform
from pathlib import Path

class Launcher:
    def __init__(self):
        self.base_dir = Path(__file__).parent.absolute()
        self.venv_dir = self.base_dir / "venv"
        self.requirements_file = self.base_dir / "requirements.txt"
        self.is_windows = platform.system().lower() == "windows"
        
    def create_venv(self):
        """Step 1: Create virtual environment if it doesn't exist"""
        print("📦 Checking virtual environment...")
        if not self.venv_dir.exists():
            print("Creating virtual environment...")
            venv.create(self.venv_dir, with_pip=True)
            print("✅ Virtual environment created")
        else:
            print("✅ Virtual environment already exists")

    def get_venv_python(self):
        """Get the path to the virtual environment's Python executable"""
        if self.is_windows:
            return self.venv_dir / "Scripts" / "python.exe"
        return self.venv_dir / "bin" / "python"

    def get_venv_pip(self):
        """Get the path to the virtual environment's pip executable"""
        if self.is_windows:
            return self.venv_dir / "Scripts" / "pip.exe"
        return self.venv_dir / "bin" / "pip"

    def install_requirements(self):
        """Step 2: Install requirements"""
        print("\n📥 Installing requirements...")
        if not self.requirements_file.exists():
            print("❌ Error: requirements.txt not found")
            sys.exit(1)
        
        result = subprocess.run(
            [str(self.get_venv_pip()), "install", "-r", str(self.requirements_file)],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Requirements installed successfully")
        else:
            print(f"❌ Error installing requirements:\n{result.stderr}")
            sys.exit(1)

    def initialize_database(self):
        """Step 3: Initialize the database"""
        print("\n🗄️ Initializing database...")
        env = os.environ.copy()
        env["FLASK_APP"] = "app.py"
        
        # Create a Python script to initialize the database
        init_script = """
from app import app, db
with app.app_context():
    db.create_all()
"""
        result = subprocess.run(
            [str(self.get_venv_python()), "-c", init_script],
            env=env,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Database initialized successfully")
        else:
            print(f"❌ Error initializing database:\n{result.stderr}")
            sys.exit(1)

    def run_application(self):
        """Step 4 & 5: Set environment variables and run the application"""
        print("\n🚀 Starting the application...")
        env = os.environ.copy()
        env["FLASK_APP"] = "app.py"
        env["FLASK_DEBUG"] = "1"
        
        flask_path = self.venv_dir / "bin" / "flask"
        if self.is_windows:
            flask_path = self.venv_dir / "Scripts" / "flask.exe"

        print("\n🌐 Application is starting at http://127.0.0.1:5000")
        print("📝 Default admin credentials:")
        print("   Email: admin@admin.com")
        print("   Password: admin123")
        print("\n⌨️  Press Ctrl+C to stop the server")
        
        try:
            subprocess.run([str(flask_path), "run"], env=env)
        except KeyboardInterrupt:
            print("\n👋 Application stopped")

def main():
    print("🔧 Click Plumbing Admin Portal Launcher")
    print("=======================================")
    
    launcher = Launcher()
    
    try:
        launcher.create_venv()
        launcher.install_requirements()
        launcher.initialize_database()
        launcher.run_application()
    except KeyboardInterrupt:
        print("\n👋 Setup cancelled")
        sys.exit(0)

if __name__ == "__main__":
    main()
