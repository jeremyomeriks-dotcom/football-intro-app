#!/usr/bin/env python3
"""
Start Node Exporter
Finds and starts Node Exporter if already installed
Supports both Windows and Linux versions
"""

import subprocess
import sys
import platform
import os
import time
import urllib.request
from pathlib import Path

class Colors:
    CYAN = '\033[96m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'

def print_color(text, color):
    print(f"{color}{text}{Colors.RESET}")

def print_header(text):
    print()
    print_color("=" * 60, Colors.CYAN)
    print_color(text, Colors.CYAN)
    print_color("=" * 60, Colors.CYAN)
    print()

def check_if_running():
    """Check if Node Exporter is already running"""
    try:
        response = urllib.request.urlopen("http://localhost:9100/metrics", timeout=2)
        if response.status == 200:
            return True
    except:
        return False

def is_wsl():
    """Check if running in Windows Subsystem for Linux"""
    return "microsoft" in platform.uname().release.lower()

def find_node_exporter():
    """Try to find Node Exporter on the system - supports both Windows and Linux versions"""
    system = platform.system()
    is_wsl_env = is_wsl()
    
    possible_locations = []
    
    if system == "Windows" or is_wsl_env:
        # Check for both Windows and Linux executables
        possible_locations = []
        
        # Check for Windows version (if running from PowerShell)
        if system == "Windows":
            windows_paths = [
                Path("C:/node_exporter/node_exporter.exe"),
                Path("C:/Program Files/node_exporter/node_exporter.exe"),
                Path.home() / "node_exporter" / "node_exporter.exe",
                Path("node_exporter.exe"),
                # Check in Downloads directory
                Path.home() / "Downloads" / "node_exporter" / "node_exporter.exe",
                Path.home() / "Downloads" / "node_exporter-*" / "node_exporter.exe",
            ]
            possible_locations.extend(windows_paths)
        
        # Check for Linux version (for WSL or if user wants to use Linux version)
        # In WSL, we can access Windows drives via /mnt/c, etc.
        if is_wsl_env:
            # Check standard Linux paths in WSL
            linux_paths = [
                Path("/usr/local/bin/node_exporter"),
                Path("/usr/bin/node_exporter"),
                Path.home() / "node_exporter" / "node_exporter",
                Path("node_exporter"),
                Path.home() / ".local/bin/node_exporter",
            ]
            possible_locations.extend(linux_paths)
            
            # Also check Windows paths from WSL perspective
            # Map Windows drives to WSL paths
            windows_drives = ['c', 'd', 'e']
            for drive in windows_drives:
                windows_paths_from_wsl = [
                    Path(f"/mnt/{drive}/node_exporter/node_exporter.exe"),
                    Path(f"/mnt/{drive}/Program Files/node_exporter/node_exporter.exe"),
                    Path(f"/mnt/{drive}/Users") / os.environ.get('USER', '') / "node_exporter" / "node_exporter.exe",
                    Path(f"/mnt/{drive}/Users") / os.environ.get('USER', '') / "Downloads" / "node_exporter" / "node_exporter.exe",
                ]
                possible_locations.extend(windows_paths_from_wsl)
        elif system == "Windows":
            # If running from Windows PowerShell but user might have Linux version
            # Check common places where Linux executables might be placed
            wsl_home = os.environ.get('WSL_HOME', '')
            if wsl_home:
                linux_paths_windows = [
                    Path(wsl_home) / "node_exporter",
                    Path(wsl_home) / ".local/bin/node_exporter",
                ]
                possible_locations.extend(linux_paths_windows)
    
    # For pure Linux systems (not WSL)
    elif system == "Linux":
        possible_locations = [
            Path("/usr/local/bin/node_exporter"),
            Path("/usr/bin/node_exporter"),
            Path.home() / "node_exporter" / "node_exporter",
            Path("node_exporter"),
            Path.home() / ".local/bin/node_exporter",
            Path("/opt/node_exporter/node_exporter"),
        ]
    
    # Expand wildcards in paths
    expanded_locations = []
    for location in possible_locations:
        if '*' in str(location):
            parent_dir = location.parent
            if parent_dir.exists():
                for match in parent_dir.glob(location.name):
                    expanded_locations.append(match)
        else:
            expanded_locations.append(location)
    
    # Check all possible locations
    for location in expanded_locations:
        if location.exists():
            return location
    
    return None

def get_executable_type(exe_path):
    """Determine if executable is Windows (.exe) or Linux binary"""
    if exe_path.suffix == '.exe':
        return 'windows'
    else:
        # Check file header to confirm it's a Linux executable
        try:
            with open(exe_path, 'rb') as f:
                header = f.read(4)
                # ELF header for Linux executables
                if header == b'\x7fELF':
                    return 'linux'
        except:
            pass
        return 'unknown'

