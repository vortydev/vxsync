# machine_b_script.py

from vnode import VNode
import time

if __name__ == "__main__":
    my_node = VNode(name="MachineB")
    my_node.display_info()

    # Wait for a moment before checking the online nodes
    time.sleep(2)

    # Display the list of online nodes
    print("Online Nodes:")
    for online_node in my_node.comms.online_nodes:
        print(f" - {online_node.name} ({online_node.host}:{online_node.port})")

    # Continue with other tasks or interact with the online nodes list as needed
    input("Press Enter to stop...")
    my_node.comms.broadcast_offline()
    my_node.comms.stop_receiver_process()
