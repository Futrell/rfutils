from __future__ import print_function
import sys
import subprocess

def system_call(cmd, verbose=False):
    """ system call

    Make a system call in the form of a Bash command, capturing stdout and 
    returning it.

    Params:
        cmd: A string representing a Bash command.
        verbose (default False): Whether to echo the command to stderr

    """
    if verbose:
        print(cmd, file=sys.stderr)    
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=None)
    output, _ = p.communicate()
    return output

def test_system_call():
    nose.tools.assert_equal(system_call("echo hello"), b"hello\n")

if __name__ == '__main__':
    import nose
    nose.runmodule()
