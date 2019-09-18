# GCC/Clang 测试脚本使用方法

### Step 1

复制benchmark文件到某个目录‘/dir/to/benchmarks’

所谓的benchmark文件，一般是独立的c/c++文件，例如tramp3d-v4.cpp；有时是一个工程，需要用make来编译，此时可以选择评估用gcc/g++/clang/clang++单独编译其中每个源码文件的时间，或者make整个工程的时间（如此，建议不使用本脚本，直接运行：`time make CFLAGS="-O0 -march=native"`，其中-O0部分手动改成-O1/-O2...）。

### Step 2

运行：

`python PerfTest_c-compiler.py <c/c++ compiler name> 
</dir/to/benchmarks><repeats>`

`<c/c++ compiler name>` gcc g++ clang clang++ 或其他
`</dir/to/benchmarks>` benchmark目录
`<repeats>` [1,∞)重复次数，性能测试一般要多次重复取平均/中位才能保证结果可信

### Step 3

在当前目录下，会有运行结果，其中log.err文件是benchmark中，一些无法编译的c/c++源码。'[Result]'开头的文件则是测试结果，点开后即懂


