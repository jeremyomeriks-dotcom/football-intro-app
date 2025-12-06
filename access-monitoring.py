#!/usr/bin/env python3
"""
Access Monitoring Dashboards - Python Version
Quick script to open port-forwards to Prometheus and Grafana
"""

import subprocess
import sys
import time
import webbrowser
from threading import Thread

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

def port_forward(service, namespace, local_port, remote_port, name):
    """Run kubectl port-forward in background"""
    cmd = f"kubectl port-forward -n {namespace} svc/{service} {local_port}:{remote_port}"
    print_color(f"Starting {name} port-forward...", Colors.BLUE)
    
    try:
        subprocess.run(cmd, shell=True, check=True)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print_color(f"Error with {name}: {e}", Colors.RED)

def main():
    print_header("📊 Access Monitoring Dashboards")
    
    print_color("This will open port-forwards to:", Colors.CYAN)
    print("  1. Application (http://localhost:8080)")
    print("  2. Prometheus (http://localhost:9090)")
    print("  3. Grafana (http://localhost:3000)")
    print()
    print_color("Press Ctrl+C to stop all port-forwards", Colors.YELLOW)
    print()
    
    # Start port-forwards in separate threads
    threads = []
    
    # Application
    t1 = Thread(
        target=port_forward,
        args=("football-intro-app-service", "default", "8080", "80", "Application")
    )
    t1.daemon = True
    t1.start()
    threads.append(t1)
    time.sleep(2)
    
    # Prometheus
    t2 = Thread(
        target=port_forward,
        args=("prometheus-kube-prometheus-prometheus", "monitoring", "9090", "9090", "Prometheus")
    )
    t2.daemon = True
    t2.start()
    threads.append(t2)
    time.sleep(2)
    
    # Grafana
    t3 = Thread(
        target=port_forward,
        args=("prometheus-grafana", "monitoring", "3000", "80", "Grafana")
    )
    t3.daemon = True
    t3.start()
    threads.append(t3)
    time.sleep(2)
    
    print()
    print_color("✅ All port-forwards started!", Colors.GREEN)
    print()
    
    print_color("Access URLs:", Colors.CYAN)
    print("  Application: http://localhost:8080")
    print("  Prometheus:  http://localhost:9090")
    print("  Grafana:     http://localhost:3000")
    print()
    
    print_color("Grafana Login:", Colors.YELLOW)
    print("  Username: admin")
    print("  Password: admin")
    print()
    
    # Ask if user wants to open browsers
    try:
        response = input("Open browsers automatically? (y/n): ").lower().strip()
        if response == 'y':
            time.sleep(2)
            webbrowser.open("http://localhost:8080")
            time.sleep(1)
            webbrowser.open("http://localhost:9090")
            time.sleep(1)
            webbrowser.open("http://localhost:3000")
            print_color("✅ Browsers opened", Colors.GREEN)
    except:
        pass
    
    print()
    print_color("Port-forwards are running. Press Ctrl+C to stop.", Colors.CYAN)
    print()
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print()
        print_color("\n⚠️  Stopping port-forwards...", Colors.YELLOW)
        print_color("✅ All port-forwards stopped", Colors.GREEN)
        sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print()
        print_color(f"❌ Error: {e}", Colors.RED)
        sys.exit(1)