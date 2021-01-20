import os
import pwd
import logging
import shutil
import commands

class ExportWebSites:
	
	logging.basicConfig(format = '%(asctime)s %(message)s',datefmt = '%m/%d/%Y %I:%M:%S %p',filename = '/var/log/export-web-sites.log',level=logging.DEBUG)
	
	DEBUG=True
	
	moodle="moodle"
	pmb="pmb"
	jclic="jclic"
	dir_export="/etc/apache2/lliurex-location"
	mod_files=["proxy","proxy_http","proxy_html","rewrite","ext_filter"]
	mod_available="/etc/apache2/mods-available/"
	mod_enabled="/etc/apache2/mods-enabled/"
	#file_sites_configuration="/etc/apache2/sites-enabled/000-default.conf"
	
	#web_sites=[moodle,jclic,pmb]
	
	
	def create_dict(self,web_sites_vector):
		
		try:
			self.dprint("Creating dictionary for web sites....")
			resume={}
			for sites in web_sites_vector:
				resume[sites]={}
				suffix='.conf'
				site_path=os.path.join(self.dir_export, sites + suffix)
				resume[sites]["file"]=site_path
				resume[sites]["install"]=False
				self.dprint("%s : %s"%(sites,resume[sites]))
			self.dprint("Creating dictionary for web sites: %s"%resume)
			return [True,resume]
		
		except Exception as e:
			print ("[ExportWebSitesServer] %s"%e)
			self.dprint(e)
			return [False,e]
		
	#def create_dict
	
	def lprint(self,arg):
		
		logging.debug(arg)
		
	#def_lprint
	
	def dprint(self,arg):
		
		self.lprint("[ExportWebSitesServer] %s"%arg)
		if ExportWebSites.DEBUG:
			print("[ExportWebSitesServer] %s"%arg)
		
	#def dprint
	
	def export_moodle(self):
		
		try:
			self.dprint("Moodle is exporting....")
			
			# Exporting lliurex-location/moodle.conf file to external netcard
			
			if self.directory_exist(self.dir_export):
				suffix='.conf'
				site_path=os.path.join(self.dir_export, "moodle" + suffix)
				if not os.path.isfile(site_path):
					os.mknod(site_path)
					os.system('chmod 644 %s'%site_path)
					with open(site_path,'w') as file:
						
						file.write('RewriteEngine on\n')
						file.write('RewriteCond "%{REQUEST_URI}" "^/moodle$"\n')
						file.write('RewriteRule ".*" http://%{HTTP_HOST}/moodle/ [R=permament]\n')

						file.write('ExtFilterDefine rewrite_ews mode=output cmd=/usr/bin/rewrite_ews\n')

						file.write('<Location /moodle>\n')

						file.write('SetOutputFilter inflate;rewrite_ews;deflate\n')

						file.write('RewriteCond "%{REQUEST_URI}" "^/moodle/(.+)"\n')
						file.write('RewriteRule ".*" "http://moodle/%1" [P,QSA,L]\n')

						file.write('RewriteCond "%{REQUEST_URI}" "^/moodle/$"\n')
						file.write('RewriteRule ".*" "http://moodle/" [P]\n')

						file.write('RewriteRule ".*" "http:/%{REQUEST_URI}" [P]\n')

						file.write('ProxyPassReverse http://moodle\n')
						file.write('</Location>\n')

						file.write('RewriteCond %{REQUEST_URI} ^/theme/.*$\n')
						file.write('RewriteCond %{DOCUMENT_ROOT}/%{REQUEST_URI} !-f\n')
						file.write('RewriteCond %{DOCUMENT_ROOT}/%{REQUEST_URI} !-d\n')
						file.write('RewriteRule "^(.*)$" "http://%{HTTP_HOST}/moodle/%{REQUEST_URI}" [P,QSA]\n')
				
				site_path2="/usr/bin/rewrite_ews"
				if not os.path.isfile(site_path2):
					print ("[ExportWebSitesServer] Writing /usr/bin/rewrite_ews....")
					os.mknod(site_path2)
				os.system('chmod 755 %s'%site_path2)
				with open(site_path2,'w') as file:
					file.write('#!/usr/bin/python\n')
					file.write('import sys,time\n')
					file.write('from subprocess import check_output\n')
					file.write('textchars = bytearray({7,8,9,10,12,13,27}|set(range(0x20,0x100))-{0x7f})\n')
					file.write('is_bin = lambda bytes: bool(bytes.translate(None,textchars))\n')

					file.write('def get_ip():\n')
					file.write('	ipstr=check_output(["/sbin/ip","-o","route","get","8.8.8.8"])\n')
					file.write('	iplist=ipstr.split()\n')
					file.write('	ip=None\n')
					file.write('	for i in range(len(iplist)):\n')
					file.write("		if iplist[i] == 'src':\n")
					file.write('			ip = iplist[i+1]\n')
					file.write('			break\n')
					file.write('	return ip\n')

					file.write('ip=get_ip()\n')

					file.write("pattern = { 'http://moodle' : 'http://'+ip+'/moodle', 'http:\/\/moodle' : 'http:\/\/'+ip+'\/moodle', 'http%3F%2F%2Fmoodle': 'http%3F%2F%2F'+ip+'%2Fmoodle'}\n")
					file.write('replace=True\n')
					file.write('for line in sys.stdin:\n')
					file.write('	if is_bin(line):\n')
					file.write('		replace=False\n')
					file.write('	if replace:\n')
					file.write('		for p in pattern.keys():\n')
					file.write('			line=line.replace(p,pattern[p])\n')
					file.write('	sys.stdout.write(line)\n')
						
					print ("[ExportWebSitesServer] File writed.")
						
				self.dprint("/etc/apache2/lliurex-location/moodle.conf file is created to exported....")
			
			
			# Modify sites-avaiable/moodle.conf in internal netcard
			
			'''modify=True
			suffix='.conf'
			moodle_site_available=os.path.join(self.site_available, "moodle" + suffix)
			if os.path.isfile(moodle_site_available):
				with open(moodle_site_available, "r") as in_file:
							buf = in_file.readlines()
				with open(moodle_site_available, "w") as out_file:
					for line in buf:
						if  "RewriteEngine" in line:
							modify=False
						else:
							if ( "Alias /moodle" in line ) & (modify):
								line = 'RewriteEngine on\nRewriteCond "%{REQUEST_URI}" "^/moodle/(.*)$"\nRewriteRule ".*" "http://moodle/%1" [P]\n' + line
						out_file.write(line)
					
				self.dprint("/etc/apache2/sites-available/moodle.conf file modified to integer moodle in export netcard....")'''
			
			'''modify=True
			moodle_config="/usr/share/moodle/config.php"
			if os.path.isfile(moodle_config):
				with open(moodle_config, "r") as in_file:
							buf = in_file.readlines()
				with open(moodle_config, "w") as out_file:
					for line in buf:
						if  "reverseproxy" in line:
							modify=False
						else:
							if ( "$CFG->admin" in line ) & (modify):
								line = line + ' $CFG->reverseproxy = 1;\n'
						out_file.write(line)
					
				self.dprint("/usr/share/moodle/config.conf file modified to integer moodle in export netcard....")'''
				
			return [True]
		
		except Exception as e:
			print ("[ExportWebSitesServer] %s"%e)
			self.dprint(e)
			return [False,str(e)]
		
	#def export_moodle
	
	def export_jclic(self):
		
		try:
			self.dprint("JCLIC is exporting....")
			if self.directory_exist(self.dir_export):
				suffix='.conf'
				site_path=os.path.join(self.dir_export, "jclic" + suffix)
				if not os.path.isfile(site_path):
					os.mknod(site_path)
					os.system('chmod 644 %s'%site_path)
					with open(site_path,'w') as file:
						
						file.write('RewriteEngine on\n')
						file.write('RewriteCond "%{REQUEST_URI}" "^/jclic-aula$"\n')
						file.write('RewriteRule ".*" http://%{SERVER_NAME}/jclic-aula/index.php [R=permament]\n')
						file.write('RewriteRule ^ - [E=server_jclic:%{SERVER_NAME}]\n')

						file.write('<Location /jclic-aula>\n')

						file.write('RewriteCond "%{REQUEST_URI}" "^/jclic-aula/(.+)"\n')
						file.write('RewriteRule ".*" "http://jclic-aula/%1" [P,QSA,L]\n')
						file.write('RewriteCond "%{REQUEST_URI}" "^/jclic-aula/$"\n')
						file.write('RewriteRule ".*" "http://jclic-aula/" [P]\n')
						file.write('RewriteRule ".*" "http:/%{REQUEST_URI}" [P]\n')

						file.write('SetOutputFilter INFLATE;proxy-html;DEFLATE\n')
						file.write('ProxyHTMLExtended On\n')
						file.write('ProxyHTMLInterp On\n')
						
						file.write('ProxyHTMLURLMap "http://server/jclic-aula" "http://${server_jclic}/jclic-aula" V\n')
						file.write('ProxyHTMLURLMap "http://jclic-aula" "http://${server_jclic}/jclic-aula" V\n')
						file.write('ProxyHTMLURLMap "http://jclic-aula/" "http://${server_jclic}/jclic-aula/" V\n')
						file.write('ProxyHTMLURLMap "http:\/\/jclic-aula" "http:\/\/${server_jclic}/jclic-aula" x,V\n')
						file.write('ProxyHTMLURLMap "http:\/\/jclic-aula\/" "http:\/\/${server_jclic}\/jclic-aula" x,V\n')
						file.write('ProxyPassReverse http://jclic-aula\n')

						file.write('</Location>\n')


				self.dprint("Jclic file is created to exported....")
			return [True]
		
		except Exception as e:
			print ("[ExportWebSitesServer] %s"%e)
			self.dprint(e)
			return [False,str(e)]
		
	#def export_jclic
	
	def export_pmb(self):
		
		try:
			self.dprint("PMB is exporting....")
			if self.directory_exist(self.dir_export):
				suffix='.conf'
				site_path=os.path.join(self.dir_export, "pmb" + suffix)
				if not os.path.isfile(site_path):
					os.mknod(site_path)
					os.system('chmod 644 %s'%site_path)
					with open(site_path,'w') as file:
						file.write('<Location /pmb/>\n')
						file.write('	ProxyPass http://pmb:800/\n')
						file.write('	ProxyPassReverse http://pmb:800/\n')
						file.write('</Location>\n')
				site_path=os.path.join(self.dir_export, "opac" + suffix)
				if not os.path.isfile(site_path):
					os.mknod(site_path)
					os.system('chmod 644 %s'%site_path)
					with open(site_path,'w') as file:
						file.write('<Location /opac/>\n')
						file.write('	ProxyPass http://opac:800/\n')
						file.write('	ProxyPassReverse http://opac:800/\n')
						file.write('</Location>\n')
				self.dprint("PMB file is created to exported....")
			return [True]
		
		except Exception as e:
			print ("[ExportWebSitesServer] %s"%e)
			self.dprint(e)
			return [False,str(e)]
		
	#def export_pmb
	
	def un_export_moodle(self):
		
		try:
			self.dprint("Moodle is cancelling the exportation....")
			if self.directory_exist(self.dir_export):
				suffix='.conf'
				site_path=os.path.join(self.dir_export, "moodle" + suffix)
				if os.path.isfile(site_path):
					os.remove(site_path)
				self.dprint("Moodle removed !!!")
			
			# Modify sites-avaiable/moodle.conf in internal netcard
			
			modify=True
			suffix='.conf'
			moodle_site_available=os.path.join(self.site_available, "moodle" + suffix)
			if os.path.isfile(moodle_site_available):
				with open(moodle_site_available, "r") as in_file:
							buf = in_file.readlines()
				with open(moodle_site_available, "w") as out_file:
					for line in buf:
						if  not "Rewrite" in line:
							out_file.write(line)
					
				self.dprint("/etc/apache2/sites-available/moodle.conf file modified to cancel moodle in export netcard....")
			
			
			return [True]
		
		except Exception as e:
			print ("[ExportWebSitesServer] %s"%e)
			self.dprint(e)
			return [False,str(e)]
		
	#def un_export_moodle
	
	def un_export_jclic(self):
		
		try:
			self.dprint("JCLIC is cancelling the exportation....")
			if self.directory_exist(self.dir_export):
				suffix='.conf'
				site_path=os.path.join(self.dir_export, "jclic" + suffix)
				if os.path.isfile(site_path):
					os.remove(site_path)
				self.dprint("Jclic removed !!!")
			return [True]
		
		except Exception as e:
			print ("[ExportWebSitesServer] %s"%e)
			self.dprint(e)
			return [False,str(e)]
		
	#def un_export_jclic
	
	def un_export_pmb(self):
		
		try:
			self.dprint("PMB is cancelling the exportation....")
			if self.directory_exist(self.dir_export):
				suffix='.conf'
				site_path=os.path.join(self.dir_export, "pmb" + suffix)
				if os.path.isfile(site_path):
					os.remove(site_path)
				site_path=os.path.join(self.dir_export, "opac" + suffix)
				if os.path.isfile(site_path):
					os.remove(site_path)
				self.dprint("Pmb removed !!!")
			return [True]
		
		except Exception as e:
			print ("[ExportWebSitesServer] %s"%e)
			self.dprint(e)
			return [False,str(e)]
		
	#def un_export_pmb
	
	def read_export_sites(self,web_sites):
		
		try:
			self.dprint("READING export sites: %s"%web_sites)
			resume=self.create_dict(web_sites)
			if resume[0]:
				resume=resume[1]
				for service in resume:
					if os.path.exists(resume[service]["file"]):
						resume[service]["install"]=True
				self.dprint(resume)		
				return [True,resume]
			else:
				return [False]
		
		except Exception as e:
			print ("[ExportWebSitesServer] %s"%e)
			self.dprint(e)
			return [False,str(e)]
		
	#def read_export_sites
	
	
	def directory_exist(self,directory):
		try:
			self.dprint("Testing directory: %s"%directory)
			if not os.path.exists(directory):
				os.makedirs(directory)
			return [True]
		
		except Exception as e:
			print ("[ExportWebSitesServer] %s"%e)
			self.dprint(e)
			return [False,str(e)]
		
	#def directory_exist
	
	def export_active(self):
		try:
			self.dprint("Activating Exportation.....")
			for filename in self.mod_files:
				os.system('a2enmod %s'%filename)
			return [True]
		
		except Exception as e:
			print ("[ExportWebSitesServer] %s"%e)
			self.dprint(e)
			return [False,str(e)]
	#def export_active
	
	def apache2_restart(self):
		try:
			status, output = commands.getstatusoutput("systemctl restart apache2")
			self.dprint("*** APACHE2 Service ***")
			self.dprint("Status: %s"%status)
			self.dprint("Output: %s"%output)
			return [True,status,output]
		
		except Exception as e:
			print ("[ExportWebSitesServer] %s"%e)
			self.dprint(e)
			return [False,str(e)]
	# def apache2_restart
	'''
	def sites_configuration(self):
		try:
			modify=True
			path, dirs, files = next(os.walk(self.dir_export))
			number_files=len(files)
			self.dprint("*** Configuration File ***")
			if ( number_files > 0 ):
				self.dprint("Adding configuration line.....")
				if os.path.isfile(self.file_sites_configuration):
					with open(self.file_sites_configuration, "r") as in_file:
						buf = in_file.readlines()
					with open(self.file_sites_configuration, "w") as out_file:
						for line in buf:
							if  "lliurex-location" in line:
								modify=False
							else:
								if ( "<Directory /var/www/admin-center>" in line ) & (modify):
									line = "include /etc/apache2/lliurex-location/*.conf\n" + line
							out_file.write(line)
			else:
				if os.path.isfile(self.file_sites_configuration):
					self.dprint("Deleting configuration line.....")
					self.dprint("Compare this lines:")
					with open(self.file_sites_configuration, "r") as in_file:
						buf = in_file.readlines()
					with open(self.file_sites_configuration, "w") as out_file:
						for line in buf:
							self.dprint(line)
							if "lliurex-location" in line:
								self.dprint("Deleting.......!!!!!!!!!!!!")
								line = "\n"
							out_file.write(line)
				
			return [True]
		
		except Exception as e:
			print ("[ExportWebSitesServer] %s"%e)
			self.dprint(e)
			return [False,str(e)]
	'''		
	#def sites_configuration