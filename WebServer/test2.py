# python3
import socket
import time

def run_server(port=53210):
  serv_sock = create_serv_sock(port)
  cid = 0
  while True:
    client_sock = accept_client_conn(serv_sock, cid)
    print('Иду сервить')
    serve_client(client_sock, cid)
    print('Засёрвил')

    cid += 1

def serve_client(client_sock, cid):
  request = read_request(client_sock)
  print('Запрос считан')
  if request is None:
    print(f'Client #{cid} unexpectedly disconnected')
  else:
    response = handle_request(request)
    write_response(client_sock, response, cid)


def create_serv_sock(serv_port):
  serv_sock = socket.socket(socket.AF_INET,
                            socket.SOCK_STREAM,
                            proto=0)
  serv_sock.bind(('', serv_port))
  serv_sock.listen()
  return serv_sock

def accept_client_conn(serv_sock, cid):
    client_sock, client_addr = serv_sock.accept()
    print(f'Client #{cid} connected '
          f'{client_addr[0]}:{client_addr[1]}')
    return client_sock

def read_request(client_sock,):
    try:
        buf = ''
        while '\r\n' not in buf:
            byte = client_sock.recv(1)  # возвращает тип bytes
            buf += str(byte, 'iso-8859-1')
        return buf

    except ConnectionResetError:
        # Соединение было неожиданно разорвано.
        return None
    except:
        raise

def handle_request(request):
    print(request)
    return request

def write_response(client_sock, response, cid):
  client_sock.sendall(response)
  client_sock.close()
  print(f'Client #{cid} has been served')



run_server(9999)
#response = requests.post('http://127.0.0.1:9999', json={'key':'value'})