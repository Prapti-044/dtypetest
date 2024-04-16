a = 10
b = 'hello'

def fun1(x: int):
	print(x)
	
def fun2(y):
	hello = 5
	fun1(y)
	y = 10
	
def main():
	a = 20
	fun2(a)
	fun2(b)
	fun1(10)
	fun1(fun2(10))