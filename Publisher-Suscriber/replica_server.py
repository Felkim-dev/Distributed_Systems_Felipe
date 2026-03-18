import zmq


def run_replica():
    """Run the replica directory server used for failover lookups."""
    context = zmq.Context()

    # Handles subscriber lookup requests if the main server fails
    frontend = context.socket(zmq.REP)
    frontend.bind("tcp://*:5556")

    # Receives background update replication from the main server
    backend = context.socket(zmq.PULL)
    backend.connect("tcp://localhost:5557")

    directory = {}
    print("[REPLICA] Replica server started on port 5556...")

    poller = zmq.Poller()
    poller.register(frontend, zmq.POLLIN)
    poller.register(backend, zmq.POLLIN)

    while True:
        socks = dict(poller.poll())

        # Process update messages from the main server
        if backend in socks:
            msg = backend.recv_string()
            parts = msg.split()
            if parts[0] == "UPDATE":
                directory[parts[1]] = parts[2]
                print(f"[REPLICA] Update received: {parts[1]} -> {parts[2]}")

        # Process failover lookup requests from subscribers
        if frontend in socks:
            msg = frontend.recv_string()
            parts = msg.split()
            if parts[0] == "LOOKUP":
                service_name = parts[1]
                location = directory.get(service_name, "NOT_FOUND")
                print(f"[REPLICA] Handling failover lookup for: {service_name}")
                frontend.send_string(location)


if __name__ == "__main__":
    run_replica()
