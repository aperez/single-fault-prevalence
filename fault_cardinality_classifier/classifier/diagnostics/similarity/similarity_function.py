import math

def div(a, b):
    return a / b if b != 0.0 else 0.0

def ochiai(n):
    res = math.sqrt(n[1][1] + n[0][1]) * math.sqrt(n[1][1] + n[1][0])
    return div(n[1][1], res)

def naish(n):
    return n[1][1] + div(n[1][0], n[1][0] + n[0][0] + 1)

def o(n):
    if n[0][1] > 0:
        return -1.0
    else:
        return n[0][0]

def tarantula(n):
    num = div(n[1][1], n[1][1] + n[0][1])
    denum = num + div(n[1][0], n[1][0] + n[0][0])
    return div(num, denum)

def dstar(star=2.0):
    def f(n):
        return div(pow(n[1][1], star), n[0][1] + n[1][0])
    return f
