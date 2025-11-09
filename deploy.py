#!/usr/bin/env python3
"""
Cross-platform deployment script for Football Introduction App
Works on Windows, Linux, and macOS
"""

import subprocess
import sys
import platform

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"\n{'='*60}")
    print(f"📋 {description}")
    print(f"{'='*60}")
    
    try:
        # On Windows, shell=True is needed for commands like 'kind'
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            text=True,
            capture_output=True
        )
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(e.stderr)
        return False

def check_docker():
    """Check if Docker is running"""
    try:
        subprocess.run(
            "docker ps",
            shell=True,
            check=True,
            capture_output=True
        )
        return True
    except:
        return False

def check_cluster_exists():
    """Check if kind cluster already exists"""
    try:
        result = subprocess.run(
            "kind get clusters",
            shell=True,
            capture_output=True,
            text=True
        )
        return "football-app-cluster" in result.stdout
    except:
        return False

def main():
    print("🚀 Deploying Football Introduction App to Kubernetes\n")
    print(f"Platform: {platform.system()}")
    print(f"Python: {sys.version.split()[0]}\n")
    
    # Check Docker
    print("Checking Docker...")
    if not check_docker():
        print("❌ Docker is not running!")
        if platform.system() == "Windows":
            print("Please start Docker Desktop from the Start menu.")
        else:
            print("Please start Docker: sudo systemctl start docker")
        sys.exit(1)
    print("✅ Docker is running\n")
    
    # Check if cluster exists
    if check_cluster_exists():
        print("✅ Cluster 'football-app-cluster' already exists")
    else:
        print("📦 Creating kind cluster...")
        if not run_command(
            "kind create cluster --config kind-config.yaml",
            "Creating Kubernetes cluster"
        ):
            print("❌ Failed to create cluster")
            sys.exit(1)
        print("✅ Cluster created successfully")
    
    # Wait for nodes to be ready
    print("\n⏳ Waiting for cluster to be ready...")
    if not run_command(
        "kubectl wait --for=condition=Ready nodes --all --timeout=300s",
        "Waiting for nodes"
    ):
        print("⚠️  Timeout waiting for nodes, but continuing...")
    
    # Apply Kubernetes manifests
    if not run_command(
        "kubectl apply -f k8s/deployment.yaml",
        "Applying deployment manifest"
    ):
        print("❌ Failed to apply deployment")
        sys.exit(1)
    
    if not run_command(
        "kubectl apply -f k8s/service.yaml",
        "Applying service manifest"
    ):
        print("❌ Failed to apply service")
        sys.exit(1)
    
    # Wait for deployment
    print("\n⏳ Waiting for deployment to be ready...")
    if not run_command(
        "kubectl wait --for=condition=available --timeout=300s deployment/football-intro-app",
        "Waiting for deployment"
    ):
        print("⚠️  Deployment may not be ready yet")
    
    # Show status
    print("\n" + "="*60)
    print("📊 Deployment Status")
    print("="*60)
    
    run_command("kubectl get deployments", "Deployments")
    run_command("kubectl get pods", "Pods")
    run_command("kubectl get services", "Services")
    
    # Final message
    print("\n" + "="*60)
    print("✅ Deployment Complete!")
    print("="*60)
    print("\n🌐 Access your application at: http://localhost:8080\n")
    print("Useful commands:")
    print("  kubectl get pods                    - View pods")
    print("  kubectl logs <pod-name>             - View pod logs")
    print("  kubectl describe pod <pod-name>     - Get pod details")
    print("  kubectl delete -f k8s/              - Delete all resources")
    print("  kind delete cluster --name football-app-cluster  - Delete cluster")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Deployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
