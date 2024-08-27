try:
    import psutil
except:
    pass

import os
import platform
import socket

from src.util.utils import get_working_directory
from src.util.UtilFile import convert_size


LO_MAC_ADDRESS = '00:00:00:00:00:00'
LO_IP_ADDR = '127.0.0.1'


def get_rpi_model():
    try:
        if os.path.exists('/proc/device-tree/model'):
            with open('/proc/device-tree/model', 'r') as file:
                model = file.read().strip()
            return model
        else:
            return ''
    except Exception as e:
        return ''


def get_free_space():
    try:
        usage = psutil.disk_usage('/')
        return convert_size(usage.free)
    except Exception as e:
        return ''


def get_memory_usage():
    try:
        memory_info = psutil.virtual_memory()
        return {
            'total': convert_size(memory_info.total),
            'available': convert_size(memory_info.available),
            'percent': memory_info.percent,
            'used': convert_size(memory_info.used),
            'free': convert_size(memory_info.free)
        }
    except Exception as e:
        return ''


def get_network_info(all=False):
    interfaces = []
    try:
        addrs = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        for iface, addr_list in addrs.items():
            if stats[iface].isup:
                mac_address = None
                ip_address = None
                for addr in addr_list:

                    if addr.family == psutil.AF_LINK:
                        mac_address = addr.address
                    elif addr.family == socket.AF_INET:
                        ip_address = addr.address

                if mac_address and ip_address and mac_address != LO_MAC_ADDRESS and ip_address != LO_IP_ADDR:
                    interface = {
                        'interface': iface,
                        'mac_address': mac_address,
                        'ip_address': ip_address
                    }

                    if not all:
                        return interface

                    interfaces.append(interface)
        return '' if not all else interfaces
    except Exception:
        return '' if not all else interfaces


def get_os_version():
    try:
        return platform.platform()
    except Exception as e:
        return ''


def get_last_lines_of_logs(logfile, lines):
    try:
        if not os.path.exists(logfile):
            return ''
        with open(logfile, 'r') as file:
            logs = file.readlines()
            return ''.join(logs[-lines:])
    except Exception as e:
        return ''


def get_default_log_file():
    os_type = platform.system()
    if os_type == 'Linux':
        return '/var/log/syslog'
    elif os_type == 'Darwin':  # macOS
        return '/var/log/system.log'
    elif os_type == 'Windows':
        return 'C:\\Windows\\System32\\LogFiles\\WMI\\SysEvent.evt'
    else:
        return None


def get_network_ipaddr():
    network_info = get_network_info()

    if isinstance(network_info, dict):
        return network_info['ip_address']
    return None


def get_all_sysinfo():
    rpi_model = get_rpi_model()
    infos = {
        "sysinfo_device_model": rpi_model if rpi_model else 'sysinfo_device_model_unknown',
        "sysinfo_storage_free_space": get_free_space(),
        "sysinfo_memory_usage": "{}{}".format(get_memory_usage()['percent'], "%"),
        "sysinfo_os_version": get_os_version(),
        "sysinfo_install_directory": get_working_directory()
    }
    network_info = get_network_info(all=True)

    if isinstance(network_info, list) and len(network_info) > 0:
        infos["sysinfo_network_interface"] = ", ".join([iface['interface'] for iface in network_info])
        infos["sysinfo_mac_address"] = ", ".join([iface['mac_address'] for iface in network_info])
        infos["sysinfo_ip_address"] = ", ".join([iface['ip_address'] for iface in network_info])
    else:
        infos["sysinfo_ip_address"] = 'common_unknown_ipaddr'

    return infos
