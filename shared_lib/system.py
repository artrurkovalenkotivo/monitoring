import subprocess


def cmd(command):
    p_output = subprocess.check_output(command,
                                       stderr=subprocess.STDOUT,
                                       shell=True,
                                       timeout=10,
                                       )
    p_output = p_output.decode("utf-8", "replace")
    return p_output
