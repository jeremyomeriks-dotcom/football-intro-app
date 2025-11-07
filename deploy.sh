#!/bin/bash

set -e

echo "🚀 Deploying Football Introduction App to Kubernetes"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}Checking for existing kind cluster...${NC}"
if kind get clusters 2>/dev/null | grep -q "football-app-cluster"; then
    echo -e "${GREEN}Cluster already exists${NC}"
else
    echo -e "${BLUE}Creating kind cluster...${NC}"
    kind create cluster --config kind-config.yaml
    echo -e "${GREEN}Cluster created successfully${NC}"
fi

echo -e "${BLUE}Waiting for cluster to be ready...${NC}"
kubectl wait --for=condition=Ready nodes --all --timeout=300s

echo -e "${BLUE}Applying Kubernetes manifests...${NC}"
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

echo -e "${BLUE}Waiting for deployment to be ready...${NC}"
kubectl wait --for=condition=available --timeout=300s deployment/football-intro-app

echo -e "${GREEN}Deployment Status:${NC}"
kubectl get deployments
echo ""
echo -e "${GREEN}Pods:${NC}"
kubectl get pods
echo ""
echo -e "${GREEN}Services:${NC}"
kubectl get services

echo ""
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo -e "${BLUE}Access your application at: http://localhost:8080${NC}"
echo ""
echo "Useful commands:"
echo "  kubectl get pods                    - View pods"
echo "  kubectl logs <pod-name>             - View pod logs"
echo "  kubectl describe pod <pod-name>     - Get pod details"
echo "  kubectl delete -f k8s/              - Delete all resources"
echo "  kind delete cluster --name football-app-cluster  - Delete cluster"