def start_node_exporter(exe_path):
    """Start Node Exporter in background"""
    print_color(f"Found Node Exporter: {exe_path}", Colors.BLUE)
    
    exe_type = get_executable_type(exe_path)
    system = platform.system()
    is_wsl_env = is_wsl()
    
    if exe_type == 'windows' and system == "Windows":
        print_color("Starting Windows version of Node Exporter...", Colors.BLUE)
        cmd = f'start /B cmd /c "{exe_path} > node_exporter.log 2>&1"'
    
    elif exe_type == 'linux' or (exe_type == 'windows' and is_wsl_env):
        print_color("Starting Linux version of Node Exporter...", Colors.BLUE)
        
        if is_wsl_env:
            # In WSL, we need to handle permissions and paths carefully
            # Make sure the executable has execute permissions
            try:
                subprocess.run(['chmod', '+x', str(exe_path)], check=True, capture_output=True)
            except:
                pass
        
        cmd = f'nohup {exe_path} > node_exporter.log 2>&1 &'
    
    else:
        print_color(f"Unknown executable type for: {exe_path}", Colors.YELLOW)
        print_color("Attempting to start with generic command...", Colors.YELLOW)
        
        if system == "Windows":
            cmd = f'start /B cmd /c "{exe_path} > node_exporter.log 2>&1"'
        else:
            cmd = f'nohup {exe_path} > node_exporter.log 2>&1 &'
    
    print_color(f"Starting Node Exporter with command: {cmd}", Colors.YELLOW)
    
    try:
        subprocess.Popen(cmd, shell=True)
        print_color("Waiting for Node Exporter to start...", Colors.YELLOW)
        time.sleep(3)
        
        if check_if_running():
            print_color("✅ Node Exporter started successfully", Colors.GREEN)
            return True
        else:
            print_color("❌ Node Exporter failed to start", Colors.RED)
            return False
    except Exception as e:
        print_color(f"❌ Error starting Node Exporter: {e}", Colors.RED)
        return False

def main():
    print_header("🖥️  Starting Node Exporter")
    
    system = platform.system()
    is_wsl_env = is_wsl()
    
    if is_wsl_env:
        print_color("Detected Windows Subsystem for Linux (WSL)", Colors.CYAN)
        print_color("Will search for both Windows and Linux versions", Colors.YELLOW)
        print()
    
    # Check if already running
    if check_if_running():
        print_color("✅ Node Exporter is already running on port 9100", Colors.GREEN)
        print()
        print_color("Access metrics at:", Colors.CYAN)
        print("  http://localhost:9100/metrics")
        print()
        return
    
    # Try to find Node Exporter
    print_color("Looking for Node Exporter...", Colors.BLUE)
    exe_path = find_node_exporter()
    
    if not exe_path:
        print_color("❌ Node Exporter not found", Colors.RED)
        print()
        print_color("Node Exporter needs to be installed first.", Colors.YELLOW)
        print()
        print_color("Download from:", Colors.CYAN)
        print("  https://github.com/prometheus/node_exporter/releases")
        print()
        print_color("Installation instructions:", Colors.CYAN)
        
        print("\nFor Windows PowerShell:")
        print("  1. Download node_exporter-*-windows-amd64.zip")
        print("  2. Extract to C:\\node_exporter\\")
        print("  3. Run this script again")
        
        print("\nFor Linux version (on WSL or native Linux):")
        print("  # Download and install")
        print("  wget https://github.com/prometheus/node_exporter/releases/download/v1.7.0/node_exporter-1.7.0.linux-amd64.tar.gz")
        print("  tar xvfz node_exporter-*.tar.gz")
        print("  sudo mv node_exporter-*/node_exporter /usr/local/bin/")
        print("  # Or extract to your home directory")
        print("  # Then run this script again")
        
        if is_wsl_env:
            print("\nFor WSL users:")
            print("  You can install either:")
            print("  - Windows version: In Windows file system (C:\\...)")
            print("  - Linux version: In WSL file system (/home/...)")
            print("  Both will be detected automatically")
        
        print()
        sys.exit(1)
    
    exe_type = get_executable_type(exe_path)
    print_color(f"✅ Found {exe_type.upper()} version of Node Exporter: {exe_path}", Colors.GREEN)
    print()
    
    # Start Node Exporter
    if start_node_exporter(exe_path):
        print()
        print_color("=" * 60, Colors.CYAN)
        print_color("✅ Node Exporter is Running!", Colors.GREEN)
        print_color("=" * 60, Colors.CYAN)
        print()
        print_color("Access metrics at:", Colors.CYAN)
        print("  http://localhost:9100/metrics")
        print()
        print_color("View in browser to see system metrics", Colors.YELLOW)
        print()
        print_color("Stop Node Exporter:", Colors.CYAN)
        
        exe_type = get_executable_type(exe_path)
        if exe_type == 'windows' or (exe_type == 'unknown' and system == "Windows"):
            print("  Windows PowerShell:")
            print("    taskkill /F /IM node_exporter.exe")
            print("    or press Ctrl+C in the terminal window")
        else:
            print("  Linux/WSL:")
            print("    pkill node_exporter")
            print("    or: kill $(pgrep node_exporter)")
            if is_wsl_env:
                print("\n  If using Windows version in WSL:")
                print("    taskkill.exe /F /IM node_exporter.exe")
        print()
    else:
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print_color("\n⚠️  Cancelled", Colors.YELLOW)
        sys.exit(1)
    except Exception as e:
        print()
        print_color(f"❌ Error: {e}", Colors.RED)
        import traceback
        traceback.print_exc()
        sys.exit(1)
