import zmq
import time


"""Publisher process that registers services and emits topic-based messages."""

context = zmq.Context()

# Host used to publish ZeroMQ PUB sockets
MY_IP = "localhost"
MAIN_SERVER = "tcp://localhost:5555"

PORT1 = "15000"
PORT2 = "15001"
PORT3 = "15002"

# Register services in the main directory server (requirement b)
print("Registering services in the Main Server...")
req = context.socket(zmq.REQ)
req.connect(MAIN_SERVER)

services = {
    "Movies": f"tcp://{MY_IP}:{PORT1}",
    "WeatherTime": f"tcp://{MY_IP}:{PORT2}",
    "PersonalInfo": f"tcp://{MY_IP}:{PORT3}",
}

for name, address in services.items():
    req.send_string(f"REGISTER {name} {address}")
    response = req.recv_string()
    print(f"Registration for {name}: {response}")
req.close()

# PUB sockets for each service endpoint
pub1 = context.socket(zmq.PUB)
pub1.bind(f"tcp://0.0.0.0:{PORT1}")

pub2 = context.socket(zmq.PUB)
pub2.bind(f"tcp://0.0.0.0:{PORT2}")

pub3 = context.socket(zmq.PUB)
pub3.bind(f"tcp://0.0.0.0:{PORT3}")

print("\nPublisher waiting for subscribers...")
time.sleep(2)

while True:
    pub1.send(("[MOVIES] Harry Potter").encode("utf-8"))
    pub2.send(("[WEATHER] It is cloudy").encode("utf-8"))
    pub2.send(("[TIME] " + time.asctime()).encode("utf-8"))
    pub3.send(("[GITHUB] Felkim-dev").encode("utf-8"))
    pub3.send(("[LOCATION] Senescyt Building - Urcuqui").encode("utf-8"))
    print("Data published.")
    time.sleep(5)
