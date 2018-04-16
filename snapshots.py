#!/usr/bin/python

import boto3
import sys
import os
import re
import time
import subprocess as sp
from datetime import datetime
from datetime import timedelta

if len(sys.argv) < 5:
	print('Missing arguments, exiting..')
	sys.exit()
elif len(sys.argv) == 5:
	num_snapshots = 3
elif len(sys.argv) == 6:
	num_snapshots = int(sys.argv[5])

product = sys.argv[1]
environment_name = sys.argv[2]
environment_type = sys.argv[3]
stack = sys.argv[4]

def create_snapshot_dir(stack):
	try:
		# Set paths variables based on stack:
		global snapshot_dir
		global stack_log
		global server_log
		global output_log_dir
		global var_log

		snapshot_dir = '/dev/snapshots/'
		stack_log = '/home/s1/wildfly/{}/nohup.out'.format(stack)
		server_log = '/home/s1/wildfly/{}/log/server.log'.format(stack)
		output_log_dir = '/home/s1/wildfly/{}/logs/'.format(stack)
		var_log = '/var/log/messages'


		#################################
		# Create snapshots directory:
		#################################
		while 'snapshots' not in os.listdir('/dev/'):
			try:
				sp.call('mkdir {}'.format(snapshot_dir), shell=True)
			except:
				print('Unable to create directory for some reason - maybe permissions issue, exiting..')
				sys.exit()
		success = '{}'.format(snapshot_dir)
		print('Snapshots directory created successfully --> {}'.format(success))
	except:
		pass

def create_date_time_dir():
	try:
		#################################
		# Create date/time sub-directory:
		#################################
		global now
		now = datetime.now()
		now = now.strftime('%Y%m%d_%H%M%S')
		while now not in os.listdir(snapshot_dir):
			try:
				sp.call('mkdir {}{}'.format(snapshot_dir, now), shell=True)
			except:
				print('Unable to create directory for some reason - maybe permissions issue, exiting..')
				sys.exit()
		success = '{}{}'.format(snapshot_dir, now)
		print('Day/Time directory created successfully --> {}'.format(success))
	except:
		pass

def output_snapshot():
	try:
		##############################
		# Get snapshot of output file:
		##############################
		print('Creating snapshot of output file..')
		files = os.listdir('/home/s1/wildfly/{}/logs/'.format(stack))
		for i in files:
			if re.search(r'_output\.log$', i):
				output_file = i # Found output file
				break
		else:
			print('No output log file found.')
			return None

		# Create the snapshots based on number passed in:
		for i in range(num_snapshots):
			try:
				sp.call('tail -n 500 {0}{1} >> {2}{3}/output_{3}'.format(output_log_dir, output_file, snapshot_dir, now), shell=True)
			except:
				print('Unable to create snapshot of \'{}{}\'for some reason - maybe output file missing.'.format(output_log_dir, output_file))
				return None
		
		time.sleep(1)
		if 'output_{}'.format(now) in os.listdir('{}{}'.format(snapshot_dir, now)):
			success = '{0}{1}/output_{1}'.format(snapshot_dir, now)
			print('Output snapshots created successfully --> {}'.format(success))
		else:
			print('Output snapshots NOT created - something went wrong')
	except:
		pass

def server_log_snapshot():
	try:
		##################################
		# Get snapshot of server log file:
		##################################
		print('Creating snapshot of server log file..')
		 
		# Create the snapshot based on number passed in:
		for i in range(num_snapshots):
			try:
				sp.call('tail -n 500 {0} >> {1}{2}/server_{2}'.format(server_log, snapshot_dir, now), shell=True)
			except:
				print('Unable to create snapshot of \'{}\'for some reason - maybe output file missing.'.format(server_log))
				return None

		time.sleep(1)
		if 'server_{}'.format(now) in os.listdir('{}{}'.format(snapshot_dir, now)):
			success = '{0}{1}/server_{1}'.format(snapshot_dir, now)
			print('Server snapshots created successfully --> {}'.format(success))
		else:
			print('Server snapshots NOT created - something went wrong')
	except:
		pass

def sar_log_snapshot():
	try:
		##########################
		# Get snapshot of sar log:
		##########################
		print('Creating snapshot of sar log..')
		sar_now = datetime.now()
		start_time = str(sar_now - timedelta(minutes=15))
		start_time = start_time.replace(start_time[-7:], '').replace(start_time[:11], '')

		end_time = str(sar_now)
		end_time = end_time.replace(end_time[-7:], '').replace(end_time[:11], '')

		print('Start time will be: {} (15 minute delta), end time will be: {}'.format(start_time, end_time))
		
		sar_log = '{0}{1}/sar_{1}'.format(snapshot_dir, now)

		# Create the sar snapshot based on number passed in:
		for i in range(num_snapshots):
			try:
				sp.call('sar -A -f -s {0} -e {1} >> {2}{3}/sar_{3}'.format(start_time, end_time, snapshot_dir, now), shell=True)
			except:
				print('Unable to create snapshot of \'{}\'for some reason - maybe output file missing.'.format(sar_log))
				return None

		time.sleep(1)
		if 'sar_{}'.format(now) in os.listdir('{}{}'.format(snapshot_dir, now)):
			print('Sar snapshots created successfully --> {}'.format(sar_log))
		else:
			print('Sar snapshots NOT created - something went wrong')
	except:
		pass

