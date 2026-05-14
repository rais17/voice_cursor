import subprocess, json, time, threading

proc = subprocess.Popen(
    ['pylsp'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

def read_stdout():
    while True:
        chunk = proc.stdout.read(1)
        if not chunk:
            break
        print(chunk.decode(errors='replace'), end='', flush=True)

def read_stderr():
    for line in proc.stderr:
        print('[ERR]', line.decode(errors='replace').strip())

threading.Thread(target=read_stdout, daemon=True).start()
threading.Thread(target=read_stderr, daemon=True).start()

def send(msg):
    body = json.dumps(msg).encode()
    header = f'Content-Length: {len(body)}\r\n\r\n'.encode()
    proc.stdin.write(header + body)
    proc.stdin.flush()
    print(f'[SENT] {msg.get("method", "unknown")}')

with open(r'D:\PyVoiceCursor\dummy.py', 'r') as f:
    content = f.read()

send({'jsonrpc':'2.0','id':1,'method':'initialize','params':{'processId':None,'rootUri':'file:///D:/PyVoiceCursor','capabilities':{'textDocument':{'publishDiagnostics':{}}}}})
time.sleep(2)
send({'jsonrpc':'2.0','method':'initialized','params':{}})
time.sleep(1)
send({'jsonrpc':'2.0','method':'textDocument/didOpen','params':{'textDocument':{'uri':'file:///D:/PyVoiceCursor/dummy.py','languageId':'python','version':1,'text':content}}})
time.sleep(1)
send({'jsonrpc':'2.0','method':'textDocument/didChange','params':{'textDocument':{'uri':'file:///D:/PyVoiceCursor/dummy.py','version':2},'contentChanges':[{'text':content}]}})
print('[WAITING 10s...]')
time.sleep(10)
print('[DONE]')