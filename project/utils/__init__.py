def get_tasks():
    from requests import get
    data = get("http://localhost:5555/api/tasks?result").json()
    return list(data.keys())


def get_hash_of_file(_file, blocksize=1024):
    from hashlib import md5
    with open(_file, 'rb') as fp:
        buf = fp.read(blocksize)
        res = md5(buf)
        while len(buf) > 0:
            res.update(buf)
            buf = fp.read(blocksize)
    return res.hexdigest()
