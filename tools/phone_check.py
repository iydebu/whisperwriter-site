import json, subprocess, time, urllib.request, websocket, base64, sys, itertools, os
CH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT = 9444
url = sys.argv[1]; out = sys.argv[2]
p = subprocess.Popen([CH, '--headless=new', f'--remote-debugging-port={PORT}', '--hide-scrollbars', '--remote-allow-origins=*',
                      '--user-data-dir=' + os.path.expandvars(r'%LOCALAPPDATA%\hermes\cache\scratch\chrome-emu'), 'about:blank'])
try:
    for _ in range(40):
        try: t = json.load(urllib.request.urlopen(f'http://127.0.0.1:{PORT}/json')); break
        except Exception: time.sleep(.25)
    ws = websocket.create_connection(next(x for x in t if x['type'] == 'page')['webSocketDebuggerUrl'], max_size=None)
    ids = itertools.count(1)
    def call(m, **pr):
        i = next(ids); ws.send(json.dumps({'id': i, 'method': m, 'params': pr}))
        while True:
            r = json.loads(ws.recv())
            if r.get('id') == i: return r.get('result', {})
    call('Emulation.setDeviceMetricsOverride', width=390, height=844, deviceScaleFactor=2, mobile=True)
    call('Page.navigate', url=url); time.sleep(2.5)
    r = call('Runtime.evaluate', expression="""(()=>{document.querySelectorAll('.reveal').forEach(e=>e.classList.add('in'));
      const wide=[...document.querySelectorAll('body *')].filter(e=>e.getBoundingClientRect().right>innerWidth+1).slice(0,8).map(e=>e.tagName+'.'+e.className+' '+Math.round(e.getBoundingClientRect().right));
      return JSON.stringify({vw:innerWidth, sw:document.documentElement.scrollWidth, h:document.documentElement.scrollHeight, wide})})()""", returnByValue=True)
    info = json.loads(r['result']['value']); print(info)
    shot = call('Page.captureScreenshot', format='png', captureBeyondViewport=True,
                clip={'x': 0, 'y': 0, 'width': 390, 'height': min(info['h'], 2400), 'scale': 1})
    open(out, 'wb').write(base64.b64decode(shot['data']))
finally:
    p.kill()
