import zmq


def run_main():
    """Run the main directory server for service registration and lookup."""
    context = zmq.Context()

    # Handles Publishers (REGISTER) and Subscribers/Consumers (LOOKUP)
    frontend = context.socket(zmq.REP)
    frontend.bind("tcp://*:5555")

    # Internal channel used to replicate updates to the replica server
    backend = context.socket(zmq.PUSH)
    backend.bind("tcp://*:5557")

    directory = {}
    print("[MAIN] Main server started on port 5555...")

    while True:
        msg = frontend.recv_string()
        parts = msg.split()
        action = parts[0]

        if action == "REGISTER":
            service_name = parts[1]
            address = parts[2]
            directory[service_name] = address

            # Notify the replica server of each update (requirement b)
            backend.send_string(f"UPDATE {service_name} {address}")
            print(f"[MAIN] Registered: {service_name} -> {address}")

            frontend.send_string("OK")

        elif action == "LOOKUP":
            service_name = parts[1]
            # Return the service address or NOT_FOUND if missing
            location = directory.get(service_name, "NOT_FOUND")
            frontend.send_string(location)


if __name__ == "__main__":
    run_main()
