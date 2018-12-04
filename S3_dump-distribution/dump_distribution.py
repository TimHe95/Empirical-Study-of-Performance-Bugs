import mysql.connector
import numpy as np
import os, shutil

from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
#
# you may change the following parameters :
#

concerned_parameters = ['`--table-size`',
                        '`--threads`',
                        '`--innodb-buffer-pool-size`',
                        '`--innodb-log-buffer-size`'] # 'distributions(buffer-log-related)'
                        # warn: parameters in this constraint are supposed to not appear concerned_parameters.
additional_constraint = 'AND `--point-selects`=100 AND `--index-updates`=100 AND `--delete-inserts`=100'
'''
concerned_parameters = ['`--table-size`', 
                        '`--threads`',
                        '`--innodb-buffer-pool-size`',
                        '`--innodb-change-buffer-max-size`',
                        '`--innodb-change-buffering`'] # 'distributions(buffer-related)'

concerned_parameters = ['`--table-size`', 
                        '`--innodb-commit-concurrency`', 
                        '`--threads`',
                        '`--innodb-thread-concurrency`',
                        '`--innodb-concurrency-tickets`'] # 'distributions(concurrency-related)'
'''
concerned_perf_metic = '`Avg_Latency(ms)`'
TB_NAME = 'oltp_read_write_test_5'              # you have to change this to the right table.
DB_NAME = 'mariadb_perf_test'
distribution_dir = 'distributions(log-buffer-related)'
data4MLtrain_dir = 'RawData4MLtrain'
fig_dpi = 200                                   # the higher the better definition of the figure.
clean_start = False                              # if set to False, make sure that you won't get any conflicts of directories.

#
# you are not supposed to change anything below
#
concerned_params_range = {} # values with ''
concerned_params_range_raw = {} # values witout ''


# make sure we are working on an empty directory
if clean_start:
    trashes = os.listdir('.')
    for trash in trashes:
        if os.path.isdir(trash):
            shutil.rmtree(trash)
        else:
            os.remove(trash)

# if an additional_constraint is given, we will work on an subdirectory instead.
if additional_constraint != '':
    os.mkdir(additional_constraint)
    os.chdir(additional_constraint)


os.mkdir(distribution_dir)
os.mkdir('%s/%s'%(distribution_dir, data4MLtrain_dir))

def enum_to_number(r, p):
    try:
        float(r)
        res = r
    except ValueError as ve:
        res = concerned_params_range_raw[p].index(r) + 1
    return res

def enumlist_to_numberlist(l, p):
    for i in range(len(l)):
        l[i] = enum_to_number(l[i], p)

def try_to_num(e):
    try:
        res = int(e.strip('\''))
    except ValueError as ve:
        res = e
    return res

def all_combine(all_sqls, half_sql, rest_params, extra_constraint):
    #print(rest_params)
    if len(rest_params) == 0 :
        #print ('==%s'%half_sql)
        all_sqls.append('%s %s'%(half_sql, extra_constraint))
    else:
        tmp = rest_params.copy()
        cur_param = tmp.pop()
        for value in concerned_params_range[cur_param] :
            all_combine(all_sqls, '%sAND %s = %s '%(half_sql, cur_param, value), tmp, extra_constraint)

def matix2str(m):
    res = str(m)
    res = res.replace('], [','\n').translate(str.maketrans('[],','   ')).strip()
    return res + '\n'



cnx = mysql.connector.connect(user='root', password='19950130hhc', host='localhost', database=DB_NAME)
cursor = cnx.cursor()


for i in range(len(concerned_parameters)):
    q1 = 'SELECT DISTINCT %s FROM %s.%s'%(concerned_parameters[i], DB_NAME, TB_NAME)
    cursor.execute(q1)
    v_set = []
    v_set_raw = []
    for v in cursor:
        v_set.append('\'%s\''%v[0])
        v_set_raw.append(v[0])
    v_set.sort(key=try_to_num)
    v_set_raw.sort()
    concerned_params_range[concerned_parameters[i]] = v_set
    concerned_params_range_raw[concerned_parameters[i]] = v_set_raw
#print(concerned_params_range)


