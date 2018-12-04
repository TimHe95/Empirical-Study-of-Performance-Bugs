# https://blog.csdn.net/zhongbeida_xue/article/details/78679601
import pexpect

import sys

print (sys.argv[0])
print (sys.argv[1])

print (int(sys.argv[1]))
try:
	print (int('ff'))
except Exception as e:
	print ('please give a number.')

'''
child = pexpect.spawn("/usr/local/mysql/bin/mysqladmin drop sbtest")
child.timeout = 10
if child.expect_exact([pexpect.TIMEOUT, '[y/N]']) == 0:
	child.kill(0)
child.sendline('y')
child.wait() # child.interact() or child.read()
'''