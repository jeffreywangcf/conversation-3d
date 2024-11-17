from scapy.all import ARP, Ether, srp
import socket

def get_hostname(ip):
    try:
        hostname = socket.gethostbyaddr(ip)[0]
        return hostname
    except socket.herror:
        return "Unknown"

def scan_network(network="192.168.1.0/24"):
    arp = ARP(pdst=network)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp
    result = srp(packet, timeout=2, verbose=False)[0]
    devices = []
    for sent, received in result:
        device_info = {
            "ip": received.psrc,
            "mac": received.hwsrc,
            "hostname": get_hostname(received.psrc)
        }
        devices.append(device_info)
    return devices