from cqc.pythonLib import CQCConnection
import sys
import time

sys.path.append("../..")
from backends.cqc_backend import CQCBackend
from components.host import Host
from components.network import Network
from objects.qubit import Qubit


def main():
    network = Network.get_instance()
    nodes = ["Alice", "Bob", "Eve", "Dean"]
    network.start(nodes)
    network.delay = 0.7
    backend = CQCBackend()

    hosts = {'alice': Host('Alice', backend),
             'bob': Host('Bob', backend)}

    network.start(nodes)
    network.packet_drop_rate = 0.75
    network.delay = 0

    hosts['alice'].add_connection('Bob')
    hosts['bob'].add_connection('Alice')

    hosts['alice'].start()
    hosts['bob'].start()

    for h in hosts.values():
        network.add_host(h)

    # ACKs for 1 hop take at most 2 seconds
    hosts['alice'].max_ack_wait = 3
    num_acks = 0
    num_messages = 15
    for _ in range(num_messages):
        ack = hosts['alice'].send_classical(hosts['bob'].host_id, 'Hello Bob', await_ack=True)
        if ack:
            num_acks += 1

    num_messages_bob_received = len(hosts['bob'].classical)
    assert num_acks != num_messages
    assert num_acks < num_messages
    assert num_messages_bob_received < num_messages

    # ACKs can also get dropped
    assert num_messages_bob_received > num_acks
    assert float(num_acks) / num_messages < 0.9
    print("All tests succesfull!")
    network.stop(True)
    exit()


if __name__ == '__main__':
    main()