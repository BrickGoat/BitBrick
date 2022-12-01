import bencodepy
import urllib.parse
import hashlib
import secrets
import string
import math
import socket, struct

# Main function
def downloadTorrent(path):
    info, announce_urls, length = decodeTorrent(path)
    req = makeAnnounceRequest(info, [('tracker.opentrackr.org', 1337)], length)

# Decode bencoded torrent file and return info key, list of udp trackers, and total size of files
def decodeTorrent(path):
    metaInfo = bencodepy.Bencode(dict_ordered=True, dict_ordered_sort=True).read(path)
    info = metaInfo[b'info']
    announce_list = metaInfo[b'announce-list']
    length = 0
    if "length" in info.keys(): # single file torrent
        length = info[b'length']
    else:
        for fileDict in info[b'files']: # Multiple files
            length += fileDict[b'length']
    announce_urls = []
    for announce_url in announce_list:
        url = announce_url[0].decode()
        if url[0:3] == "udp":
            begin = str(url).rindex("/") + 1
            end = str(url).rindex(":")
            name = url[begin:end]
            port = url[end+1:len(url)]
            announce_urls.append((name, int(port)))
    return info, announce_urls, length

"""
    Orchestrates calls to other function in order to request connection id from tracker 
    then make announcement in order to get list of peers
     - Currently the announcement only returns my own information? 
"""
def makeAnnounceRequest(info, announce_urls, length):
    # Bencode the info key then create a sha1 hash of it before url encoding it and converting it back to bytes
    h = hashlib.sha1()
    encodedInfo = bencodepy.encode(info)
    h.update(encodedInfo)
    infoHash = h.hexdigest()
    infoHash = urllib.parse.quote_plus(infoHash).encode('UTF-8')
    # Create the peerId
    sequence = string.ascii_letters + string.digits
    randStr = ''.join(secrets.choice(sequence) for i in range(12))
    peerId = bytes(f"-BB0001-{randStr}", 'utf-8')
    # Attempt to make a connection with each tracker
    for i in range(len(announce_urls)):
        name = announce_urls[i][0] 
        port = announce_urls[i][1]
        # Create conncection packet and retrieve connection id
        connection_packet, trans_id = getConnectPack()
        resp = sendUdpPacket(name, port, connection_packet)
        if resp is None or readConnectionResp(resp, trans_id) is None:
            continue
        connection_id = readConnectionResp(resp, trans_id)
        # Create announcement packet and retrieve peer list
        announcement_pack = getAnnouncePack(connection_id, infoHash, peerId, trans_id=trans_id, left=length)
        url = announce_urls.pop(i)
        announce_urls.insert(0, url)
        for i in range(len(announce_urls)):
            name = announce_urls[i][0] 
            port = announce_urls[i][1]
            resp = sendUdpPacket(name, port, announcement_pack)
            if resp is None or readAnnounceResp(resp, trans_id) is None:
                continue
            peers = readAnnounceResp(resp, trans_id)
            print(peers)
            raise Exception("Placeholder")

# Creates udp tracker connection packet
def getConnectPack():
    protocol_id = 0x41727101980
    action = 0
    sequence = string.digits
    trans_id = ''.join(secrets.choice(sequence) for i in range(4))
    return struct.pack(">QII", protocol_id, action, int(trans_id)), trans_id

# Creates udp tracker announcement packet
def getAnnouncePack(connection_id, info_hash, peer_id, trans_id=None, left =0, uploaded=0,  downloaded=0, event=2):
    sequence = string.digits
    action = 1
    if trans_id is None:
        trans_id = ''.join(secrets.choice(sequence) for i in range(4))
    key = ''.join(secrets.choice(sequence) for i in range(4))
    return struct.pack(">QII20s20sQQQIIIiH", connection_id, action, int(trans_id), info_hash, peer_id, downloaded, left, uploaded, event, 0, int(key), -1, 6881)

# Returns connection id if tracker response is valid else None
def readConnectionResp(resp, id):
    action, trans_id, connect_id = struct.unpack(">IIQ", resp)
    if action == 0 and int(trans_id) == int(id):
        return connect_id
    return None

# Returns peerlist from announcement response
def readAnnounceResp(resp, id):
    peerList = []
    action, trans_id = struct.unpack(">II", resp[:8])
    if action != 1 or int(trans_id) != int(id):
        if action == 3: # if error, print error msg
            print(resp[8:])
        return None
    # valid response, read variable amount of peers from rest of response packet
    peers = resp[20:]
    peerLen = 6
    peerCount = int(len(peers)/6)
    print(peerCount)
    for i in range(peerCount):
        offset = i * peerLen
        peerDict = {}
        peerDict["ip"], peerDict["port"] = struct.unpack(">IH", peers[offset:offset+6])
        peerDict["ip"] = socket.inet_ntoa(struct.pack(">I", peerDict["ip"]))
        peerList.append(peerDict)
    return peerList
    
# send udp packet to (name, port) destination, retry connection based on bittorent specification
def sendUdpPacket(name, port, packet):
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
            UDPClientSocket.close()
            return resp[0]
        except Exception as e:
            print(e)
    return None
    

downloadTorrent("./cosmos-laundromat.torrent")
