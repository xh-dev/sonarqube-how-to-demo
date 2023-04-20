import subprocess
from typing import Callable
import re
import yaml
import sys
import os
import stat

pattern = re.compile("(?P<hostname>.*)-ip[ ]*=[ ]*\"(?P<ip>[^\"]+)\"")
lines = subprocess.check_output("terraform output".split(" ")).decode("utf-8").split("\n")

ip_list = [ 
	{
		"host": result.group("hostname"),
		"ip": result.group("ip")
	}
	for line in lines
	for result in [pattern.match(line)] if result is not None
]

d = dict()
d["fresh-server"] = {"hosts":{}}
for key_map in ip_list:
	d["fresh-server"]["hosts"].update(
	{
		key_map['host']: {
			"ansible_host": key_map['ip'],
			"ansible_user":"root"
		}
	})


def create_file(file_name: str, op:Callable, executable: bool = False):
	with open(file_name, "w") as f:
		op(f)

	if executable:
		st = os.stat(file_name)
		os.chmod(file_name, st.st_mode | stat.S_IEXEC)


def write_inventory_file(f):
	yaml.dump(d, f, indent=2, allow_unicode=True, default_flow_style=False)
create_file("inventory.yaml", write_inventory_file)


def write_setup_hosts(f):
	script = """\
!/bin/bash

setup_known_hosts(){
				 export ip=$1
				 echo "Setup known_hosts for $ip"
				 ssh-keygen -R $ip
				 ssh-keyscan -H $ip > ~/.ssh/known_hosts
}
"""
	script +="\n".join([ f"setup_known_hosts {i['ip']}" for i in ip_list])
	f.write(script)


create_file("setup_hosts.sh",write_setup_hosts,True)

def write_ansible_playbook_trigger(f):
	script = """\
#!/bin/bash

curl -O https://gist.githubusercontent.com/xh-dev/0cde34a413392ed1b401446afb757ca0/raw/init-ubuntu.yaml
curl -O https://gist.githubusercontent.com/xh-dev/0cde34a413392ed1b401446afb757ca0/raw/install-docker.yaml

ansible-playbook -i inventory.yaml \
	init-ubuntu.yaml \
	install-docker.yaml\
	playbook-sonarqube.yaml
"""
	f.write(script)
	

create_file("ansible-playbook-script.sh", 
	write_ansible_playbook_trigger,True)


def write_variable_setup(f):
	f.write("""\
#!/bin/bash
export ip="{ip}"
""".format_map(ip_list[0])
)
	
create_file("variable-setup.sh", 
	write_variable_setup,True)


def to_write(f):
	f.write("""\
rm -fr venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# setup variables
./variable-setup.sh

# ansible setups
./setup_hosts.sh
./ansible-playbook-script.sh
"""
)

create_file("init.sh", to_write, True)
