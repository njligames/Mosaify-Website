import platform

def isDarwin():
    return "Darwin" == platform.uname().system
