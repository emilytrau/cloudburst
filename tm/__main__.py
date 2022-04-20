import jinja2
import pulumi
from pulumi import Output, ResourceOptions
import pulumi_cloudinit as cloudinit
from pulumi_command import local
from pulumi_openstack import compute
import pulumi_tailscale as tailscale

FLAVOR = 't3.small'
IMAGE = '356ff1ed-5960-4ac2-96a1-0c0198e6a999' # NeCTAR Ubuntu 20.04 LTS (Focal)
USER_SSH_KEY = 'ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEAxs0LYg6V2IvrwaW74RCzoZlvSAXS5fed9/sFMz51DPqGAw420Q2jPsvKsSAbOlLD3ZjTu8Xy+TPQSbFJgSp448/s9aXWtmCioP5zNrzorShvhzH9VnyraWwjgAEscr09xSelDZ7wlFtdoBYkpoOM8FWRWYYCm91yi5xzPHBo/hG6q4mkaLaJC6LdRRNXRkAaCBg/jfcv7jHudoHOVwzcm8w2GOKurI6awM8Tmvy9S2ZNeq9W20SuydnkzVP4Y4Rtss50xLU/r3H7An54Oyv9QeOkEHz0M7FHUZ2NOUVivOTCt2uJkzUOR5BQR7asFEaZ7AyEV3Y+MpeHtwq9TtW0Fw== EmilyTrau'

jinja_env = jinja2.Environment(
		loader=jinja2.FileSystemLoader("cloudinit"),
		autoescape=jinja2.select_autoescape(),
		trim_blocks=True,
		lstrip_blocks=True)
cloudinit_templates = [jinja_env.get_template(x) for x in jinja_env.list_templates()]

keypair = compute.Keypair('tm-keypair',
	public_key=USER_SSH_KEY)

# Enable MagicDNS
tailnet_nameservers = tailscale.DnsNameservers("tailnet-dns-nameservers", nameservers=[
    "8.8.8.8",
    "8.8.4.4",
])
tailscale.DnsPreferences("tailnet-dns-preferences",
	magic_dns=True,
	opts=ResourceOptions(depends_on=[tailnet_nameservers]))

tailnet_key = tailscale.TailnetKey('tailnet-key',
    ephemeral=True,
    reusable=True).key

munge_key = local.Command('munge-key',
    create='mungekey -cfk /tmp/munge.key && base64 -w0 /tmp/munge.key && rm /tmp/munge.key',
	opts=ResourceOptions(additional_secret_outputs=['stdout'], ignore_changes=['stdout'])).stdout

def create_instance(hostname, node_type):
	host_keys = local.Command(f'ssh-host-keys-{hostname}',
		create=fr"""mkdir -p /tmp/hostkey-{hostname}/etc/ssh \
			&& ssh-keygen -Af /tmp/hostkey-{hostname} > /dev/null \
			&& tar -cC /tmp/hostkey-{hostname} . | base64 -w0 \
			&& rm -rf /tmp/hostkey-{hostname}
		""",
		opts=ResourceOptions(additional_secret_outputs=['stdout'], ignore_changes=['stdout'])).stdout

	pulumi.export(f'{hostname}-key', host_keys)
	
	def create_cloudinit(args):
		# print(args)
		templates = [t.render(**args) for t in cloudinit_templates]
		import sys
		# sys.stdout.write(args['host_keys'])
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
			tailscale_authkey=tailnet_key,
			munge_key=munge_key,
		).apply(create_cloudinit)

	instance = compute.Instance(hostname,
		flavor_name=FLAVOR,
		image_id=IMAGE,
		key_pair=keypair.name,
		user_data=cloudinit_config,
		stop_before_destroy=True)
	
	pulumi.export(f'{hostname}-ip', instance.access_ip_v4)

create_instance('tm-login', node_type='login')
create_instance('tm-compute1', node_type='compute')
