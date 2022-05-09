import jinja2
import pulumi
from pulumi import Output, ResourceOptions
import pulumi_cloudinit as cloudinit
from pulumi_command import local
from pulumi_openstack import compute, networking
import pulumi_tailscale as tailscale

FLAVOR = 't3.xsmall'
IMAGE = '64a0c9c0-dac0-48c6-aa01-d433dcc362e2' # NeCTAR Ubuntu 22.04 LTS (Jammy)
AVAILABILITY_ZONE = 'monash-02'
USER_SSH_KEY = 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCm2ewMbK6crRF5FSnf4m4rRKxdqAmjmyJqlesj7+w/ahk+PTYbTniThr4+7kc9fzSwToaMDtxOQfq2jIhYeIWHjD3XaHtxeI2kIbBnL8UuBfKAHE2VzD+6sBv+MeHWAGOwP/TKWe/eyfSfJvt54WUtYgH7x2WtrYeK/WSdESydgPaoYBBfiChhFK2s6krlrxDDcMWLPCLDxZSbEvDU9yOY4DXcA4Bd0MHR5PLWX0pLKaHXcZz8E68QXmJ7LqqZ7M1RxGAAaw17u18j2F3PnvXPZLhGALLEVpgDnl3XUz5TrwPGFNGgwq41O0w+kFsoo5TFT0teqF3ZgovUntaGv/sPUNCLsw5HM+ShgCKEOpx0ZrctNYIzSZhxMDB7UBNHBuGaf9028zvscNQEzGtZmfxoygWvmHqa+S0R5rLTbaVnGCNigQMi5z4JFxSnSBA+7Fp9VS7M63tjgpmaAJM5HDQQA/RcelTrEOuuDliDtHaP08NYsfnEUFw6OP7CNequylc= gitpod@emilytrau-cloudburst-zojmwdxkbos'

jinja_env = jinja2.Environment(
		loader=jinja2.FileSystemLoader("cloudinit"),
		autoescape=jinja2.select_autoescape(),
		trim_blocks=True,
		lstrip_blocks=True)
cloudinit_templates = [jinja_env.get_template(x) for x in jinja_env.list_templates()]

keypair = compute.Keypair('tm-keypair',
	name='tm-keypair',
	public_key=USER_SSH_KEY)

security_group = networking.SecGroup('tm-security-group')
security_group_ssh = networking.SecGroupRule(
	'tm-security-group-ssh',
	direction='ingress',
	ethertype='IPv4',
	security_group_id=security_group.id,
	port_range_max=22,
    port_range_min=22,
    protocol="tcp",
    remote_ip_prefix="0.0.0.0/0",
)

munge_key = local.Command(
	'munge-key',
  create='mungekey -cfk /tmp/munge.key -b 4096 && base64 -w0 /tmp/munge.key && rm /tmp/munge.key',
	opts=ResourceOptions(additional_secret_outputs=['stdout'], ignore_changes=['stdout'])
).stdout

def create_instance(hostname, node_type):
	host_keys = local.Command(f'ssh-host-keys-{hostname}',
		create=fr"""mkdir -p /tmp/hostkey-{hostname}/etc/ssh \
			&& ssh-keygen -Af /tmp/hostkey-{hostname} > /dev/null \
			&& tar -czC /tmp/hostkey-{hostname} . | base64 -w0 \
			&& rm -rf /tmp/hostkey-{hostname}
		""",
		opts=ResourceOptions(additional_secret_outputs=['stdout'], ignore_changes=['stdout'])).stdout
	
	def create_cloudinit(args):
		# print(args)
		templates = [t.render(**args) for t in cloudinit_templates]
		import sys
		# sys.stdout.write(args['munge_key'])
		# for t in templates:
		# 	sys.stdout.write(t)
		config_parts = [
			cloudinit.GetConfigPartArgs(
				content=template,
				content_type='text/cloud-config',
				merge_type='list(append)+dict(recurse_array)+str()'
			)
			for template in templates
		]
		config = cloudinit.get_config(parts=config_parts, gzip=True)
		return config.rendered

	cloudinit_config = Output.all(
			user_ssh_key=USER_SSH_KEY,
			hostname=hostname,
			node_type=node_type,
			host_keys=host_keys,
			munge_key=munge_key,
		).apply(create_cloudinit)

	instance = compute.Instance(hostname,
		flavor_name=FLAVOR,
		image_id=IMAGE,
		availability_zone_hints=AVAILABILITY_ZONE,
		key_pair=keypair.name,
		security_groups=[security_group.name],
		user_data=cloudinit_config,
		stop_before_destroy=True)
	
	pulumi.export(f'{hostname}-ip', instance.access_ip_v4)

create_instance('tm-login', node_type='login')
create_instance('tm-compute1', node_type='compute')
