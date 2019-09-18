# GCC/Clang 测试脚本使用方法

### Step 1

复制benchmark文件到某个目录‘/dir/to/benchmarks’

> 所谓的benchmark文件，一般是独立的c/c++文件，例如tramp3d-v4.cpp；有时是一个工程，需要用make来编译，此时可以选择评估用gcc/g++/clang/clang++单独编译其中每个源码文件的时间，或者make整个工程的时间（如此，建议不使用本脚本，直接运行：`time make CFLAGS="-O0 -march=native"`，其中-O0部分手动改成-O1/-O2...）。

### Step 2

运行：

`python PerfTest_c-compiler.py <c/c++_compiler_name> 
</dir/to/benchmarks> <repeats>`

* `<c/c++ compiler name>` gcc g++ clang clang++ 或其他
* `</dir/to/benchmarks>` benchmark目录
* `<repeats>` [1,∞)重复次数，性能测试一般要多次重复取平均/中位才能保证结果可信

### Step 3

在当前目录下，会有运行结果，其中log.err文件是benchmark中，一些无法编译的c/c++源码。'[Result]'开头的文件则是测试结果，点开后即懂

# MySQL/MariaDB 测试脚本使用方法

> 注：该脚本仅能在5.1/5.6/5.7的版本中使用，8.x的版本需要修改`reset_cmd_v3`变量为8.x版本的数据库初始化命令（`/usr/local/mysqld --initialize`）

### 运行脚本前需修改的变量：
* 检查 `mariadb_socket` 与自己的测试环境中的是否一致（可能是`/tmp/mysql.sock`）
* `sysbench_lua_prefix` 应该为之前发布的那些lua文件的存储位置
* `output_dir` 为结果输出目录
* `mariadb_sample_result` 为`pict`输出文件

运行脚本前需要用`pict`对参数进行抽样，例如待测配置为`innodb_buffer_pool_size`，用不同的workload去测试这个配置在不同取值下的性能。即得形如到下面的测试样例文件：
```
sysbench	--table-size	--tables	--threads	--mysql-storage-engine	--innodb-buffer-pool-size	--innodb-log-file-size
"oltp_write_only.lua"	60000	10	25	innodb	1M	200M	2000
"oltp_write_only.lua"	80000	10	25	innodb	16M	200M	2000
"oltp_write_only.lua"	40000	10	25	innodb	256M	200M	2000
"oltp_write_only.lua"	100000	10	1	innodb	1M	200M	2000
"oltp_write_only.lua"	60000	10	100	innodb	8M	200M	2000
.... .... .... ....
```

### 如何得到上述文件：

首先安装[pict](https://github.com/microsoft/pict)（很简单：下载源码、进入源码目录执行`make`）

然后编辑如下文件`conf_variable_and_values.txt`：
```
###########################
###    Basic Scripts    ###
###########################

sysbench: "oltp_read_write.lua"

###########################
### workload  variables ###
###########################

# Number of rows per table(10000)
--table-size: 10, 40000, 100000, 200000, 400000, 600000, 800000, 1000000

--tables: 10

# number of threads to use(1)
--threads: 1, 50, 100

# Storage engine, only innodb support transaction(innodb)
--mysql-storage-engine: innodb

# 5M, 10M, 20M, 50M 100M
--innodb-buffer-pool-size: 5242880, 2147483648, 4294967296

# Do not change this 2 configurations unless you encounter errors about them
--innodb-log-file-size: 200M
--thread-concurrency: 2000


###########################
###       models        ###
###########################

{--table-size, --threads, --innodb-buffer-pool-size} @ 3
```
其中，`--innodb-buffer-pool-size: 5242880, 2147483648, 4294967296`为待测配置及几个可能取值（**测其他配置需要修改**），`--table-size`, `--threads`为sysbench的选项，请根据自己所测的配置视情况增加选项。

有了这个文件后可以通过运行（在`pict`的目录下）`./pict conf_variable_and_values.txt > mariadb_sample_result.txt`

得到的`mariadb_sample_result.txt`，就是运行脚本所必需的测试样例文件。

### 运行脚本

修改好脚本的几个参数后，执行：

`python PerfTest_dbs.py`

运行结束后，可以在之前设置好的输出目录看到结果。
