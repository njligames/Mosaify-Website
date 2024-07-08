import platform

def isDarwin():
    return "Darwin" == platform.uname().system

def isLinux():
    return "Linux" == platform.uname().system

