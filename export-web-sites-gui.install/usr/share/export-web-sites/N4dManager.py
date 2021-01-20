import xmlrpc.client
import ssl
import threading
import time


class N4dManager:
	
	moodle="moodle"
	jclic="jclic"
	pmb="pmb"
	
	def __init__(self,server=None):
		
		self.debug=False
		
		self.user_validated=False
		self.client=None
		self.user_val=()
		self.validation=None

		if server!=None:
			self.set_server(server)
		
	#def init
	
	def lprint(self,validation,arg):
		
		self.client.lprint(validation,"ExportWebServices", arg)
		
	#def_lprint
	
	def mprint(self,msg):
		
		if self.debug:
			print("[ExportWebServicesN4DManager] %s"%str(msg))
			
	#def mprint
		
	
	def set_server(self,server):
		
		context=ssl._create_unverified_context()	
		self.client=xmlrpc.client.ServerProxy("https://%s:9779"%server,allow_none=True,context=context)
		self.mprint("Proxy: %s"%self.client)
		
	#def set_server
	
	
	def validate_user(self,user,password):
		
		ret=self.client.validate_user(user,password)
		self.user_validated,self.user_groups=ret
			
		
		if self.user_validated:
			self.user_val=(user,password)
		
		return [self.user_validated, self.user_val]
		
	#def validate_user
	
	def export_web_sites(self,validation,web_site):
				
		resolve=[]
		
		try:
			context=ssl._create_unverified_context()
			tmp=xmlrpc.client.ServerProxy("https://server:9779",allow_none=True,context=context)
			self.mprint("From N4D Manager calling to server to export %s"%web_site)
			if (  web_site == self.moodle ):
				resolve=tmp.export_moodle(validation,"ExportWebSites")
				if (  resolve == "USER DOES NOT EXIST" ):
					return[False,"YOUR USER[%s] CAN'T MAKE THIS CHANGES IN THE SERVER"%validation[0]]
				if resolve[0]:
					return[True,resolve]
				else:
					return[False]
					
			elif(  web_site == self.jclic ):
				resolve=tmp.export_jclic(validation,"ExportWebSites")
				if (  resolve == "USER DOES NOT EXIST" ):
					return[False,"YOUR USER[%s] CAN'T MAKE THIS CHANGES IN THE SERVER"%validation[0]]
				#self.mprint(resolve)
				if resolve[0]:
					return[True,resolve]
				else:
					return[False]
					
			elif(  web_site == self.pmb ):
				resolve=tmp.export_pmb(validation,"ExportWebSites")
				if (  resolve == "USER DOES NOT EXIST" ):
					return[False,"YOUR USER[%s] CAN'T MAKE THIS CHANGES IN THE SERVER"%validation[0]]
				#self.mprint(resolve)
				if resolve[0]:
					return[True,resolve]
				else:
					return[False]
	
		except Exception as e:
			print ("[ExportWebServicesN4DManager] ERROR: %s"%e)
			self.lprint (validation,"[ExportWebServicesN4DManager] %s"%e)
			return [False,str(e)]	
		
	#def export_web_sites
	
	def un_export_web_sites(self,validation,web_site):
				
		resolve=[]
		
		try:
			context=ssl._create_unverified_context()
			tmp=xmlrpc.client.ServerProxy("https://server:9779",allow_none=True,context=context)
			self.mprint("From N4D Manager calling to server to cancel the exportation %s"%web_site)
			if (  web_site == self.moodle ):
				resolve=tmp.un_export_moodle(validation,"ExportWebSites")
				if (  resolve == "USER DOES NOT EXIST" ):
					return[False,"YOUR USER[%s] CAN'T MAKE THIS CHANGES IN THE SERVER"%validation[0]]
				if resolve[0]:
					return[True,resolve]
				else:
					return[False]
					
			elif(  web_site == self.jclic ):
				resolve=tmp.un_export_jclic(validation,"ExportWebSites")
				#self.mprint(resolve)
				if (  resolve == "USER DOES NOT EXIST" ):
					return[False,"YOUR USER[%s] CAN'T MAKE THIS CHANGES IN THE SERVER"%validation[0]]
				if resolve[0]:
					return[True,resolve]
				else:
					return[False]
					
			elif(  web_site == self.pmb ):
				resolve=tmp.un_export_pmb(validation,"ExportWebSites")
				#self.mprint(resolve)
				if (  resolve == "USER DOES NOT EXIST" ):
					return[False,"YOUR USER[%s] CAN'T MAKE THIS CHANGES IN THE SERVER"%validation[0]]
				if resolve[0]:
					return[True,resolve]
				else:
					return[False]
	
		except Exception as e:
			print ("[ExportWebServicesN4DManager] ERROR: %s"%e)
			self.lprint (validation,"[ExportWebServicesN4DManager] %s"%e)
			return [False,str(e)]	
		
	#def un_export_web_sites
	
	def read_export_sites(self,validation,web_sites):
		
		try:
			context=ssl._create_unverified_context()
			tmp=xmlrpc.client.ServerProxy("https://server:9779",allow_none=True,context=context)
			self.mprint("Reading inital state in server....")
			resolve=tmp.read_export_sites(validation,"ExportWebSites",web_sites)
			self.mprint("Solved: %s"%resolve)
			if resolve[0]:
				return[True,resolve[1]]
			else:
				return[False,resolve[1]]
	
		except Exception as e:
			print ("[ExportWebServicesN4DManager] ERROR: %s"%e)
			self.lprint (validation,"[ExportWebServicesN4DManager] %s"%e)
			return [False,str(e)]	
		
	#def read_export_sites
	
	
	def export_active(self,validation):
		
		try:
			context=ssl._create_unverified_context()
			tmp=xmlrpc.client.ServerProxy("https://server:9779",allow_none=True,context=context)
			self.mprint("Does Server have mod-enabled to export sites?")
			resolve=tmp.export_active(validation,"ExportWebSites")
			return[resolve]
	
		except Exception as e:
			print ("[ExportWebServicesN4DManager] ERROR: %s"%e)
			self.lprint (validation,"[ExportWebServicesN4DManager] %s"%e)
			return [False,str(e)]	
		
	#def export_active
	
	def apache2_restart(self,validation):
		
		try:
			context=ssl._create_unverified_context()
			tmp=xmlrpc.client.ServerProxy("https://server:9779",allow_none=True,context=context)
			self.mprint("Restarting Apache 2 service")
			resolve=tmp.apache2_restart(validation,"ExportWebSites")
			self.mprint(resolve)
			return resolve
	
		except Exception as e:
			print ("[ExportWebServicesN4DManager] ERROR: %s"%e)
			self.lprint (validation,"[ExportWebServicesN4DManager] %s"%e)
			return [False,str(e)]	
		
	#def apache2_restart
	'''
	def sites_configuration(self,validation):
		
		try:
			context=ssl._create_unverified_context()
			tmp=xmlrpc.client.ServerProxy("https://server:9779",allow_none=True,context=context)
			self.mprint("Restarting Apache 2 service")
			resolve=tmp.sites_configuration(validation,"ExportWebSites")
			self.mprint(resolve)
			return resolve
	
		except Exception as e:
			print ("[ExportWebServicesN4DManager] ERROR: %s"%e)
			self.lprint (validation,"[ExportWebServicesN4DManager] %s"%e)
			return [False,str(e)]	
	'''	
	#def sites_configuration
			