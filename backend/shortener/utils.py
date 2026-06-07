import random

BASE62_ALPH = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
CODE_LENGTH = 7

def encode_to_b62(num: int) -> str:
    #encodes a non negative integer to a base62 string, 
    #int becase ascii

    if num==0:
        return BASE62_ALPH[0]
    result = []
    while num:
        num, remainder = divmod(num, 62)
        result.append(BASE62_ALPH[remainder])
    
    return "".join(reversed(result))

def gen_short_code() -> str:
    #gen a random codelength b62 string
    
    num = random.randint(0, 62**CODE_LENGTH - 1)
    code = encode_to_b62(num)

    #pad the left side with 0 to keep the length consistent
    return code.zfill(CODE_LENGTH)
