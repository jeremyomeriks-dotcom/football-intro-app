#!/usr/bin/env python3
"""
Start Port Forwards
Starts port-forwarding for all services to make them accessible
"""

import subprocess
import sys
import time
import platform
import urllib.request

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

def check_service_exists(service_name):
    """Check if Kubernetes service exists"""
    result = subprocess.run(
        f"kubectl get service {service_name}",
        shell=True,
        capture_output=True,
        text=True
    )
    return result.returncode == 0

def start_port_forward(service_name, local_port, service_port):
    """Start port forward in background"""
    print_color(f"Starting port-forward: {service_name} ({local_port} -> {service_port})", Colors.BLUE)
    
    cmd = f"kubectl port-forward service/{service_name} {local_port}:{service_port}"
    
    try:
        # Start in background
        if platform.system() == "Windows":
            # Windows: Use CREATE_NEW_PROCESS_GROUP to detach
            subprocess.Popen(
                cmd,
                shell=True,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        else:
            # Linux/Mac: Use nohup
            subprocess.Popen(
                f"nohup {cmd} > /dev/null 2>&1 &",
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                preexec_fn=lambda: None
            )
        
        print_color(f"  ✅ Port-forward started", Colors.GREEN)
        return True
    except Exception as e:
        print_color(f"  ❌ Failed: {e}", Colors.RED)
        return False

def check_url(url, service_name, max_attempts=10):
    """Check if URL is accessible"""
    print_color(f"Checking {service_name}...", Colors.YELLOW)
    
    for attempt in range(max_attempts):
        try:
            response = urllib.request.urlopen(url, timeout=2)
            if response.status == 200:
                print_color(f"  ✅ {service_name} is accessible!", Colors.GREEN)
                return True
        except:
            if attempt < max_attempts - 1:
                time.sleep(1)
    
    print_color(f"  ⚠️  {service_name} not accessible yet", Colors.YELLOW)
    return False

def main():
    print_header("🚀 Starting Port Forwards for All Services")
    
    # Define services to forward
    services = [
        ("football-intro-app-service", 8080, 80, "Football App", "http://localhost:8080"),
        ("prometheus", 9090, 9090, "Prometheus", "http://localhost:9090"),
        ("grafana", 3000, 3000, "Grafana", "http://localhost:3000"),
    ]
    
    # Check which services exist
    print_color("Checking available services...", Colors.BLUE)
    available_services = []
    
    for service_name, local_port, service_port, display_name, url in services:
        if check_service_exists(service_name):
            print_color(f"  ✅ {display_name} service found", Colors.GREEN)
            available_services.append((service_name, local_port, service_port, display_name, url))
        else:
            print_color(f"  ⚠️  {display_name} service not found", Colors.YELLOW)
    
    if not available_services:
        print()
        print_color("❌ No services found in cluster!", Colors.RED)
        print()
        print_color("Deploy services first:", Colors.YELLOW)
        print("  python deploy-monitoring-stack.py")
        sys.exit(1)
    
    print()
    
    # Start port forwards
    print_header("Starting Port Forwards")
    
    started_services = []
    for service_name, local_port, service_port, display_name, url in available_services:
        if start_port_forward(service_name, local_port, service_port):
            started_services.append((display_name, url))
        time.sleep(2)  # Small delay between starting each forward
    
    if not started_services:
        print_color("❌ Failed to start any port forwards", Colors.RED)
        sys.exit(1)
    
    print()
    
    # Wait a bit for port forwards to establish
    print_color("Waiting for port forwards to establish...", Colors.YELLOW)
    time.sleep(5)
    print()
    
    # Check accessibility
    print_header("Checking Service Accessibility")
    
    accessible = []
    for display_name, url in started_services:
        if check_url(url, display_name):
            accessible.append((display_name, url))
    
    print()
    
    # Show results
    print_header("✅ Port Forwards Active")
    
    if accessible:
        print_color("Accessible services:", Colors.GREEN)
        for display_name, url in accessible:
            print(f"  🌐 {display_name}: {url}")
    else:
        print_color("⚠️  Services may take a moment to become accessible", Colors.YELLOW)
        print_color("Try accessing these URLs:", Colors.CYAN)
        for display_name, url in started_services:
            print(f"  🌐 {display_name}: {url}")
    
    print()
    print_color("Port forwards are running in the background", Colors.CYAN)
    print()
    
    print_color("To stop port forwards:", Colors.YELLOW)
    if platform.system() == "Windows":
        print("  taskkill /F /IM kubectl.exe")
    else:
        print("  pkill kubectl")
    print()
    
    print_color("Press Ctrl+C to exit (port forwards will continue)", Colors.YELLOW)
    
    try:
        # Keep script running to show it's active
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print()
        print_color("Exiting (port forwards still active in background)", Colors.CYAN)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print_color("\n👋 Port forwards still running in background", Colors.CYAN)
        sys.exit(0)
    except Exception as e:
        print()
        print_color(f"❌ Error: {e}", Colors.RED)
        import traceback
        traceback.print_exc()
        sys.exit(1)
