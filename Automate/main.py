import json
import os

from models import Router, Interface, Network
from jinja2 import Environment, FileSystemLoader

def handle_network(network):
    ASList = {}
    for As in network['AS']:
        routerAsList = {}
        ipNetworkUsed = {}
        lastSubnetId = 0

        for router in As['routers']:

            routerObj = Router()
            routerObj.id = router['id']
            routerObj.hostname = router['hostName']

            intLoopback = Interface()
            intLoopback.name = 'Loopback0'
            intLoopback.address = router['id'] + "." + router['id'] + "." + router['id'] + "." + router['id']
            intLoopback.ospfArea = "0"
            routerObj.loopback = intLoopback
            routerObj.interfaces = []

            for connection in router['connections']:
                interface = Interface()
                interface.name = "GigabitEthernet" + connection['interface'] + "/0"

                if (router["id"], connection['router']) in ipNetworkUsed:
                    interface.prefix = ipNetworkUsed[(router["id"], connection['router'])]
                else:
                    lastSubnetId += 1
                    interface.prefix = lastSubnetId
                    ipNetworkUsed[(connection['router'], router["id"])] = lastSubnetId

                interface.address = "10.1." + str(interface.prefix) + "." + router['id']
                interface.ospfArea = connection['ospfArea']
                routerObj.interfaces.append(interface)

            networkObj = Network()
            networkObj.address = "10.1." + router['id'] + "." + "0"
            # networkObj.address = "10.1.0.0"
            networkObj.mask = "0.0.0.255"
            routerObj.network = networkObj

            routerAsList[routerObj.id] = routerObj

        ASList[As['number']] = routerAsList


    return ASList












if __name__ == '__main__':
    environment = Environment(loader=FileSystemLoader('Automate/templates/'), trim_blocks = True, lstrip_blocks = True)
    template = environment.get_template('config_template.txt')
    f = open('Automate/network.json','r')
    load = json.load(f)
    ASList = handle_network(load)
    for AS in ASList.values():
        for router in AS.values():
            print(router.hostname)
            # if router.hostname == "R1117":
            #     print(router.routeMapIns)
            path = "D:/INSA/INSA 3e TC/NAS/Projet_TP/project-files/dynamips"
            cfg_file = 'i' + str(load['routerMap'][router.hostname]) + "_startup-config.cfg"
            real_path=""
            for root, dirs, files in os.walk(path):
                if cfg_file in files:
                    real_path = os.path.join(root, cfg_file)
            f2 = open(real_path, "w")
            f2.write(template.render(router=router))
            f2.close()
            f = open("config/" + router.hostname + ".cfg", "w")
            f.write(template.render(router=router))
            f.close()

    f.close()