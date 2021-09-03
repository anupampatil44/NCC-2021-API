from seccomp import *
import sys

# create a filter object with a default KILL action

'''For more information, refer: 
https://github.com/seccomp/libseccomp/blob/main/src/python/seccomp.pyx
https://lwn.net/Articles/634391/
'''

def install_filter():
    f = SyscallFilter(defaction=KILL)
    f.add_rule(ALLOW, "read", Arg(0, EQ, sys.stdin.fileno()))
    f.add_rule(ALLOW, "write", Arg(0, EQ, sys.stdout.fileno()))
    f.add_rule(ALLOW, "write", Arg(0, EQ, sys.stderr.fileno()))
    f.add_rule(ALLOW, "fstat")
    f.add_rule(ALLOW, 'ioctl')
    f.add_rule(ALLOW, 'sigaltstack')
    f.add_rule(ALLOW, "rt_sigaction")
    f.add_rule(ALLOW, "exit_group")

    # Required for traceback when a runtime error occurs, the following signals are necessary
    f.add_rule(ALLOW, "read")
    f.add_rule(ALLOW, "stat")
    f.add_rule(ALLOW, "openat")
    f.add_rule(ALLOW, "lseek")
    f.add_rule(ALLOW, "close")
    f.add_rule(ALLOW, "mmap")
    f.add_rule(ALLOW, "brk")
    f.add_rule(ALLOW, "getdents")
    f.add_rule(ALLOW, "munmap")
    f.add_rule(ALLOW, "mprotect")
    f.add_rule(ALLOW, "access")
    f.add_rule(ALLOW, "futex")
    f.add_rule(ALLOW, "getrandom")
    f.add_rule(ALLOW, "getcwd")
    f.add_rule(ALLOW, "lstat")
    f.add_rule(ALLOW, "fcntl")


    f.load() # Loading the current seccomp filter into the kernel using the .load() method.


install_filter()
