## C++ in Python

This will be using [Boost Python](http://www.boost.org/doc/libs/1_66_0/libs/python/doc/html/index.html) to interface C++ into Python.

## Setup

1. You need Boost, but we need to build from source since the Ubuntu version is most likely old (16.04 only has 1.58).
	* Instructions are [here](http://www.boost.org/doc/libs/1_46_1/more/getting_started/unix-variants.html)
    * There is also a build script `utilities/build_boost.sh` which will install Boost and all components
    * [Description](https://stackoverflow.com/a/45767023) of build process

2. Compile the `boost_test.cpp` to test that boost is installed properly.
3. The `boost-python` directory has a set of examples for interfacing python and boost. To test just run

~~~
mkdir build; cd build
cmake ..
make
make tests
~~~

## Commands

* This builds the object file
~~~
g++ -ftemplate-depth-128 -O0 -fno-inline -Wall -g -fPIC -I/usr/include/python3.5m -c -o "hello.o" "hello.cpp"
~~~

* This links it into a library for python

~~
g++ -o hello.so -Wl,-h -Wl,hello.so -shared -Wl,--start-group hello.o  -Wl,-Bstatic  -Wl,-Bdynamic -L/usr/local/lib -lboost_python3 -ldl -lpthread -lutil -Wl,--end-group
~~

There's an example `CMakeLists.txt` for a more general build, a standalone `Makefile` for simple projects.

## Helpful Links

* [Boost Python Tutorial](http://www.boost.org/doc/libs/1_66_0/libs/python/doc/html/tutorial/index.html)
* [Boost Numpy]()

