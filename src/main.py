import selectors
import socket


HOST = 'localhost'
PORT = 2077

pull = selectors.DefaultSelector()
ss = socket.socket()
ss.bind((HOST, PORT))
ss.listen()
ss.setblocking(False)
pull.register(ss, selectors.EVENT_READ, data=None)
while True:
    try:
        events = pull.select()
        for key, mask in events:
            # If data is None, the socket is server socket, accept connection
            if key.data is None:
                s, attr = key.fileobj.accept()
                s.setblocking(False)
                print('{} connected'.format(attr))
                pull.register(s, selectors.EVENT_READ,
                              dict(attr=attr, outb=b''))
            # If it is not server socket, and read event is available then read
            elif mask & selectors.EVENT_READ:
                d = key.fileobj.recv(8)
                if d:
                    key.data['outb'] += d
                    print('Read \'{}\' from {}'.format(d.decode(), key.data['attr']))
                else:
                    pull.modify(key.fileobj, selectors.EVENT_WRITE, key.data)
            # If it is not server socket, and write event is evailable
            # then write and close connection
            elif mask & selectors.EVENT_WRITE:
                if key.data['outb']:
                    print('Echoing \'{}\' to {}'.format(key.data['outb'].decode(), key.data['attr']))
                    key.fileobj.sendall(key.data['outb'])
                pull.unregister(key.fileobj)
                key.fileobj.close()
                print('{} closed'.format(key.data['attr']))
    except KeyboardInterrupt:
        print('\nInterrupted by keyboard')
        break
    except Exception as e:
        print(e)
        break
pull.close()
ss.close()
