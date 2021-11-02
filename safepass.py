import secrets
import string


def safepas(n = 60):
    chars = string.digits + string.ascii_letters + string.punctuation
    chars = chars.replace('#','')
    chars = chars.replace('"','')
    return ''.join(secrets.choice(chars) for _ in range(40))

if __name__ == "__main__":
    pass
    #print(safepas())