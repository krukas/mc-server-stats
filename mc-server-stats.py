#!/usr/bin/env python
# Show mincraft server stats from te server.log file.
# Copyright (C) 2012 Maikel Martens
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import time
import datetime
import re
import math

#########################################################################################
# Minecraft CLASS
#########################################################################################
class Minecraft:
    
	def __init__(self):
		self.logfile = ""
		self.users = {}
		self.started = 0
		self.totaltime = 0
		self.serverfirststarted = 0
		self.serverlastclosed = 0

	#Start the proces
	def getStats(self):
		try:
			file = open(self.logfile, 'r')
		except IOError as e:
			return 0
		
		data = file.readlines()

		#Go through every line in the server.log
		for line in data:
			#Check if server started
			if re.match('([0-9-]+ [0-9:]+) \[INFO\] Starting minecraft server',line):
				result = re.match('([0-9-]+ [0-9:]+) \[INFO\] Starting minecraft server',line)
				self.serverStarted(result.group(1))
			
			#Check if player login
			elif re.match('([0-9-]+ [0-9:]+) \[INFO\] ([a-zA-Z0-9-_]+) ?\[.*logged in with entity',line):
				result = re.match('([0-9-]+ [0-9:]+) \[INFO\] ([a-zA-Z0-9-_]+) ?\[.*logged in with entity',line)
				self.online(result.group(2), result.group(1))
			
			#Check if user logs.out
			elif re.match('([0-9-]+ [0-9:]+) \[INFO\] ([a-zA-Z0-9-_]+) lost connection',line):
				result = re.match('([0-9-]+ [0-9:]+) \[INFO\] ([a-zA-Z0-9-_]+) lost connection',line)
				self.offline(result.group(2), result.group(1))
			
			#Check if server stoped
			elif re.match('([0-9-]+ [0-9:]+) \[INFO\] Stopping server',line):
				result = re.match('([0-9-]+ [0-9:]+) \[INFO\] Stopping server',line)
				self.serverStoped(result.group(1))

		#Call last line to close all users and server
		result = re.match('([0-9-]+ [0-9:]+)',data[len(data)-1])
		self.serverStoped(result.group(0))
		self.serverlastclosed = self.timestamp(result.group(0))
		file.close()

		#display the stats
		self.display()
		return 1

	#Sets the logfile location
	def setLogFile(self,log):
		self.logfile = log

	#Add new user to the dictionary
	def addUser(self, name, time):
		stamp = self.timestamp(time)
		self.users[name] = {
			'name' 			: name,
			'online' 		: stamp,
			'lastonline'	: stamp,
			'logcount'		: 1,
			'totaltime'		: 0
			}

	#Sets user online and lastonline when user not exists call addUser
	def online(self, name, time):
		if not self.users.has_key(name):
			self.addUser(name, time)
		else:
			stamp = self.timestamp(time)
			self.users[name]['logcount'] += 1
			self.users[name]['online'] = stamp
			self.users[name]['lastonline'] = stamp

	#Sets user offline, calculate and add user playing time 
	def offline(self, name, time):
		if self.users[name]['online'] == 0:
			return
		if self.users.has_key(name):
			stamp = self.timestamp(time)
			self.users[name]['totaltime'] += stamp - self.users[name]['online']
			self.users[name]['online'] = 0

	#Sets the time for when server started and first started
	def serverStarted(self, time):
		stamp = self.timestamp(time)
		if self.serverfirststarted == 0:
			self.serverfirststarted = stamp
		self.started = stamp

	#Calculate and add running server time, sets every user to offline
	def serverStoped(self, time):
		stamp = self.timestamp(time)
		if self.started > 0:
			self.totaltime += stamp - self.started
		self.started = 0
		for user in self.users:
			if self.users[user]['online'] > 0:
				self.offline(user, time)

	#Generate timestamp from the data out of the log file
	def timestamp(self, data):
		year = int(data[:4])
		month = int(data[5:7])
		day = int(data[8:10])
		hours = int(data[11:13])
		minutes = int(data[14:16])
		seconds = int(data[17:19])

		dateTime = datetime.datetime(year, month, day, hours, minutes, seconds)
		return int(time.mktime(dateTime.timetuple()))

	####################################################################################
	# Functions for displaying the stats
	####################################################################################
	#Convert unix timestamp to readable data and time
	def displayTime(self, time):
		return datetime.datetime.fromtimestamp(int(time)).strftime('%Y-%m-%d %H:%M:%S')

	#Calculate the uptime percentage
	def uptime(self, total, running):
		 return int((float(running) / float(total))*100)

	#convert the seconds in readable time
	def sec2Time(self, time):
	 	string = ""
	 	if time >= 31556926:
	 		value = int(math.floor(time/31556926))
	 		if value == 1:
	 			string += str(value)+' year, '
	 		else:
	 			string += str(value)+' years, '
 			time = (time%31556926)
			if time >= 86400:
				value = int(math.floor(time/86400))
				if value == 1:
					string += str(value)+' day, '
				else:
					string += str(value)+' days, '
				time = (time%86400)
			if time >= 3600:
				value = int(math.floor(time/3600))
				if value == 1:
					string += str(value)+' hour, '
				else:
					string += str(value)+' hours, '
				time = (time%3600)
			if time >= 60:
				value = int(math.floor(time/60))
				if value == 1:
					string += str(value)+' minute, '
				else:
					string += str(value)+' minutes, '
			time = (time%60)

		return string+str(time)+' seconds'

	#Display the stats in terminal	
	def display(self):
		print("######################################################################")
		print("# Server Stats")
		print("######################################################################")
		print('')
		print('Server has been running since: '+self.displayTime(self.serverfirststarted))
		print('Server uptime: '+str(self.sec2Time(self.totaltime)))
		print('Server uptime percentage: '+str( self.uptime( (self.serverlastclosed - self.serverfirststarted), self.totaltime)))+'%'
		print('')
		print('#######################################################################')
		print('# Player stats ')
		print('#######################################################################')
		print('')
		for user in self.users:
			data = self.users[user]
			print('Player: '+data['name'])
			print('Time played: '+str(self.sec2Time(data['totaltime'])))
			print('Last online: '+str(self.displayTime(data['lastonline'])))
			print('Times logged in: '+str(data['logcount']))
			print('----------------------------------------------------------------------')
		print('')
		print('Script by Maikel Martens')
		print('Github: https://github.com/krukas/mc-server-stats')
		print('Website: http://maikel.me')
		print('')



#########################################################################################
# Running script
#########################################################################################
print('')  
print('Minecraft Server Stats Copyright (C) 21012 Maikel Martens')
print('This program comes with ABSOLUTELY NO WARRANTY;')
print('This is free software, and you are welcome to redistribute it')
print('under certain conditions;')  
print('')  
mc = Minecraft()
fileLocation = raw_input("Minecraft server.log location: ")
mc.setLogFile(fileLocation)
while not mc.getStats():
	print('')
	print('Could not open file!')
	print('')
	fileLocation = raw_input("Minecraft server.log location: ")
	mc.setLogFile(fileLocation)