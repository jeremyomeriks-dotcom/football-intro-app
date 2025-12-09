[file name]: start-port-forwards.py
# In the main() function, update the services list:

    services = [
        ("football-intro-app-service", 8080, 80, "Football App", "http://localhost:8080"),
        ("prometheus", 9090, 9090, "Prometheus", "http://localhost:9090"),
        ("grafana", 3000, 3000, "Grafana", "http://localhost:3000"),
    ]

# ... later in the accessible services display ...

    print_color("Access all monitoring tools:", Colors.CYAN)
    print("  🏈 Football App:        http://localhost:8080")
    print("  📊 App Metrics Page:    http://localhost:8080/metrics-dashboard")
    print("  📡 Raw Metrics:         http://localhost:8080/app-metrics")
    print("  📈 Prometheus:          http://localhost:9090")
    print("  📋 Grafana:             http://localhost:3000")
