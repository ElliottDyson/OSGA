import builtins as __builtin__

def print(*msg):
    '''print and log!'''
    # import datetime for timestamps
    import datetime as dt
    # convert input arguments to strings for concatenation
    message = []
    for m in msg:
        message.append(str(m))
    message = ' '.join(message)
    # append to the log file
    with open('output.txt','a') as log:
        # log.write(f'{dt.datetime.now()} | {message}\n')
        try:
            log.write(f'{message}\n')
        except:
            log.write(f'{message.encode("utf-8")}\n')
    # print the message using the copy of the original print function to stdout
    __builtin__.print(message)