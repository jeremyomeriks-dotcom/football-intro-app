#!/usr/bin/env python3
"""
Complete Monitoring Setup Script
Installs Prometheus and Grafana, configures everything, and starts services
"""

import subprocess
import sys
import os
import platform
import time
import json
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

def run_command(command, check=False):
    """Run a shell command"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=check,
            text=True,
            capture_output=True
        )
        return result.returncode == 0
    except:
        return False

def check_service(url, service_name):
    """Check if a service is running"""
    try:
        response = urllib.request.urlopen(url, timeout=2)
        if response.status == 200:
            print_color(f"✅ {service_name} is running", Colors.GREEN)
            return True
    except:
        pass
    print_color(f"⚠️  {service_name} is not running", Colors.YELLOW)
    return False

def start_prometheus():
    """Start Prometheus in background"""
    print_color("Starting Prometheus...", Colors.BLUE)
    
    system = platform.system()
    
    if system == "Windows":
        prom_dir = Path("C:/prometheus")
        prom_exe = prom_dir / "prometheus.exe"
    else:
        prom_dir = Path.home() / "prometheus"
        prom_exe = prom_dir / "prometheus"
    
    if not prom_exe.exists():
        print_color(f"❌ Prometheus not found at {prom_exe}", Colors.RED)
        print_color("Run: python install-prometheus.py first", Colors.YELLOW)
        return False
    
    # Start in background
    if system == "Windows":
        cmd = f'start /B cmd /c "cd {prom_dir} && prometheus.exe > prometheus.log 2>&1"'
    else:
        cmd = f'cd {prom_dir} && nohup ./prometheus > prometheus.log 2>&1 &'
    
    subprocess.Popen(cmd, shell=True)
    
    print_color("Waiting for Prometheus to start...", Colors.YELLOW)
    time.sleep(5)
    
    if check_service("http://localhost:9090", "Prometheus"):
        return True
    
    print_color("❌ Prometheus failed to start. Check prometheus.log", Colors.RED)
    return False

def start_grafana():
    """Start Grafana in background"""
    print_color("Starting Grafana...", Colors.BLUE)
    
    system = platform.system()
    
    if system == "Windows":
        grafana_dir = Path("C:/grafana/bin")
        grafana_exe = grafana_dir / "grafana-server.exe"
    else:
        grafana_dir = Path.home() / "grafana" / "bin"
        grafana_exe = grafana_dir / "grafana-server"
    
    if not grafana_exe.exists():
        print_color(f"❌ Grafana not found at {grafana_exe}", Colors.RED)
        print_color("Run: python install-grafana.py first", Colors.YELLOW)
        return False
    
    # Start in background
    if system == "Windows":
        cmd = f'start /B cmd /c "cd {grafana_dir} && grafana-server.exe > grafana.log 2>&1"'
    else:
        cmd = f'cd {grafana_dir} && nohup ./grafana-server > grafana.log 2>&1 &'
    
    subprocess.Popen(cmd, shell=True)
    
    print_color("Waiting for Grafana to start...", Colors.YELLOW)
    time.sleep(10)
    
    if check_service("http://localhost:3000", "Grafana"):
        return True
    
    print_color("❌ Grafana failed to start. Check grafana.log", Colors.RED)
    return False

def add_prometheus_datasource():
    """Add Prometheus as Grafana data source via API"""
    print_color("Adding Prometheus data source to Grafana...", Colors.BLUE)
    
    # Grafana API credentials
    api_url = "http://localhost:3000/api/datasources"
    auth = ("admin", "admin")
    
    datasource_config = {
        "name": "Prometheus",
        "type": "prometheus",
        "url": "http://localhost:9090",
        "access": "proxy",
        "isDefault": True,
        "jsonData": {
            "httpMethod": "POST"
        }
    }
    
    try:
        # Create request
        req = urllib.request.Request(
            api_url,
            data=json.dumps(datasource_config).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        
        # Add basic auth
        import base64
        credentials = base64.b64encode(f"{auth[0]}:{auth[1]}".encode()).decode()
        req.add_header('Authorization', f'Basic {credentials}')
        
        # Send request
        response = urllib.request.urlopen(req)
        
        if response.status == 200:
            print_color("✅ Prometheus data source added successfully", Colors.GREEN)
            return True
    except urllib.error.HTTPError as e:
        if e.code == 409:
            print_color("✅ Prometheus data source already exists", Colors.GREEN)
            return True
        print_color(f"⚠️  Could not add data source automatically: {e}", Colors.YELLOW)
        print_color("Add it manually in Grafana UI", Colors.YELLOW)
    except Exception as e:
        print_color(f"⚠️  Could not add data source automatically: {e}", Colors.YELLOW)
        print_color("Add it manually in Grafana UI", Colors.YELLOW)
    
    return False

def show_final_instructions():
    """Show final instructions to user"""
    print_header("✅ Monitoring Stack Setup Complete!")
    
    print_color("Services Status:", Colors.CYAN)
    print()
    
    prom_status = check_service("http://localhost:9090", "Prometheus")
    grafana_status = check_service("http://localhost:3000", "Grafana")
    node_exporter_status = check_service("http://localhost:9100/metrics", "Node Exporter")
    
    print()
    print_color("Access URLs:", Colors.CYAN)
    print("  📊 Prometheus: http://localhost:9090")
    print("  📈 Grafana:    http://localhost:3000 (admin/admin)")
    print("  🖥️  Node Exporter: http://localhost:9100/metrics")
    print()
    
    print_color("Quick Start:", Colors.CYAN)
    print("1. Open Grafana: http://localhost:3000")
    print("2. Login with: admin / admin (change password when prompted)")
    print("3. Go to: Connections → Data Sources → Prometheus")
    print("4. Import a dashboard:")
    print("   - Click '+' → Import")
    print("   - Enter dashboard ID: 1860 (Node Exporter Full)")
    print("   - Select Prometheus data source")
    print("   - Click 'Import'")
    print()
    
    print_color("Stop services:", Colors.CYAN)
    if platform.system() == "Windows":
        print("  taskkill /F /IM prometheus.exe")
        print("  taskkill /F /IM grafana-server.exe")
    else:
        print("  pkill prometheus")
        print("  pkill grafana-server")
    print()

def main():
    print_header("🚀 Complete Monitoring Stack Setup")
    
    print_color("This script will:", Colors.CYAN)
    print("  1. Check if Prometheus and Grafana are installed")
    print("  2. Start Prometheus")
    print("  3. Start Grafana")
    print("  4. Add Prometheus as a Grafana data source")
    print()
    
    try:
        response = input("Continue? (yes/no): ").lower().strip()
        if response not in ['yes', 'y']:
            print_color("Setup cancelled", Colors.YELLOW)
            sys.exit(0)
    except KeyboardInterrupt:
        print()
        sys.exit(0)
    
    print()
    
    # Check installations
    print_color("Checking installations...", Colors.BLUE)
    
    system = platform.system()
    if system == "Windows":
        prom_installed = Path("C:/prometheus/prometheus.exe").exists()
        grafana_installed = Path("C:/grafana/bin/grafana-server.exe").exists()
    else:
        prom_installed = (Path.home() / "prometheus" / "prometheus").exists()
        grafana_installed = (Path.home() / "grafana" / "bin" / "grafana-server").exists()
    
    if not prom_installed:
        print_color("⚠️  Prometheus not installed", Colors.YELLOW)
        print_color("Installing Prometheus...", Colors.BLUE)
        if run_command("python install-prometheus.py", check=False):
            print_color("✅ Prometheus installed", Colors.GREEN)
        else:
            print_color("❌ Failed to install Prometheus", Colors.RED)
            sys.exit(1)
    else:
        print_color("✅ Prometheus is installed", Colors.GREEN)
    
    if not grafana_installed:
        print_color("⚠️  Grafana not installed", Colors.YELLOW)
        print_color("Installing Grafana...", Colors.BLUE)
        if run_command("python install-grafana.py", check=False):
            print_color("✅ Grafana installed", Colors.GREEN)
        else:
            print_color("❌ Failed to install Grafana", Colors.RED)
            sys.exit(1)
    else:
        print_color("✅ Grafana is installed", Colors.GREEN)
    
    print()
    
    # Start services
    if not start_prometheus():
        sys.exit(1)
    
    print()
    
    if not start_grafana():
        sys.exit(1)
    
    print()
    
    # Wait a bit for Grafana to fully start
    print_color("Waiting for services to stabilize...", Colors.YELLOW)
    time.sleep(5)
    
    # Add Prometheus data source
    print()
    add_prometheus_datasource()
    
    # Show final instructions
    print()
    show_final_instructions()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print_color("\n⚠️  Setup cancelled", Colors.YELLOW)
        sys.exit(1)
    except Exception as e:
        print()
        print_color(f"❌ Setup failed: {e}", Colors.RED)
        import traceback
        traceback.print_exc()
        sys.exit(1)
