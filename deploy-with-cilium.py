#!/usr/bin/env python3
"""
Deploy Football App with Cilium Network Policies - Python Script
Cross-platform script to deploy the application after Cilium is setup
"""

import subprocess
import sys
import time

class Colors:
    """ANSI color codes for terminal output"""
    CYAN = '\033[96m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'

def print_color(text, color):
    """Print colored text"""
    print(f"{color}{text}{Colors.RESET}")

def print_header(text):
    """Print a header with decorative line"""
    print()
    print_color("=" * 60, Colors.CYAN)
    print_color(text, Colors.CYAN)
    print_color("=" * 60, Colors.CYAN)
    print()

def run_command(command, description=None, check=True, capture_output=True):
    """Run a shell command and handle errors"""
    if description:
        print_color(description, Colors.BLUE)
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=check,
            text=True,
            capture_output=capture_output
        )
        if capture_output and result.stdout:
            print(result.stdout)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        if check:
            print_color(f"❌ Error: {e}", Colors.RED)
            if e.stderr:
                print(e.stderr)
        return False

def check_pods_ready(label, timeout=120):
    """Wait for pods to be ready"""
    print()
    print_color("⏳ Waiting for pods to be ready...", Colors.BLUE)
    
    elapsed = 0
    while elapsed < timeout:
        try:
            result = subprocess.run(
                f"kubectl get pods -l {label} -o jsonpath='{{.items[*].status.containerStatuses[0].ready}}'",
                shell=True,
                capture_output=True,
                text=True,
                check=False
            )
            
            if "true" in result.stdout:
                print_color("✅ Application pods are ready", Colors.GREEN)
                return True
        except:
            pass
        
        print_color(f"Waiting... ({elapsed} seconds)", Colors.YELLOW)
        time.sleep(5)
        elapsed += 5
    
    print_color("⚠️  Timeout waiting for pods", Colors.YELLOW)
    return False

def main():
    print_header("🚀 Deploying Football App with Cilium Network Policies")

    # Build Docker image
    print_color("📦 Building Docker image...", Colors.BLUE)
    if not run_command("docker build -t football-intro-app:local .", capture_output=False):
        print_color("❌ Failed to build image", Colors.RED)
        sys.exit(1)
    print_color("✅ Image built", Colors.GREEN)

    # Load image into Kind cluster
    print()
    print_color("📦 Loading image into Kind cluster...", Colors.BLUE)
    if not run_command("kind load docker-image football-intro-app:local --name football-app-cluster", capture_output=False):
        print_color("❌ Failed to load image", Colors.RED)
        sys.exit(1)
    print_color("✅ Image loaded", Colors.GREEN)

    # Deploy application
    print()
    print_color("📋 Deploying application...", Colors.BLUE)
    
    if not run_command("kubectl apply -f k8s/deployment.yaml"):
        print_color("❌ Failed to deploy application", Colors.RED)
        sys.exit(1)
    
    if not run_command("kubectl apply -f k8s/service.yaml"):
        print_color("❌ Failed to deploy service", Colors.RED)
        sys.exit(1)

    # Wait for pods to be ready
    time.sleep(10)
    check_pods_ready("app=football-intro-app", timeout=120)

    # Show status
    print()
    print_color("📊 Current Status:", Colors.CYAN)
    print()
    print_color("Pods:", Colors.YELLOW)
    run_command("kubectl get pods -l app=football-intro-app", capture_output=False)
    
    print()
    print_color("Service:", Colors.YELLOW)
    run_command("kubectl get svc football-intro-app-service", capture_output=False)

    # Final message
    print_header("✅ Application Deployed!")
    
    print_color("Test access:", Colors.YELLOW)
    print("  kubectl port-forward service/football-intro-app-service 8080:80")
    print("  Then open: http://localhost:8080")
    print()
    
    print_color("Next: Apply network policies with:", Colors.YELLOW)
    print("  kubectl apply -f network-policies/")
    print("  Or run: python apply-network-policies.py")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print_color("\n⚠️  Deployment interrupted by user", Colors.YELLOW)
        sys.exit(1)
    except Exception as e:
        print()
        print_color(f"❌ Unexpected error: {e}", Colors.RED)
        import traceback
        traceback.print_exc()
        sys.exit(1)