import bencodepy
import hashlib

def decodeTorrent(path):
    metaInfo = bencodepy.Bencode().read(path)
    info = metaInfo[b'info']
    announce_url = metaInfo[b'announce'].decode('UTF-8')
    return info, announce_url

def makeRequest(info, announce):
    h = hashlib.sha1()
    encodedInfo = bencodepy.encode(info)
    h.update(encodedInfo)
    infoHash = h.digest()
    

def downloadTorrent(path):
    info, announce = decodeTorrent(path)
    req = makeRequest(info, announce)

torrent_path = input("What is path to torrent? ")

downloadTorrent(torrent_path)