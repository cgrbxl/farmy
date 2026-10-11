"""Exercise the actual image over loopback, with a read-only unprivileged runtime."""
import base64
import hashlib
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request


def docker(*args):
    return subprocess.check_output(['docker', *args], text=True).strip()


def main(image):
    container = docker('run', '--platform=linux/amd64', '-d', '--rm', '--read-only', '--cap-drop=ALL',
                       '--security-opt=no-new-privileges', '--memory=256m', '--cpus=0.25',
                       '-p', '127.0.0.1::8080', image)
    try:
        for attempt in range(30):
            ports = json.loads(docker('inspect', container))[0]['NetworkSettings']['Ports'].get('8080/tcp')
            if ports:
                port = ports[0]['HostPort']; break
            time.sleep(0.5)
        else:
            raise RuntimeError('Docker did not publish the loopback port.')
        endpoint = 'http://127.0.0.1:'+port
        for attempt in range(30):
            try:
                with urllib.request.urlopen(endpoint+'/health', timeout=1) as response:
                    assert json.load(response) == {'status':'ok'}
                break
            except (OSError, urllib.error.URLError):
                time.sleep(0.5)
        else:
            raise RuntimeError('Container did not become healthy.')
        raw = b'Synthetic container check.\n'
        digest = hashlib.sha256(raw).hexdigest()
        query = dict(contract='farmy.processing.text/0.1-draft', operation='text.stats', requestId='container-test-001',
                     payload=dict(receiverId='processor.scaleway', purpose='text-statistics', evidence=dict(
                         schema='farmy.evidence/0.1-draft', contentBase64=base64.b64encode(raw).decode(),
                         resource=dict(id='sha256:'+digest, sha256=digest, size=len(raw), mediaType='text/plain;charset=utf-8'))))
        def send():
            return urllib.request.urlopen(urllib.request.Request(endpoint+'/process', data=json.dumps(query).encode(),
                                                   headers={'Content-Type':'application/json'}), timeout=5)
        with send() as response:
            result = json.load(response)
        assert result['input'] == query['payload']['evidence']['resource']
        assert result['producerId'] == 'processor.scaleway'
        assert result['requestId'] == query['requestId']
        assert result['output'] == dict(bytes=len(raw), lines=1, words=3)
        query['payload']['evidence']['resource']['sha256'] = '0'*64
        try:
            send()
            raise AssertionError('Tampered input accepted.')
        except urllib.error.HTTPError as error:
            assert error.code == 400
            error.close()
        assert not docker('logs', container), 'Unexpected application request logging'
        assert docker('exec', container, 'id', '-u') == '65532'
        print('PASS actual container: readiness, exact result, tamper rejection, non-root, read-only, no request logs.')
    finally:
        subprocess.run(['docker', 'stop', '-t', '1', container], check=True, stdout=subprocess.DEVNULL)

if __name__ == '__main__':
    main(sys.argv[1])