def var_log_snapshot():
	try:
		##########################
		# Get snapshot of var log:
		##########################
		print('Creating snapshot of var log..')
		 
		# Create the snapshot based on number passed in:
		for i in range(num_snapshots):
			try:
				sp.call('tail -n 500 {0} >> {1}{2}/var_{2}'.format(var_log, snapshot_dir, now), shell=True)
			except:
				print('Unable to create snapshot of \'{}\'for some reason - maybe output file missing.'.format(var_log))
				return None

		time.sleep(1)
		if 'var_{}'.format(now) in os.listdir('{}{}'.format(snapshot_dir, now)):
			success = '{0}{1}/var_{1}'.format(snapshot_dir, now)
			print('Var snapshot created successfully --> {}'.format(success))
		else:
			print('Var snapshot NOT created - something went wrong')
	except:
		pass

def top_snapshot():
	######################
	# Get snapshot of top:
	######################
	try:
		sp.call('top -H -b -n 1 >> {0}{1}/top_{1}'.format(snapshot_dir, now), shell=True)
	except:
		print('Unable to create snapshot of \'{0}{1}/top_{1}\'for some reason.'.format(snapshot_dir, now))
		return None
	else:
		time.sleep(1)
		if 'top_{}'.format(now) in os.listdir('{}{}'.format(snapshot_dir, now)):
			success = '{0}{1}/top_{1}'.format(snapshot_dir, now)
			print('Top snapshot created successfully --> {0}{1}/top_{1}'.format(snapshot_dir, now))
		else:
			print('Top snapshot NOT created - something went wrong')

def tail_f_stack_snapshot(num_snapshots):
	try:
		######################################
		# Get snapshot of stack via 'tail -f':
		######################################
		try:
			sp.call('tail -f {0} >> {1}{2}/stack_{2} &'.format(stack_log, snapshot_dir, now), shell=True)
		except:
			print('Unable to create snapshot of \'{}\'for some reason.'.format(stack_log))
			return None
		else:
			print('Finding java PID..')
			java_pid = sp.check_output('pgrep -l java', shell=True) # Get java PID
			if java_pid:
				java_pid = java_pid.split()[0]
				print('Found java PID = {}'.format(java_pid))
				
				### Code entered here
				counter = 1
				for num in range(num_snapshots):
					print('Taking snapshot #{}'.format(counter))
					print('Executing "killall -3 java" command..')
					try:
						sp.call('killall -3 java', shell=True) # Send quit signal to java PID
					except:
						print('Failed to execute "killall -3 java" command')
					else:
						print('Command "killall -3 java" executed successfully!')
						top_snapshot()
						print('Snapshot #{} complete!'.format(counter))
						counter += 1
						
			pid = sp.check_output('pgrep -l tail', shell=True)
			if pid:
				pid = pid.split()
				pid = pid[0]
				print('Stack tail -f Pid = {}'.format(pid))
				print('Sleeping for 2 seconds..')
				time.sleep(2)
				print('Killing Pid {}..'.format(pid))
				sp.call('kill {}'.format(pid), shell=True)
				pid_alive = sp.check_output('sudo ps aux | grep tail', shell=True)
				if pid not in pid_alive:
					print('Pid {} killed successfully!'.format(pid))
				else:
					print('Unable to kill Pid {} for some reason'.format(pid))
						
		print('Stack snapshot created successfully --> {0}{1}/stack_{1}'.format(snapshot_dir, now))					
	except:
		pass

def zip_the_snapshots():
	try:
		####################
		# Zip the snapshots:
		####################
		global zip_file
		print('Zipping the snapshots...')
		os.chdir(snapshot_dir)
		if now in os.listdir('.'):
			while '{}.zip'.format(now) not in os.listdir('.'):
				try:
					sp.call('zip {0}.zip {0}/*'.format(now), shell=True)
					time.sleep(2)
				except:
					print('Something went wrong trying to zip the snapshots.')
					return False
			zip_file = '{}.zip'.format(now)
			print('Snapshots zipped successfully --> {}{}.zip'.format(snapshot_dir, now))
			return True
		else:
			print('Unable to zip snapshots - directory missing.')
			return False
	except:
		pass

def cleanup():
	try:
		###########################
		# Cleanup snapshot sub-dir:
		###########################
		print('Cleaning up local files and directory...')
		time.sleep(4)
		if zip_file in os.listdir(snapshot_dir):
			sp.call('sudo rm -rf {}{}/'.format(snapshot_dir, now), shell=True)
			sp.call('sudo rm -rf {}{}'.format(snapshot_dir, zip_file), shell=True)
			print('Cleanup done!')
	except:
		pass

def send_snapshots_to_s3():
	try:
		#########################
		# Upload snapshots to s3:
		#########################
		s3 = boto3.resource('s3', region_name='us-west-2')
		bucket = 'xxxx-dev-us-west-2-s1-snapshot'

		print('Uploading {} to s3 bucket {}...'.format(zip_file, bucket))

		date = str(datetime.now()).split()[0] # Get today's date for s3 path
		ip = sp.check_output('curl http://169.254.169.254/latest/meta-data/local-ipv4', shell=True) # Get server IP

		try:
			s3.meta.client.upload_file(zip_file, bucket, '{}{}-{}/{}/{}/ip{}-{}'.format(product, environment_name, environment_type, stack, date, ip, zip_file))
		
		except boto3.exceptions.S3UploadFailedError as e:
			print(e)
			return False
		else:
			print('{} has been uploaded to s3 bucket {} successfully!'.format(zip_file, bucket))
			return True
	except:
		pass

def main(stack, num_snapshots=3):
	create_snapshot_dir(stack)
	create_date_time_dir()
	tail_f_stack_snapshot(num_snapshots)
	output_snapshot()
	server_log_snapshot()
	sar_log_snapshot()
	var_log_snapshot()
	zipped = zip_the_snapshots()
	if zipped:
		uploaded = send_snapshots_to_s3()
		if uploaded:
			cleanup()



if __name__ == '__main__':
	main(stack, num_snapshots=num_snapshots)
