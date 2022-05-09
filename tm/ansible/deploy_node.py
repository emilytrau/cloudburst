import json
import os
import subprocess
import sys
import ansible_runner

payload = json.loads(sys.argv[1])
directory = os.path.dirname(os.path.realpath(__file__))
my_ip = subprocess.run('hostname -I | cut -d" " -f1', shell=True, capture_output=True, check=True).stdout.decode('utf-8').strip()

inventory = {}
for group_name, group in payload.items():
    group_inventory = { 'hosts': {} }
    for node in group:
        group_inventory['hosts'][node['hostname']] = {
            'ansible_host': node['ip']
        }
    inventory[group_name] = group_inventory

with open(os.path.join(directory, 'id_rsa'), 'r') as f:
    ssh_key = f.read()

if __name__ == '__main__':
    ansible_runner.interface.run(
        project_dir=directory,
        playbook='site.yml',
        cmdline='--user ubuntu --ssh-extra-args="-oStrictHostKeyChecking=no -oConnectionAttempts=60"',
        ssh_key=ssh_key,
        inventory=inventory,
        extravars={
            'SLURMCTL_IP': my_ip
        },
    )
