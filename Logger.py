import sys

def log(message):
    try:
        if type(message) == bytes:
            message = message.decode('utf8')
        print(str(message))
        sys.stdout.flush()
    except BaseException as e:
        print('? {0}'.format(e))
        try:
            print('\t?:', message)
        except BaseException as e:
            pass


