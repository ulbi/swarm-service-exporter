# Swarm Service Exporter
A prometheus exporter, which emits three metrics.
| Metric                      | Description                                                                                                                                                    |
|-----------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| swarm_service_target_scale  | Gauge - Target number of tasks for this service. In mode "Global" - this is set to the number of swarm cluster nodes, otherwise the number of replicas is set. |
| swarm_service_current_scale | Gauge - Current number of running tasks for this service.                                                                                                      |
| swarm_service_start_count   | Counter - Counts the number of tasks starts.                                                                                                                   |

To build it:
```
    docker build -t swarm-service-exporter:latest
```

To run it either use docker:

```
    docker run --network <your prometheus net> -v /var/run/docker.sock:/var/run/docker.sock -p 9010:9010 -d --name exportertest swarm-service-exporter:latest 
```

Or use composer:

```
    swarm-service-exporter:
        image: swarm-service-exporter:latest
        networks:
          - <your prometheus net>
        volumes:
          - /var/run/docker.sock:/var/run/docker.sock
        deploy:
          resources:
            limits:
              memory: 128M
            reservations:
              memory: 64M
```

Include it in prometheus:

```
  - job_name: 'custom-metrics'
    static_configs:
      - targets: 
        - swarm-service-exporter:9010
```

You can also use those [rules](swarm-service-rules.yml).