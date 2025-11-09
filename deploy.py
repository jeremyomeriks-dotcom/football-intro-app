#!/usr/bin/env python3

import subprocess
import sys

def run_cmd(cmd, description):
    print(f"\n{'='*60}")
    print(f"📋 {description}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, text=True, capture_output=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(e.stderr)
        return False

def check_cluster():
    try:
        result = subprocess.run("kind get clusters", shell=True, capture_output=True, text=True)
        return "football-app-cluster" in result.stdout
    except:
        return False

print("🚀 Deploying Football Introduction App to Kubernetes\n")

if check_cluster():
    print("✅ Cluster 'football-app-cluster' already exists")
else:
    print("📦 Creating kind cluster...")
    if not run_cmd("kind create cluster --config kind-config.yaml", "Creating cluster"):
        sys.exit(1)
    print("✅ Cluster created")

print("\n⏳ Waiting for cluster to be ready...")
run_cmd("kubectl wait --for=condition=Ready nodes --all --timeout=300s", "Waiting for nodes")

run_cmd("kubectl apply -f k8s/deployment.yaml", "Applying deployment")
run_cmd("kubectl apply -f k8s/service.yaml", "Applying service")

print("\n⏳ Waiting for deployment...")
run_cmd("kubectl wait --for=condition=available --timeout=300s deployment/football-intro-app", "Waiting")

print("\n📊 Status:")
run_cmd("kubectl get deployments", "Deployments")
run_cmd("kubectl get pods", "Pods")
run_cmd("kubectl get services", "Services")

print("\n✅ Deployment Complete!")
print("🌐 Access at: http://localhost:8080\n")