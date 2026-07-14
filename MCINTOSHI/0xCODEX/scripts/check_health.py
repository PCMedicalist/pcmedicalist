#!/usr/bin/env python3
import subprocess
import sys

def run(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

def main():
    res = run('docker compose ps --services')
    if res.returncode != 0:
        print('Failed to list services:', res.stderr)
        return 2
    services = [s.strip() for s in res.stdout.splitlines() if s.strip()]
    if not services:
        print('No services found in docker compose.')
        return 1
    failures = []
    for svc in services:
        print(f'Checking service: {svc}')
        q = run(f'docker compose ps -q {svc}')
        cid = q.stdout.strip()
        if not cid:
            print(f'  {svc}: container not running')
            failures.append(svc)
            continue
        # check for main.py process
        check = run(f'docker exec {cid} pgrep -f main.py')
        if check.returncode == 0:
            print(f'  {svc}: main.py running (pid(s): {check.stdout.strip()})')
        else:
            print(f'  {svc}: main.py NOT running')
            # show last 20 lines of logs to help debug
            logs = run(f'docker logs --tail 20 {cid}')
            print('  last logs:')
            for line in logs.stdout.splitlines():
                print('   ', line)
            failures.append(svc)
    if failures:
        print('\nHealth check failures:', ', '.join(failures))
        return 1
    print('\nAll services healthy.')
    return 0

if __name__ == '__main__':
    sys.exit(main())
