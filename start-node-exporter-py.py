#!/usr/bin/env python3
"""
Start Node Exporter
Finds and starts Node Exporter if already installed
"""

import subprocess
import sys
import platform
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

def find_node_exporter():
    """Try to find Node Exporter on the system"""
    system = platform.system()
    
    possible_locations = []
    
    if system == "Windows":
        possible_locations = [
            Path("C:/node_exporter/node_exporter.exe"),
            Path.home() / "node_exporter" / "node_exporter.exe",
            Path("node_exporter.exe"),
        ]
    else:
        possible_locations = [
            Path("/usr/local/bin/node_exporter"),
            Path("/usr/bin/node_exporter"),
            Path.home() / "node_exporter" / "node_exporter",
            Path("node_exporter"),
        ]
    
    for location in possible_locations:
        if location.exists():
            return location
    
    return None

def start_node_exporter(exe_path):
    """Start Node Exporter in background"""
    print_color(f"Starting Node Exporter from: {exe_path}", Colors.BLUE)
    
    system = platform.system()
    
    if system == "Windows":
        cmd = f'start /B cmd /c "{exe_path} > node_exporter.log 2>&1"'
    else:
        cmd = f'nohup {exe_path} > node_exporter.log 2>&1 &'
    
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
        
        if platform.system() == "Windows":
            print("  1. Download node_exporter-*-windows-amd64.zip")
            print("  2. Extract to C:\\node_exporter\\")
            print("  3. Run: C:\\node_exporter\\node_exporter.exe")
        else:
            print("  # Download and install")
            print("  wget https://github.com/prometheus/node_exporter/releases/download/v1.7.0/node_exporter-1.7.0.linux-amd64.tar.gz")
            print("  tar xvfz node_exporter-*.tar.gz")
            print("  sudo mv node_exporter-*/node_exporter /usr/local/bin/")
            print("  node_exporter")
        print()
        sys.exit(1)
    
    print_color(f"✅ Found Node Exporter: {exe_path}", Colors.GREEN)
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
        if platform.system() == "Windows":
            print("  taskkill /F /IM node_exporter.exe")
        else:
            print("  pkill node_exporter")
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
