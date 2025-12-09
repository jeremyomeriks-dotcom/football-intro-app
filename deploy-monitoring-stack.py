[file name]: deploy-monitoring-stack.py
# Add after line ~50 (in the cleanup section)

    # Deploy Football App with metrics
    print_header("Step 2: Deploying Football App with Metrics")
    run_command("kubectl delete configmap nginx-config --ignore-not-found=true", check=False)
    run_command("kubectl delete configmap metrics-dashboard-html --ignore-not-found=true", check=False)  # ADD THIS LINE
    run_command("kubectl delete deployment football-intro-app --ignore-not-found=true", check=False)
    run_command("kubectl delete service football-intro-app-service --ignore-not-found=true", check=False)
    time.sleep(5)

# ... later in the final instructions section ...

    print_color("Access URLs:", Colors.CYAN)
    print("  🏈 Football App:        http://localhost:8080")
    print("  📊 App Metrics Page:    http://localhost:8080/metrics-dashboard")
    print("  📡 App Metrics API:     http://localhost:8080/app-metrics")
    print("  📈 Prometheus:          http://localhost:9090")
    print("  📋 Grafana:             http://localhost:3000 (admin/admin)")
    print()
    
    print_color("Try the built-in metrics dashboard:", Colors.YELLOW)
    print("  1. Open: http://localhost:8080/metrics-dashboard")
    print("  2. See real-time metrics from Prometheus")
    print("  3. Links to all monitoring tools")
    print()
