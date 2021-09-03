#include<seccomp.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <stddef.h>

void install_filters()
{
            scmp_filter_ctx context;

            /*The seccomp_init() function must be called before any other
              libseccomp functions as the rest of the library API will fail if
              the filter context is not initialized properly.*/

            context = seccomp_init(SCMP_ACT_KILL); // initializing the seccomp filter using seccomp_init method
            /* SCMP_ACT_KILL: Thread will be killed if any of the rules lies outside the configured rules. */

            // Adding certain rules, i.e. allow only these system calls to be executed based on the user's code-
            /* Parameters to the seccomp_rule_add method:
               context-  the seccomp filter which we are adding the rules to
               SCMP_ACT_ALLOW- The action to be performed on the rule that we are adding- in this case allow the action
               SCMP_SYS(...)- The syscall which we are adding the rule for the specified action (this is an integer)
            */

            seccomp_rule_add(context, SCMP_ACT_ALLOW, SCMP_SYS(exit_group), 0); // exit_group - exit all threads in a process
            seccomp_rule_add(context, SCMP_ACT_ALLOW, SCMP_SYS(read), 0); // read - read from a file descriptor
            seccomp_rule_add(context, SCMP_ACT_ALLOW, SCMP_SYS(write), 0); // write - write to a file descriptor
            seccomp_rule_add(context, SCMP_ACT_ALLOW, SCMP_SYS(fstat),0); // fstat- get file ststus
            seccomp_rule_add(context, SCMP_ACT_ALLOW, SCMP_SYS(brk),0); // brk- change data segment size
            seccomp_rule_add(context, SCMP_ACT_ALLOW, SCMP_SYS(lseek),0); // lseek - reposition read/write file offset
            seccomp_rule_add(context, SCMP_ACT_ALLOW, SCMP_SYS(writev),0); // writev — write a vector
            seccomp_rule_add(context, SCMP_ACT_ALLOW, SCMP_SYS(mmap),0); //mmap, munmap - map or unmap files or devices into memory
            seccomp_rule_add(context, SCMP_ACT_ALLOW, SCMP_SYS(munmap),0);

            seccomp_load(context); // Loading the current seccomp filter into the kernel using seccomp_load() method
}