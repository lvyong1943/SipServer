#!/usr/bin/env python3

import sys
import socket
import subprocess
import time
import platform
import argparse

def test(testFunction):
    resultTest = testFunction()
    print("\n{0} is {1}passed\n".format(testFunction.__name__,'' if resultTest else 'NOT '))
    return resultTest

def portListening():
    if DEBUG:
        print(sys._getframe().f_code.co_name)
    command = [path, '-p', port]
    result = subprocess.Popen(command, stdout=subprocess.PIPE)
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    time.sleep(0.1)
    messages = ['Hello', 'World', 'q']
    if DEBUG:
        for m in messages:
            print('< ', m)
    for m in messages:
        clientSocket.sendto(m.encode(), serverEndPoint)
    stdoutResult = [x.decode() for x in result.stdout]
    if DEBUG:
        for r in stdoutResult:
            print('> ', r[:-1])
    if all(any(r.find(m) != -1 for r in stdoutResult) for m in messages):
        return True
    return False

def portListeningMultiConnection():
    if DEBUG:
        print(sys._getframe().f_code.co_name)
    command = [path, '-p', port]
    result = subprocess.Popen(command, stdout=subprocess.PIPE)
    time.sleep(0.1)
    messages = ['Hello', 'World', 'q']
    amountClients = 3
    sockets = [socket.socket(socket.AF_INET, socket.SOCK_DGRAM) for _ in range(amountClients)]
    for m in messages:
        for sock in sockets:
            if DEBUG:
                print('< ', m)
            sock.sendto(m.encode(), serverEndPoint)
    stdoutResult = [x.decode() for x in result.stdout]
    if DEBUG:
        for r in stdoutResult:
            print('> ', r[:-1])
    if all(all(any(r.find(m) != -1 for r in stdoutResult) for m in messages) for s in sockets):
        return True
    return False

def portListeningUsedPort():
    if DEBUG:
        print(sys._getframe().f_code.co_name)
    usedSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    usedSocket.sendto("q".encode(), serverEndPoint)
    usedPort = usedSocket.getsockname()[-1]

    command = [path, '-p', str(usedPort)]
    result = subprocess.Popen(command, stdout=subprocess.PIPE)
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    time.sleep(0.1)
    messages = ['Hello', 'World', 'q']
    if DEBUG:
        for m in messages:
            print('< ', m)
    for m in messages:
        clientSocket.sendto(m.encode(), serverEndPoint)
    return result.returncode != 0

def portListeningUnavailablePort():
    if DEBUG:
        print(sys._getframe().f_code.co_name)
    osType = platform.system()
    if DEBUG:
        print("OS is", osType)
    if osType != 'Linux':
        return True
    command = [path, '-p', '54']
    result = subprocess.Popen(command, stdout=subprocess.PIPE)
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    time.sleep(0.1)
    return result.returncode != 0

def portListeningSpecificInterface():
    if DEBUG:
        print(sys._getframe().f_code.co_name)
    networkInterface ='192.168.64.100'
    endPoint = (networkInterface, serverEndPoint[1])
    print(endPoint)
    command = [path, '-p', port, '-n', networkInterface]

    result = subprocess.Popen(command, stdout=subprocess.PIPE)
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    time.sleep(0.1)
    messages = ['Hello', 'World', 'q']

    if DEBUG:
        for m in messages:
            print('< ', m)

    for m in messages:
        clientSocket.sendto(m.encode(), endPoint)


    stdoutResult = [x.decode() for x in result.stdout]

    if DEBUG:
        for r in stdoutResult:
            print('> ', r[:-1])

    return all(any(r.find(m) != -1 for r in stdoutResult) for m in messages)

def portListeningSpecificInterfaceUnavailable():
    if DEBUG:
        print(sys._getframe().f_code.co_name)
    command = [path, '-p', '0', '-n', '1.2.3.4']
    result = subprocess.Popen(command, stdout=subprocess.PIPE)
    time.sleep(0.1)
    return result.returncode != 0


def echoServer():
    if DEBUG:
        print(sys._getframe().f_code.co_name)
    command = [path, '-p', port]
    result = subprocess.Popen(command, stdout=subprocess.PIPE)
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    time.sleep(0.1)
    messages = ['Hello', 'World', 'q']
    if DEBUG:
        for m in messages:
            print('< ', m)
    for m in messages:
        clientSocket.sendto(m.encode(), serverEndPoint)

    data = [clientSocket.recv(len(m)).decode() for m in messages]
    if DEBUG:
        for d in data:
            print('> ', d)
    return data == messages

def echoMultiConnection():
    if DEBUG:
        print(sys._getframe().f_code.co_name)
    command = [path, '-p', port]
    result = subprocess.Popen(command, stdout=subprocess.PIPE)
    time.sleep(0.1)
    messages = ['Hello', 'World', 'q']
    amountClients = 3
    sockets = [socket.socket(socket.AF_INET, socket.SOCK_DGRAM) for _ in range(amountClients)]
    for m in messages:
        for sock in sockets:
            if DEBUG:
                print('< ', m)
            sock.sendto(m.encode(), serverEndPoint)

    data = [[sock.recv(len(m)).decode() for m in messages] for sock in sockets]
    if DEBUG:
        print("Data is", data)
    return all(d == messages for d in data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-a','--address', required='True', help='IP address')
    parser.add_argument('-p', '--port', required='True', help='Port of SipServer')
    parser.add_argument('-s', '--sipserver', required='True', help='Path to SipServer')
    parser.add_argument('-i', '--interface', help='Network interface')
    parser.add_argument('-l', '--loglevel', help='Logger level')
    args = parser.parse_args()

    address = args.address
    port = args.port
    path = args.sipserver
    interface = args.interface
    DEBUG = True if args.loglevel else False

    serverEndPoint = (address, int(port))
    print(address, port, path)
    test(portListening)
    test(portListeningMultiConnection)
    test(portListeningUnavailablePort)
    test(portListeningUsedPort)
    test(portListeningSpecificInterface)
    test(portListeningSpecificInterfaceUnavailable)
    test(echoServer)
    test(echoMultiConnection)
