import bencodepy

def decodeTorrent(path):
    metaInfo = bencodepy.Bencode().read(path)
    info = metaInfo[b'info']
    announce_url = metaInfo[b'announce'].decode('UTF-8')
    return info, announce_url

def downloadTorrent(path):
    info, announce = decodeTorrent(path)

torrent_path = input("What is path to torrent? ")

downloadTorrent(torrent_path)