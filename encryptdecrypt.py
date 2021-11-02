import os
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Hash import SHA256

chunks = 32*1024


def encstring(data, key):
    data = data.encode("utf-8")
    filesz = str(len(data)).zfill(16).encode("utf-8")
    IV = Random.new().read(16)
    encrypter = AES.new(key, AES.MODE_CFB, IV)
    outdata = b''
    i = 0
    while True:
        temdata = data[0+chunks*i: chunks+chunks*i]
        if len(temdata) == 0:
            break
        if len(temdata)%16 != 0:
            temdata += b' ' * (16-len(temdata))
        outdata += encrypter.encrypt(temdata)
        i = i+1
    return (filesz, IV, outdata)


def keyfrompas(pas):
    return SHA256.new(pas.encode("utf-8")).digest()



def writetofile(dir, fname, length, IV, tdata):
    with open(os.path.join(dir, fname), 'wb') as fo:
        fo.write(length)
        fo.write(IV)
        fo.write(tdata)


def decryptfile(dir, filename, key):
    with open(os.path.join(dir, filename), "rb") as fin:
        fz = int(str(fin.read(16) , "utf-8"))
        IV = fin.read(16)
        decrypter = AES.new(key, AES.MODE_CFB, IV)
        outdata = b""
        while True:
            temdata = fin.read(chunks)
            if(len(temdata) == 0):
                break
            outdata += decrypter.decrypt(temdata)
        outdata = outdata[0:fz]
        return outdata


if __name__ == '__main__':
    k = keyfrompas("abc")
    a = encstring("asdfaushiauhsdfoigashfpuiaidfuhda0ßsd",keyfrompas("abc"))
    decryptfile("data", "l1.txt",k)