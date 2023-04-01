import json
import time
from prometheus_client.core import Gauge, Counter
from prometheus_client import start_http_server
import docker
from dateutil import parser
from datetime import datetime
from pytz import utc

class Collector():
    def __init__(self):
        # connect to docker
        self.client = docker.DockerClient(base_url='unix://var/run/docker.sock')
        # set the metrics
        self.gauge_target = Gauge("swarm_service_target_scale", "Target scale for this service", 
                               ["container_label_com_docker_stack_namespace",
                                "container_label_com_docker_swarm_service_id",
                                "container_label_com_docker_swarm_service_name"])

        self.gauge_current = Gauge("swarm_service_current_scale", "Current scale for this service", 
                               ["container_label_com_docker_stack_namespace",
                                "container_label_com_docker_swarm_service_id",
                                "container_label_com_docker_swarm_service_name"])
        self.count = Counter("swarm_service_start_count", "Number of times the service started", 
                               ["container_label_com_docker_stack_namespace",
                                "container_label_com_docker_swarm_service_id",
                                "container_label_com_docker_swarm_service_name"])
        self.lastcall = utc.localize(datetime.now())
        pass
    def collect(self):
        # get the number of docker nodes - this is the target count for mode "global"
        nodecount = len(self.client.nodes.list())
        # go through all services
        for service in self.client.services.list():
            service.reload()
            # get the target count
            targetcount=1
            if "Global" in service.attrs["Spec"]["Mode"].keys():
                targetcount=nodecount
            else:
                targetcount=service.attrs["Spec"]["Mode"]["Replicated"]["Replicas"]
            currentcount = 0
            start_count = 0
            # for all tasks in the service
            for task in service.tasks():
                # get creation time
                creationtime = parser.parse(task["CreatedAt"])
                # if it is running, add it to the current running count
                status = task["Status"]["State"]
                if status == "running":
                    currentcount += 1
                # has it been created since the last call?
                if creationtime > self.lastcall:
                    start_count += 1
            # fill the values
            namespace = service.attrs["Spec"]["Labels"]["com.docker.stack.namespace"]
            self.gauge_target.labels(namespace, service.id, service.name).set(targetcount)
            self.gauge_current.labels(namespace, service.id, service.name).set(currentcount)
            self.count.labels(namespace, service.id, service.name).inc(start_count)

        # remember the time
        self.lastcall = utc.localize(datetime.now())

if __name__ == "__main__":
    # port to listen to
    port = 9010
    frequency = 15
    # start the server
    start_http_server(port)
    # init the collector
    collector = Collector()
    while True: 
        # period between collection
        time.sleep(frequency)
        collector.collect()