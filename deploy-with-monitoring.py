#!/usr/bin/env python3
"""
Deploy Football App with Monitoring - Python Version
Deploy application with Prometheus metrics and Grafana dashboards
"""

import subprocess
import sys
import time

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

def print_step(step_num, text):
    print()
    print_color(f"📋 Step {step_num}: {text}", Colors.BLUE)

def run_command(command, check=True, capture_output=True):
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

def main():
    print_header("🚀 Deploying Football App with Monitoring")

    # Step 1: Build Docker image with metrics
    print_step(1, "Building Docker image with metrics support...")
    
    # Use Dockerfile.metrics if it exists, otherwise regular Dockerfile
    import os
    if os.path.exists("Dockerfile.metrics"):
        build_cmd = "docker build -f Dockerfile.metrics -t football-intro-app:local ."
    else:
        build_cmd = "docker build -t football-intro-app:local ."
    
    if not run_command(build_cmd, capture_output=False):
        print_color("❌ Failed to build image", Colors.RED)
        sys.exit(1)
    print_color("✅ Image built", Colors.GREEN)

    # Step 2: Load image into Kind cluster
    print_step(2, "Loading image into Kind cluster...")
    if not run_command("kind load docker-image football-intro-app:local --name football-app-cluster", 
                      capture_output=False):
        print_color("❌ Failed to load image", Colors.RED)
        sys.exit(1)
    print_color("✅ Image loaded", Colors.GREEN)

    # Step 3: Deploy application with metrics
    print_step(3, "Deploying application with metrics...")
    
    # Check if deployment-with-metrics.yaml exists
    import os
    if os.path.exists("k8s/deployment-with-metrics.yaml"):
        deployment_file = "k8s/deployment-with-metrics.yaml"
    else:
        deployment_file = "k8s/deployment.yaml"
    
    if not run_command(f"kubectl apply -f {deployment_file}"):
        print_color("❌ Failed to deploy application", Colors.RED)
        sys.exit(1)
    
    if not run_command("kubectl apply -f k8s/service.yaml"):
        print_color("❌ Failed to deploy service", Colors.RED)
        sys.exit(1)
    
    print_color("✅ Application deployed", Colors.GREEN)

    # Step 4: Deploy ServiceMonitor
    print_step(4, "Deploying ServiceMonitor for Prometheus...")
    
    if os.path.exists("monitoring/servicemonitor.yaml"):
        if run_command("kubectl apply -f monitoring/servicemonitor.yaml", check=False):
            print_color("✅ ServiceMonitor deployed", Colors.GREEN)
        else:
            print_color("⚠️  ServiceMonitor deployment failed (may not be needed)", Colors.YELLOW)
    else:
        print_color("⚠️  ServiceMonitor file not found, skipping...", Colors.YELLOW)

    # Step 5: Wait for pods
    print_step(5, "Waiting for pods to be ready...")
    time.sleep(10)
    
    timeout = 120
    elapsed = 0
    while elapsed < timeout:
        try:
            result = subprocess.run(
                "kubectl get pods -l app=football-intro-app -o jsonpath='{.items[*].status.containerStatuses[*].ready}'",
                shell=True,
                capture_output=True,
                text=True
            )
            
            if all(status == "true" for status in result.stdout.strip().split()):
                print_color("✅ Application pods are ready", Colors.GREEN)
                break
        except:
            pass
        
        print_color(f"Waiting... ({elapsed} seconds)", Colors.YELLOW)
        time.sleep(5)
        elapsed += 5

    # Step 6: Show status
    print_step(6, "Current status...")
    print()
    print_color("Application Pods:", Colors.CYAN)
    run_command("kubectl get pods -l app=football-intro-app", capture_output=False)
    
    print()
    print_color("Services:", Colors.CYAN)
    run_command("kubectl get svc", capture_output=False)

    # Final instructions
    print_header("✅ Deployment with Monitoring Complete!")
    
    print_color("Access Application:", Colors.YELLOW)
    print("  kubectl port-forward service/football-intro-app-service 8080:80")
    print("  Open: http://localhost:8080")
    print()
    
    print_color("Access Prometheus:", Colors.YELLOW)
    print("  kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090")
    print("  Open: http://localhost:9090")
    print("  Query examples:")
    print("    - nginx_connections_active")
    print("    - rate(nginx_http_requests_total[5m])")
    print()
    
    print_color("Access Grafana:", Colors.YELLOW)
    print("  kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80")
    print("  Open: http://localhost:3000")
    print("  Username: admin | Password: admin")
    print()
    
    print_color("Next: Import Grafana dashboard", Colors.CYAN)
    print("  1. Login to Grafana")
    print("  2. Go to Dashboards > Import")
    print("  3. Upload monitoring/football-app-dashboard.json")
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