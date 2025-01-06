import ipaddress
from typing import Iterator
import geni.portal as portal

class NetworkManager:

    NODE_INTERFACE_NAME_FORMAT = "if%d"
    NODE_PHYSICAL_INTERFACE_FORMAT = "eth%d"
    VIRTUAL_INTERFACE_INDEX = 0
    PHYSICAL_INTERFACE_INDEX = 0

    ADDRESS_NETWORK = ipaddress.IPv4Network("10.0.0.0/24", False)
    ADDRESS_NETWORK_ITER: Iterator[ipaddress.IPv4Address] = ADDRESS_NETWORK.__iter__()

    @classmethod
    def nextVirtualInterface(cls) -> str:
        iface = cls.NODE_INTERFACE_NAME_FORMAT % cls.VIRTUAL_INTERFACE_INDEX
        cls.VIRTUAL_INTERFACE_INDEX += 1
        return iface

    @classmethod
    def nextPhysicalInterface(cls) -> str:
        iface = cls.NODE_PHYSICAL_INTERFACE_FORMAT % cls.PHYSICAL_INTERFACE_INDEX
        cls.PHYSICAL_INTERFACE_INDEX += 1
        return iface

    @classmethod
    def nextAddress(cls) -> ipaddress.IPv4Address:
        try:
            return cls.ADDRESS_NETWORK_ITER.__next__()
        except StopIteration:
            portal.context.reportError(portal.PortalError(
                "Address allocation exceeded subnet prefix: {}".format(
                    cls.ADDRESS_NETWORK.exploded
                )
            ))
        exit(1)