count = 1;
for i in range(len(concerned_parameters)-1):
    for j in range(i+1, len(concerned_parameters)):

        cur_dir = '%s/%s&&%s'%(distribution_dir, concerned_parameters[i], concerned_parameters[j])
        if os.path.exists(cur_dir):
            shutil.rmtree(cur_dir)
        os.mkdir(cur_dir)

        # ------------------------------- 1st part of the SQL -------------------------------
        q1 = 'SELECT DISTINCT %s, %s, %s FROM %s.%s WHERE 1=1 '%(concerned_parameters[i], concerned_parameters[j], concerned_perf_metic, DB_NAME, TB_NAME)
        
        # ------------------------------- 2nd part of the SQL -------------------------------
        tmp = concerned_parameters.copy()
        if i<j:
            tmp.remove(tmp[j])
            tmp.remove(tmp[i])
        elif i>j:
            tmp.remove(tmp[i])
            tmp.remove(tmp[j])
        #print ('--------%s'%tmp)
        all_sqls = [] # all possible SQLs in this params-combination
        all_combine(all_sqls, q1, tmp, additional_constraint)

        # ------------------------------- execute all SQLs -------------------------------
        for sql in all_sqls:
            if count % 100 == 0:
                print ('[NOTE] %d distributions finished'%count)

            # ------------------------------- for drawing -------------------------------
            x_range = len(concerned_params_range[concerned_parameters[i]])              #|
            y_range = len(concerned_params_range[concerned_parameters[j]])              #|
            val =  [[0] * y_range for row in range(x_range)]                            #|
            X = []                                                                      #|
            Y = []                                                                      #|
            Z = []                                                                      #|
            fig = plt.figure(figsize=plt.figaspect(0.25))                               #|
            ax0 = fig.add_subplot(1, 3, 1, projection='3d')                             #|
            ax1 = fig.add_subplot(1, 3, 2, projection='3d')                             #|
            ax2 = fig.add_subplot(1, 3, 3, projection='3d')                             #|
            # ---------------------------------------------------------------------------

            f = open('%s/distribution_%d.txt'%(cur_dir, count), 'w')
            
            f.write('%s\n'%sql)
            f.write('%s\t%s\t%s\n'%(concerned_parameters[i], concerned_parameters[j], concerned_perf_metic))
            cursor.execute(sql)
            for r1, r2, v in cursor:
                f.write(('%s\t%s\t%s\n')%(r1,r2,v))

                rr1 = enum_to_number(r1, concerned_parameters[i])
                rr2 = enum_to_number(r2, concerned_parameters[j])

                X.append(rr1)
                Y.append(rr2)
                Z.append(v)
                val[concerned_params_range[concerned_parameters[i]].index('\'%s\''%r1)][concerned_params_range[concerned_parameters[j]].index('\'%s\''%r2)] = v
            
            # --------------------------------------- for drawing ---------------------------------------
            X_s = np.array(X, dtype=float)                                                              #|
            Y_s = np.array(Y, dtype=float)                                                              #|
            Z_s = np.array(Z, dtype=float)                                                              #|
            ax0.scatter(X_s, Y_s, Z_s, color='b') # 散点图                                               #|
                                                                                                        #|
            tmpX = concerned_params_range_raw[concerned_parameters[i]].copy()                           #|
            tmpY = concerned_params_range_raw[concerned_parameters[j]].copy()                           #|
            enumlist_to_numberlist(tmpX, concerned_parameters[i])                                       #|
            enumlist_to_numberlist(tmpY, concerned_parameters[j])                                       #|
            X_array = np.array(tmpX, dtype=float)                                                       #|
            Y_array = np.array(tmpY, dtype=float)                                                       #|
            Z_matix = np.array(val).T                                                                   #|
                                                                                                        #|
            # ---------------------------------------------------------------------------               #|
            mlf = open('%s/%s/%s'%(distribution_dir, data4MLtrain_dir, count), 'w')     #|
            mlf.write(matix2str(tmpX))                                                  #|
            mlf.write(matix2str(tmpY))                                                  #|
            mlf.write(matix2str(val))                                                   #|
            mlf.close()                                                                 #|
            # ---------------------------------------------------------------------------               #|
                                                                                                        #|
            X_array, Y_array = np.meshgrid(X_array, Y_array)                                            #|
            for a in range(y_range-1, -1, -1) :                                                         #|
                ax1.plot(X_array[0], Y_array[a], Z_matix[a]) # 折线图1                                   #|
                                                                                                        #|
            for b in range(x_range) :                                                                   #|
                ax2.plot(X_array.T[b], Y_array.T[0], Z_matix.T[b]) # 折线图2                             #|
                                                                                                        #|
            ax0.set_xlabel(concerned_parameters[i])                                                     #|
            ax0.set_ylabel(concerned_parameters[j])                                                     #|
            ax1.set_xlabel(concerned_parameters[i])                                                     #|
            ax1.set_ylabel(concerned_parameters[j])                                                     #|
            ax2.set_xlabel(concerned_parameters[i])                                                     #|
            ax2.set_ylabel(concerned_parameters[j])                                                     #|
            #plt.xlabel('add label here')                                                               #|
            #plt.ylabel('add label here')                                                               #|
                                                                                                        #|
            fig.suptitle(sql[sql.find('WHERE 1=1 AND')+len('WHERE 1=1 AND'):])                          #|
            # ax.set_title('add title here')                                                            #|
            # ax.set_title('add title here')                                                            #|
                                                                                                        #|
            plt.savefig('%s/distribution_%d.png'%(cur_dir, count), dpi = fig_dpi)                       #|
            # -------------------------------------------------------------------------------------------

            f.close()
            count += 1

cursor.close()
cnx.close()
