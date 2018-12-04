import pexpect
import os
import commands
import time

mariadb_user = 'root'
mariadb_socket = '/tmp/mysql.sock'
sysbench_lua_prefix = '/usr/local/share/sysbench/'
mariadb_prefix = '/usr/local/mysql/'
mariadb_sample_result = '4_4.txt' # model file
wkld_separator = '--innodb' # symbol for the first wkld-param. prefix
parameter_stop_words = ['nil', '-1']

mariadb_file = open(mariadb_sample_result, 'r')
mariadb_lines = mariadb_file.readlines()
mariadb_head = mariadb_lines[0].strip().split('\t')
mariadb_body = mariadb_lines[1:]

shutdown_cmd = '%sbin/mysqladmin shutdown'%mariadb_prefix
ping_cmd = '%sbin/mysqladmin ping'%mariadb_prefix
create_db_cmd = '%sbin/mysqladmin create sbtest'%mariadb_prefix
drop_db_cmd = '%sbin/mysqladmin drop sbtest'%mariadb_prefix


def perform_drop_db():
	child = pexpect.spawn(drop_db_cmd)
	child.timeout = 10
	index = child.expect_exact([pexpect.TIMEOUT, '[y/N]'])
	if index == 0:
		child.kill(0)
	elif index == 1:
		child.sendline('y')
		child.wait() # child.interact() or child.read()
		print ('[%s] DB: \'sbtest\' dropped.'%(time.strftime("%Y-%m-%d %H:%M:%S")))
	return


separate_loc = 0
for param in mariadb_head:
	if wkld_separator in param:
		break
	separate_loc += 1
if separate_loc == 0:
	print ('wkld_separator error.')
	exit(0)

wkld_head = mariadb_head[0:separate_loc]
conf_head = mariadb_head[separate_loc:]

sample_count = 0
sample_total = len(mariadb_body) 
for mariadb_line in mariadb_body:
	sample_count += 1
	mariadb_params = mariadb_line.strip().split('\t')
	
	# ---------------- for sysbench cmdline ----------------
	wkld_params = mariadb_params[0:separate_loc]

	# for connection parameters
	sysbench_cmd = 'sysbench %s%s'%(sysbench_lua_prefix, wkld_params[0])
	sysbench_cmd = '%s --mysql-socket=%s --mysql-user=%s'%(sysbench_cmd, mariadb_socket, mariadb_user)
	
	# for workload parameters
	for i in range(1, len(wkld_params)): # wkld_params[0] is 'sysbench'
		if wkld_params[i] in parameter_stop_words:
			continue
		sysbench_cmd = '%s %s=%s' % (sysbench_cmd, wkld_head[i] , wkld_params[i])
	sysbench_cmd = sysbench_cmd + ' --mysql-ignore-errors=all --time=10  --forced-shutdown=5'

	sysbench_prepare = sysbench_cmd + ' prepare'
	sysbench_warmup = sysbench_cmd + ' warmup'
	sysbench_run = sysbench_cmd + ' run'

	# ---------------- for mysqld cmdline ----------------
	conf_params = mariadb_params[separate_loc:]

	mysqld_cmd = '%sbin/mysqld_safe '%mariadb_prefix
	for j in range(0, len(conf_params)):
		if conf_params[j] in parameter_stop_words:
			continue
		mysqld_cmd = '%s %s=%s' % (mysqld_cmd, conf_head[j], conf_params[j])
	mysqld_cmd = mysqld_cmd + ' --innodb-log-file-size=200M --thread-concurrency=2000 &' # run background

	# ---------------- run this sample ----------------
	print ('************** Case [%d/%d] **************'%(sample_count, sample_total))
	ddl = 0
	next_sample = False
	os.system(mysqld_cmd) # start mysqld
	while (commands.getstatusoutput(ping_cmd)[0]):
		time.sleep(0.1)
		ddl += 1
		if ddl > 100:
			next_sample = True
			break
	if next_sample == True:
		print ('[%s] mysqld start timeout, next sample.'%(time.strftime("%Y-%m-%d %H:%M:%S")))
		continue # next sample
	print ('[%s] mysqld started!'%(time.strftime("%Y-%m-%d %H:%M:%S")))


	if (commands.getstatusoutput(create_db_cmd)[0]):
		print ('[%s] DB: \'sbtest\' exists, recreate it.'%(time.strftime("%Y-%m-%d %H:%M:%S")))
		perform_drop_db()
		if (0 == commands.getstatusoutput(create_db_cmd)[0]):
			print ('\trecreat OK.')
	else :
		print ('[%s] DB: \'sbtest\' created.'%(time.strftime("%Y-%m-%d %H:%M:%S")))


	print ('[%s] preparing data...'%(time.strftime("%Y-%m-%d %H:%M:%S")))
	prep_res = commands.getstatusoutput(sysbench_prepare)
	if prep_res[0] == 0 :
		print ('\t--OK.')
	else:
		errlog = open('log/err_prep%s.txt'%sample_count, 'w')
		errlog.write(prep_res[1])
		errlog.close()
		print ('\t --not OK, see log/err_prep%s.txt for more INFO.'%sample_count)
		print ('[%s] Doing cleanning up.'%(time.strftime("%Y-%m-%d %H:%M:%S")))
		perform_drop_db()
		print ('[%s] One finished, shutting down mysqld.'%(time.strftime("%Y-%m-%d %H:%M:%S")))
		commands.getstatusoutput(shutdown_cmd)
		continue


	print ('[%s] warming up data...'%(time.strftime("%Y-%m-%d %H:%M:%S")))
	commands.getstatusoutput(sysbench_warmup)


	print ('[%s] running...'%(time.strftime("%Y-%m-%d %H:%M:%S")))
	run_res = commands.getstatusoutput(sysbench_run)
	if run_res[0] == 0 :
		print ('\t--OK :)')
	else :
		print ('\t--not OK :(')
	res_file = open('log/out_%s.txt'%sample_count, 'w')
	res_file.write(run_res[1])
	res_file.close() 


	print ('[%s] Doing cleanning up.'%(time.strftime("%Y-%m-%d %H:%M:%S")))
	perform_drop_db()


	print ('[%s] One finished, shutting down mysqld.'%(time.strftime("%Y-%m-%d %H:%M:%S")))
	commands.getstatusoutput(shutdown_cmd)


mariadb_file.close()


