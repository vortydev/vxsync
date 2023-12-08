# machine_a_script.py

from vnode import VNode

if __name__ == "__main__":
    my_node = VNode(name="MachineA")
    my_node.display_info()
    my_node.comms.broadcast_online()

    # Continue with other tasks or interact with the online nodes list as needed
    input("Press Enter to stop...")
    my_node.comms.broadcast_offline()
    my_node.comms.stop_receiver_process()
