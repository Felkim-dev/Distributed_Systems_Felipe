import zmq


def lookup_service(service_name):
    """Resolve a service endpoint from main server, with replica failover."""
    context = zmq.Context.instance()

    # Try the main server first
    print(f"Looking up service '{service_name}' in the Main Server...")
    client = context.socket(zmq.REQ)
    client.connect("tcp://localhost:5555")
    client.send_string(f"LOOKUP {service_name}")

    poller = zmq.Poller()
    poller.register(client, zmq.POLLIN)

    # Max wait time: 2000 ms
    if poller.poll(2000):
        address = client.recv_string()
        client.close()
        return address
    else:
        # Timeout: fall back to replica server.
        print(
            f"TIMEOUT! Main Server is not responding. Looking up '{service_name}' in the Replica..."
        )
        client.setsockopt(zmq.LINGER, 0)
        client.close()

        # Query the replica server
        backup_client = context.socket(zmq.REQ)
        backup_client.connect("tcp://localhost:5556")
        backup_client.send_string(f"LOOKUP {service_name}")

        address = backup_client.recv_string()
        backup_client.close()
        return address


if __name__ == "__main__":
    context = zmq.Context.instance()
    s = context.socket(zmq.SUB)
    
    # Dynamically resolve where required services are running
    addr_weather_time = lookup_service("WeatherTime")
    addr_info = lookup_service("PersonalInfo")

    print("\n--- Connecting to Publishers ---")
    print(f"Connecting to WeatherTime at: {addr_weather_time}")
    print(f"Connecting to PersonalInfo at: {addr_info}")

    s.connect(addr_weather_time)
    s.connect(addr_info)

    # Topic subscriptions
    s.setsockopt_string(zmq.SUBSCRIBE, "[TIME]")
    s.setsockopt_string(zmq.SUBSCRIBE, "[GITHUB]")
    s.setsockopt_string(zmq.SUBSCRIBE, "[WEATHER]")

    print("\nWaiting for data...")
    for i in range(15):
        message = s.recv().decode("utf-8")
        print(message)
