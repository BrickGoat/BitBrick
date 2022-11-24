import bencodepy
import urllib.parse
import hashlib
import secrets
import string

def decodeTorrent(path):
    metaInfo = bencodepy.Bencode().read(path)
    info = metaInfo[b'info']
    announce_url = metaInfo[b'announce'].decode('UTF-8')
    begin = str(announce_url).rindex("/") + 1
    end = str(announce_url).rindex(":")
    name = announce_url[begin:end]
    port = announce_url[end+1:len(announce_url)]
    return info, name, port

def makeAnnounceRequest(info, name, port):
    h = hashlib.sha1()
    encodedInfo = bencodepy.encode(info)
    h.update(encodedInfo)
    infoHash = h.digest()
    sequence = string.ascii_letters + string.digits
    randStr = ''.join(secrets.choice(sequence) for i in range(12))
    peerId = f"-BB0001-{randStr}"


def makeUdpConnection(url):
    pass

def downloadTorrent(path):
    info, name, port = decodeTorrent(path)
    req = makeAnnounceRequest(info, name, port)

downloadTorrent("./big-buck-bunny.torrent")

torrent_path = input("What is path to torrent? ")

downloadTorrent(torrent_path)