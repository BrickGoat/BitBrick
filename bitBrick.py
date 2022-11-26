import bencodepy
import urllib.parse
import hashlib
import secrets
import string
import time
import math
import socket, struct

def decodeTorrent(path):
    metaInfo = bencodepy.Bencode(dict_ordered=True).read(path)
    info = metaInfo[b'info']
    announce_url = metaInfo[b'announce'].decode('UTF-8')
    
    announce_urls = []
    for announce_url in metaInfo[b'announce-list']:
        url = announce_url[0].decode()
        if url[0:3] == "udp":
            begin = str(url).rindex("/") + 1
            end = str(url).rindex(":")
            name = url[begin:end]
            port = url[end+1:len(url)]
            announce_urls.append((name, int(port)))
    return info, announce_urls

def makeAnnounceRequest(info, announce_urls):
    h = hashlib.sha1()
    encodedInfo = bencodepy.encode(info)
    h.update(encodedInfo)
    infoHash = h.digest()
    infoHash = bytes(urllib.parse.quote(infoHash), 'utf-8')
    sequence = string.ascii_letters + string.digits
    randStr = ''.join(secrets.choice(sequence) for i in range(12))
    peerId = bytes(f"-BB0001-{randStr}", 'utf-8')
    
    for i in range(len(announce_urls)):
        name = announce_urls[i][0] 
        port = announce_urls[i][1]
        connection_packet, trans_id = getConnectPack()
        resp = makeUdpConnection(name, port, connection_packet)
        #print(resp)
        if resp is None or readConnectionResp(resp, trans_id) is None:
            #announce_urls.pop(i)
            continue
        connection_id = readConnectionResp(resp, trans_id)

def getConnectPack():
    protocol_id = 0x41727101980
    action = 0
    sequence = string.digits
    trans_id = ''.join(secrets.choice(sequence) for i in range(4))
    return struct.pack(">QII", protocol_id, action, int(trans_id)), trans_id

def readConnectionResp(resp, id):
    action, trans_id, connect_id = struct.unpack(">IIQ", resp)
    print(action)
    print(f"t: {int(trans_id)}, t_: {int(id)}")
    if action == 0 and int(trans_id) == int(id):
        return connect_id
    return None

def makeUdpConnection(name, port, packet):
    buffSize = 4096
    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    n = 0
    while n < 3:
        try:
            timeout = 15 * math.pow(2, n)
            print(timeout)
            UDPClientSocket.settimeout(timeout)
            n = n + 1
            print((name, port))
            UDPClientSocket.sendto(packet, (name, port))
            resp = UDPClientSocket.recvfrom(buffSize)
            return resp[0]
        except Exception as e:
            print(e)
    return None
    

def downloadTorrent(path):
    info, announce_urls = decodeTorrent(path)
    #print(announce_urls)
    req = makeAnnounceRequest(info, announce_urls)

downloadTorrent("./big-buck-bunny.torrent")
