#!/usr/bin/env python3
"""
Deploy Complete Monitoring Stack to Kubernetes
Deploys Football App, Prometheus, and Grafana with metrics enabled
"""

import subprocess
import sys
import time
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

def run_command(command, description=None, check=True):
    if description:
        print_color(description, Colors.BLUE)
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=check,
            text=True,
            capture_output=True
        )
        if result.stdout:
            print(result.stdout.strip())
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        if check:
            print_color(f"❌ Error: {e}", Colors.RED)
            if e.stderr:
                print(e.stderr)
        return False

def wait_for_pods(label, namespace="default", timeout=120):
    """Wait for pods to be ready"""
    print_color(f"⏳ Waiting for {label} pods to be ready...", Colors.YELLOW)
    
    elapsed = 0
    while elapsed < timeout:
        result = subprocess.run(
            f"kubectl get pods -l {label} -n {namespace} -o jsonpath='{{.items[*].status.containerStatuses[*].ready}}'",
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.stdout and "true" in result.stdout:
            print_color(f"✅ {label} pods are ready", Colors.GREEN)
            return True
        
        time.sleep(5)
        elapsed += 5
    
    print_color(f"⚠️  Timeout waiting for {label} pods", Colors.YELLOW)
    return False

def check_service(url, service_name, timeout=30):
    """Check if a service is accessible"""
    print_color(f"Checking {service_name}...", Colors.BLUE)
    
    for _ in range(timeout):
        try:
            response = urllib.request.urlopen(url, timeout=2)
            if response.status == 200:
                print_color(f"✅ {service_name} is accessible", Colors.GREEN)
                return True
        except:
            time.sleep(1)
    
    print_color(f"⚠️  {service_name} not accessible yet", Colors.YELLOW)
    return False

def main():
    print_header("🚀 Deploying Complete Monitoring Stack")
    
    print_color("This will deploy:", Colors.CYAN)
    print("  1. Football App with Nginx Exporter")
    print("  2. Prometheus (in Kubernetes)")
    print("  3. Grafana (in Kubernetes)")
    print()
    
    # Build and load app image
    print_header("Step 1: Building Football App Image")
    if not run_command("docker build -t football-intro-app:local ."):
        print_color("❌ Failed to build image", Colors.RED)
        sys.exit(1)
    print_color("✅ Image built", Colors.GREEN)
    print()
    
    print_color("Loading image into Kind cluster...", Colors.BLUE)
    if not run_command("kind load docker-image football-intro-app:local --name football-app-cluster"):
        print_color("❌ Failed to load image", Colors.RED)
        sys.exit(1)
    print_color("✅ Image loaded", Colors.GREEN)
    print()
    
    # Deploy Football App with metrics
    print_header("Step 2: Deploying Football App with Metrics")
    run_command("kubectl delete configmap nginx-config --ignore-not-found=true", check=False)
    run_command("kubectl delete deployment football-intro-app --ignore-not-found=true", check=False)
    run_command("kubectl delete service football-intro-app-service --ignore-not-found=true", check=False)
    time.sleep(5)
    
    if not run_command("kubectl apply -f k8s/nginx-exporter.yaml"):
        print_color("❌ Failed to deploy Football App", Colors.RED)
        sys.exit(1)
    
    wait_for_pods("app=football-intro-app")
    print()
    
    # Deploy Prometheus
    print_header("Step 3: Deploying Prometheus")
    run_command("kubectl delete deployment prometheus --ignore-not-found=true", check=False)
    run_command("kubectl delete service prometheus --ignore-not-found=true", check=False)
    run_command("kubectl delete configmap prometheus-config --ignore-not-found=true", check=False)
    time.sleep(5)
    
    if not run_command("kubectl apply -f k8s/prometheus-deployment.yaml"):
        print_color("❌ Failed to deploy Prometheus", Colors.RED)
        sys.exit(1)
    
    wait_for_pods("app=prometheus")
    print()
    
    # Deploy Grafana
    print_header("Step 4: Deploying Grafana")
    run_command("kubectl delete deployment grafana --ignore-not-found=true", check=False)
    run_command("kubectl delete service grafana --ignore-not-found=true", check=False)
    run_command("kubectl delete configmap grafana-datasources --ignore-not-found=true", check=False)
    time.sleep(5)
    
    if not run_command("kubectl apply -f k8s/grafana-deployment.yaml"):
        print_color("❌ Failed to deploy Grafana", Colors.RED)
        sys.exit(1)
    
    wait_for_pods("app=grafana")
    print()
    
    # Show status
    print_header("Step 5: Verifying Deployment")
    
    print_color("Deployments:", Colors.CYAN)
    run_command("kubectl get deployments", check=False)
    print()
    
    print_color("Services:", Colors.CYAN)
    run_command("kubectl get services", check=False)
    print()
    
    print_color("Pods:", Colors.CYAN)
    run_command("kubectl get pods", check=False)
    print()
    
    # Check services
    print_header("Step 6: Checking Service Accessibility")
    
    check_service("http://localhost:8080", "Football App")
    check_service("http://localhost:30090", "Prometheus")
    check_service("http://localhost:30030", "Grafana")
    
    # Final instructions
    print_header("✅ Monitoring Stack Deployed Successfully!")
    
    print_color("Access URLs:", Colors.CYAN)
    print("  🏈 Football App:  http://localhost:8080")
    print("  📊 Prometheus:    http://localhost:30090")
    print("  📈 Grafana:       http://localhost:30030 (admin/admin)")
    print("  📡 App Metrics:   http://localhost:30113/metrics")
    print()
    
    print_color("Verify Prometheus Targets:", Colors.YELLOW)
    print("  1. Open: http://localhost:30090/targets")
    print("  2. Check 'football-app' target is UP")
    print()
    
    print_color("View Metrics in Grafana:", Colors.YELLOW)
    print("  1. Open: http://localhost:30030")
    print("  2. Login: admin / admin")
    print("  3. Go to: Explore")
    print("  4. Select: Prometheus data source")
    print("  5. Try queries:")
    print("     - nginx_http_requests_total")
    print("     - nginx_connections_active")
    print("     - rate(nginx_http_requests_total[5m])")
    print()
    
    print_color("Create Dashboard:", Colors.YELLOW)
    print("  Run: python create-football-dashboard.py")
    print()
    
    print_color("Stop everything:", Colors.YELLOW)
    print("  python cleanup.py")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print_color("\n⚠️  Deployment interrupted", Colors.YELLOW)
        sys.exit(1)
    except Exception as e:
        print()
        print_color(f"❌ Deployment failed: {e}", Colors.RED)
        import traceback
        traceback.print_exc()
        sys.exit(1)
