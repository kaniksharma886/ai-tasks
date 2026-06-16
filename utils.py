

''' 
New arguments added to display streaming in same line
'''
def log(*msg, end="\n", flush=False):

    print(*msg, end=end, flush=flush)


def log_error(*msg):

    print("[ERROR]", *msg)


