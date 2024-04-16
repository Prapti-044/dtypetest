class A:
    pass

class B:
    pass

class C(A):
    pass


def fun1(x):
    print(x)

def fun2(x):
    print(x)
    return x
    

fun1(A())
fun2(B())

fun1(fun2(C()))

fun1(5)