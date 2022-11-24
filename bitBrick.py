import bencodepy
import hashlib
import secrets
import string

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
    sequence = string.ascii_letters + string.digits
    randStr = ''.join(secrets.choice(sequence) for i in range(12))
    peerId = f"-BB0001-{randStr}"

def downloadTorrent(path):
    info, announce = decodeTorrent(path)
    req = makeRequest(info, announce)

torrent_path = input("What is path to torrent? ")

downloadTorrent(torrent_path)