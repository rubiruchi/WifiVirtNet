#!/usr/bin/python
# −∗− coding: utf8 −∗−
"""
    mesh.py cria hosts e atribue interfaces 802.11 a eles e
    depois interfaces 802.11s e testando sua comunicação

    Autor: Thalyson Luiz
"""
from mininet.topo import Topo
from mininet.util import irange
from mininet.net import Mininet
from mininet.log import setLogLevel
from mininet.cli import CLI
from string import *
import argparse

#Classe de criação de topologia padrão mininet
"""class SingleSwitchTopo(Topo):
    "Single switch connected to n hosts."
    def __init__(self, n=2, **opts):
        # Initialize topology and default options
        Topo.__init__(self, **opts)
        switch = self.addSwitch('s1')
        # Python's range(N) generates 0..N-1
        for h in irange(1, n):
            host = self.addHost('h%s' % h)
            self.addLink(host, switch)
"""

class NumRadiosException(Exception): pass


#Classe da topologia wi-fi, cria apenas hosts para a rede.
class MeshTopo(Topo):
    "Cria n hosts."
    def __init__(self, n=2, **opts):
        # Initialize topology and default options
        Topo.__init__(self, **opts)
        # Função mininet irange(X, N) gera números X..N
        for h in irange(1, n):
            self.addHost('h%s' % h)

#Função que passado um nome de host, retorna seu pid de processo.
def pid(name):
    "Retorna o pid de um host."
    x = 0
    for h in range(len(hosts)):
        if hosts[h].name == name:
            x = h
            break
    return hosts[x].pid

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'WifiVirtNet.')

    parser.add_argument('--radios', action = 'store', dest = 'radios',
                           default = '2', required = False,
                           help = 'Número de hosts criados.')
    
    arguments = parser.parse_args()

    radios = int(arguments.radios)
    
    if radios < 2:
        raise NumRadiosException("Número de radios deve ser maior que 1!")

    # Tell mininet to print useful information
    setLogLevel('info')

    topo = MeshTopo(n=radios)
    net = Mininet(topo)
    net.start()

    #hosts é um vetor com todos os hosts criados para a rede
    hosts = net.hosts

    #c0 recebe o controlador da rede
    c0 = net.controllers[0]

    try:
        #carrega o módulo de criação de interfaces wi-fi mac80211_hwsim encontra o pid dos hosts
        c0.cmdPrint('modprobe mac80211_hwsim')
        pid1 = pid('h1')
        pid2 = pid('h2')

        #Trasfere as interfaces para cada host
        iw1 = 'iw phy phy0 set netns '+str(pid1)
        iw2 = 'iw phy phy1 set netns '+str(pid2)
        c0.cmdPrint(iw1)
        c0.cmdPrint(iw2)

        #Cria interfaces 802.11s vinculadas as interfaces wi-fi
        hosts[0].cmdPrint('iw dev wlan0 interface add mesh0 type mp mesh_id teste')
        hosts[1].cmdPrint('iw dev wlan1 interface add mesh0 type mp mesh_id teste')

        #Configura as interfaces 802.11s
        hosts[0].cmdPrint('ifconfig mesh0 10.1.1.1')
        hosts[1].cmdPrint('ifconfig mesh0 10.1.1.2')
        #hosts[0].cmdPrint('iw dev mesh0 station dump')
        #hosts[1].cmdPrint('iw dev mesh0 station dump')

        #Retorna as configurações dos hosts e do controlador
        hosts[0].cmdPrint('ifconfig -a')
        hosts[1].cmdPrint('ifconfig -a')
        c0.cmdPrint('ifconfig -a')
    except Exception,e:
        #c0.cmdPrint('modprobe -r mac80211_hwsim')
        net.stop()
        #print "Erro:",e
        raise
    else:
        #Parte que será implementada para a adição de novos comandos
        """while True:
            param = raw_input("MeshVi> ")
            params = param.split()

            if params[0] == "pid":
                print "pid %s: %d "% (str(params[1]), pid(params[1]))
                #print "Pegar Pid"
                #for h in range(len(hosts)):
                # print(hosts[h].pid)
            if param == "exit":
                break
            #print "Testing network connectivity"
            #net.pingAll()
        """
        try:
            #Linha de comnado mininet
            CLI(net)
            #c0.cmdPrint('modprobe -r mac80211_hwsim')
            net.stop()
        except Exception,e:
            #c0.cmdPrint('modprobe -r mac80211_hwsim')
            net.stop()
            #print "Erro:",e
            raise
