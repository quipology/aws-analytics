#!/usr/bin/python

import boto3
import sys
import os
import time
import subprocess as sp

product = sys.argv[1]
environment_name = sys.argv[2]
environment_type = sys.argv[3]
component = sys.argv[4]
stack = sys.argv[5]
num_snapshots = sys.argv[6]


def create_ec2_client():
	return boto3.client('ec2', region_name='us-west-2')

def find_instances(client):
	return client.describe_instances(
    Filters = [
        {
            'Name':'tag:s1:environment-type', 'Values': [environment_type]
        },
        {
            'Name':'tag:s1:environment-name', 'Values': [environment_name]
        },
        {
            'Name':'tag:s1:product', 'Values': [product]
        },
        {
            'Name':'tag:s1:role', 'Values': [role]
        }
    ]
)

def main():
	jar = []
	ec2 = create_ec2_client()

	###########################
	#### BEGIN CONDITIONAL ####
	###########################
	global role
	# If app was selected:
	if component == 'app':
		#---- app ----:
		role = 'app'
		found_app = find_instances(ec2)
		try:
			for instances in found_app['Reservations']:
				for instance in instances['Instances']:
					ip_address = instance['PrivateIpAddress']
					# Put found app instances in the jar:
					if ip_address:
						if ip_address not in jar:
							jar.append(ip_address+' role:app')
		except:
			print('Something went wrong with the instance search for s1:role = \'app\'')

		#---- timer ----:
		role = 'timer'
		found_timer = find_instances(ec2)
		try:
			for instances in found_timer['Reservations']:
				for instance in instances['Instances']:
					ip_address = instance['PrivateIpAddress']
					# Put found timer instances in the jar:
					if ip_address:
						if ip_address not in jar:
							jar.append(ip_address+' role:timer')
		except:
			print('Something went wrong with the instance search for s1:role = \'timer\'')
	
	#==================================================================
	#==================================================================
	# If api was selected:
	elif component == 'api':
		#---- api ----:
		role = 'api'
		found_app = find_instances(ec2)
		try:
			for instances in found_app['Reservations']:
				for instance in instances['Instances']:
					ip_address = instance['PrivateIpAddress']
					# Put found app instances in the jar:
					if ip_address:
						if ip_address not in jar:
							jar.append(ip_address+' role:api')
		except:
			print('Something went wrong with the instance search for s1:role = \'api\'')
	
	#==================================================================
	#==================================================================
	# If all was selected:		
	elif component == 'all':
		#---- app ----:
		role = 'app'
		found_app = find_instances(ec2)
		try:
			for instances in found_app['Reservations']:
				for instance in instances['Instances']:
					ip_address = instance['PrivateIpAddress']
					# Put found app instances in the jar:
					if ip_address:
						if ip_address not in jar:
							jar.append(ip_address+' role:app')
		except:
			print('Something went wrong with the instance search for s1:role = \'app\'')

		#---- timer ----:
		role = 'timer'
		found_timer = find_instances(ec2)
		try:
			for instances in found_timer['Reservations']:
				for instance in instances['Instances']:
					ip_address = instance['PrivateIpAddress']
					# Put found timer instances in the jar:
					if ip_address:
						if ip_address not in jar:
							jar.append(ip_address+' role:timer')
		except:
			print('Something went wrong with the instance search for s1:role = \'timer\'')

		#---- api ----:
		role = 'api'
		found_app = find_instances(ec2)
		try:
			for instances in found_app['Reservations']:
				for instance in instances['Instances']:
					ip_address = instance['PrivateIpAddress']
					# Put found app instances in the jar:
					if ip_address:
						if ip_address not in jar:
							jar.append(ip_address+' role:api')
		except:
			print('Something went wrong with the instance search for s1:role = \'api\'')

	##########################
	#### END CONDITIONAL #####
	##########################

	#############################################################
	#### LOOP THROUGH IPs AND EXECUTE LOCAL SNAPSHOT SCRIPT #####
	#############################################################

	for i in jar:
		print('Found IP:{}, starting snapshots..'.format(i))
		i = i.split()
		try:
			sp.call('ssh -i ~/.ssh/s1dev_infra -o StrictHostKeyChecking=no ec2-user@{} "sudo python ~/snapshots.py {} {} {} {} {}"'.format(i[0], product, environment_name, environment_type, stack, num_snapshots), shell=True)
			time.sleep(1)
		except:
			print('Something went wrong with SSH attempt to {}'.format(i[0]))


	print('Execution Complete!')

if __name__ == '__main__':
	main()
