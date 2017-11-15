# A Simple Proc Util

A simple process monitor utility for Linux

## Getting Started

Ensure you have either Python2.7.x or Python 3.x installed (tested on 2.7.9), as well as pip for library management

### Prerequisites

Some external libraries are required to run. They can be easily installed using pip install <library>

```
pip - for installations
psutil - for process queries
numpy - for math
```

### How to run

You can run this in a few ways. Run with -h for all options. In each case it gathers info every 5 seconds, returning an average of each metric every 30 seconds.

```
$ ./SimpleProcUtil.py
```
Will run as the default and monitor 10 random processes for 10 runs

```
$ ./SimpleProcUtil.py -p 123
```
Will monitor a single pid 123 for 10 runs

```
$ ./SimpleProcUtil.py -e mysql -r 5
```
Will monitor all processes matching 'mysql' for 5 runs

### TODO
See the [TODO.txt] (TODO.txt) file for details

## Built With

* [PSutil](https://github.com/giampaolo/psutil) - The process library
* [numpy](http://www.numpy.org/) - The quintessential math library

## Authors

* **Tiago Baptista** - [Github](https://github.com/SurrealTiggi)
