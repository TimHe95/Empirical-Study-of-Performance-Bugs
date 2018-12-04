import re
import os 
import mysql.connector
from mysql.connector import errorcode

DB_NAME = 'mariadb_perf_test'
TB_NAME = 'oltp_read_write_test_5'
concerned_perf_metic = 'avg:'
param_combine_file = 'log-buffer-sample.data'
result_dir = 'log'

frame = open('frame', 'r')
column_names = frame.readline().strip().split('\t')
column_type = frame.readline().strip().split('\t')
frame.close()
#LFA90E83CE4B
#Z9F881A7D256
sql_create = ''
for i in range(len(column_names)):
    sql_create = '%s `%s` %s, '%(sql_create, column_names[i], column_type[i])
sql_create = '%s `Avg_Latency(ms)` double, `status` enum(\'success\',\'forced_ended\',\'run_failed\')'%(sql_create) # remove the last ','


TABLES = {}
TABLES[TB_NAME] = (
    'CREATE TABLE `%s` (%s) ENGINE=InnoDB'%(TB_NAME, sql_create))


def create_database(cursor):
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
    except mysql.connector.Error as err:
        print("[ERROR] Failed creating database: {}".format(err))
        exit(1)


# __________________________ connect __________________________ 

try:
	cnx = mysql.connector.connect(user='root', password='19950130hhc', host='localhost')
except mysql.connector.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("[ERROR] Wrong user name or password")
    exit(1)
  else:
    print(err)
    exit(1)

print("[NOTE] Mysql Connected.")
cursor = cnx.cursor()

# __________________________ db create __________________________ 
try:
    cursor.execute("USE {}".format(DB_NAME))
    print ("[NOTE] USE {}".format(DB_NAME))
except mysql.connector.Error as err:
    print("[WARN] Database {} does not exists.".format(DB_NAME))
    if err.errno == errorcode.ER_BAD_DB_ERROR:
        create_database(cursor)
        print("[NOTE] Database {} created successfully.".format(DB_NAME))
        cnx.database = DB_NAME
    else:
        print(err)
        exit(1)

# __________________________ table create __________________________ 
for table_name in TABLES:
    table_description = TABLES[table_name]
    try:
        print('[NOTE] Creating table {}: '.format(table_name), end='')
        cursor.execute(table_description)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print('table already exists.')
        else:
            print('\n[ERROR] %s'%err.msg)
    else:
        print('OK')

# __________________________ insert data __________________________ 
# which column to insert
sql_insert = ''
for i in range(len(column_names)):
    sql_insert = '%s`%s`, '%(sql_insert, column_names[i])
sql_insert = '%s`Avg_Latency(ms)`, `status`'%sql_insert

# param_combines part
ff = open(param_combine_file, 'r')
param_combines = ff.readlines()
ff.close()
# running_result part
prog = 0
try:
    for file in os.listdir(result_dir):

        if not len(re.findall('\d+', file)):
            continue

        s_id = int(re.findall('\d+', file)[0])
        tmp = param_combines[s_id-1].strip().split('\t')[1:]


        avg_latency = '0.0'
        res_file = open('%s/%s'%(result_dir, file), 'r')
        res_file_body = res_file.readlines()
        res_file.close()
        for line in res_file_body:
            if concerned_perf_metic in line:
                avg_latency = re.findall(r"\d+\.?\d*", line)[0]
                break
        tmp.append(avg_latency)

        status = 'success'
        if 'err' in file :
            status = 'run_failed'
        elif 'fail' in file :
            status = 'forced_ended'
        elif 'suc' in file :
            status = 'success'
        tmp.append(status)

        for j in range(len(tmp)):
            if tmp[j].lower() in ['on', 'true', 'yes'] :
                tmp[j] = 'true'
            elif tmp[j].lower() in ['off', 'false', 'no'] :
                tmp[j] = 'false'
            else:
                tmp[j] = '\'%s\''%tmp[j] # varchar, int, double, enum can all be insert in qouted format

        tmp = ','.join(tmp)

        add_record = ('INSERT INTO %s (%s) VALUES (%s)')%(TB_NAME, sql_insert, tmp)
        # print (add_record)
        cursor.execute(add_record)

        prog += 1
        if prog % 100 == 0:
            print ('[NOTE] %d records inserted.'%prog)

except Exception as e:
    print ('[ERROR] %s\n%s'%(file, add_record))
    exit(0)

print ('[NOTE] Committing records...')
cnx.commit()
print ('DONE.')
cursor.close()
cnx.close()