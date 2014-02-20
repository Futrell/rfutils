from __future__ import print_function
import subprocess

def system_call(cmd):
    """ system call

    Make a system call in the form of a Bash command, capturing stdout and 
    returning it.

    Params:
        cmd: A string representing a Bash command.

    """
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=None)
    output, _ = p.communicate()
    return output
