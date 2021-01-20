#!/usr/bin/env python
# -*- coding: utf-8 -*

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango, GdkPixbuf, Gdk, Gio, GObject,GLib

import signal
import gettext
import sys
import threading
import copy
import subprocess
import os
import N4dManager
import xmlrpc.client
import ssl
import time
#import ExportWebSitesServer

signal.signal(signal.SIGINT, signal.SIG_DFL)
gettext.textdomain('export-web-sites-gui')
_ = gettext.gettext




class ExportWebSites:
	

	
	#log="/var/log/home_eraser.log"
	
	# ********HACKKKKKK
	#server="server"
	moodle="moodle"
	jclic="jclic"
	pmb="pmb"
	web_sites=[moodle,jclic,pmb]
	initial_state=[]
	apache_error=False
	
	DEBUG=False
	
	def dprint(self,arg):
		#self.n4d_man.lprint(self.user_val, "[ExportWebSitesGUI] %s"%arg)
		if ExportWebSites.DEBUG:
			print("[ExportWebSitesGUI] %s"%arg)
		
	#def dprint	
	
	
	def __init__(self,args_dic):
		
		self.n4d_man=N4dManager.N4dManager()
		#self.n4d_man.set_server(args_dic[self.server])
		
		if args_dic["gui"]:
			
			self.start_gui()
			GObject.threads_init()
			Gtk.main()
		
	#def __init__(self):
	
	
	def start_gui(self):

		builder=Gtk.Builder()
		builder.set_translation_domain('export-web-sites')
		builder.add_from_file("/usr/share/export-web-sites/rsrc/export-web-sites.ui")
		self.main_window=builder.get_object("main_window")
		self.main_window.set_icon_from_file('/usr/share/export-web-sites/rsrc/export-web-sites-icon.svg')

		self.main_box=builder.get_object("main_box")
		self.login_box=builder.get_object("login_box")
		self.main_content_box=builder.get_object("main_content_box")
		
		self.stack=Gtk.Stack()
		self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
		self.stack.set_transition_duration(500)
		self.stack.add_titled(self.login_box,"login","login")
		self.stack.add_titled(self.main_content_box,"main","main")
		
		self.stack.show_all()
		
		self.main_box.pack_start(self.stack,True,True,5)
		
		self.login_button=builder.get_object("login_button")
		self.entry_user=builder.get_object("entry1")
		self.entry_password=builder.get_object("entry2")
		self.entry_server=builder.get_object("entry3")
		self.login_msg_label=builder.get_object("login_msg_label")
		
		#self.separator3 = builder.get_object("separator3")
		#self.separator4 = builder.get_object("separator4")
		
		self.switch_moodle = builder.get_object("checkbutton1")
		self.switch_jclic = builder.get_object("checkbutton2")
		#self.switch_jclic.set_sensitive(False)
		self.switch_pmb = builder.get_object("checkbutton3")
		
		self.apply_button=builder.get_object("apply_button")
		self.txt_apply=builder.get_object("txt_apply")
		self.spinner=builder.get_object("spinner")
		
		self.set_css_info()
		
		self.connect_signals()
		self.main_window.show()
		
		self.apply_button.set_sensitive(False)
		
	#def start_gui
	
	def set_css_info(self):
		
		self.style_provider=Gtk.CssProvider()
		f=Gio.File.new_for_path("/usr/share/export-web-sites/ExportWebSites.css")
		self.style_provider.load_from_file(f)
		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),self.style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		self.main_window.set_name("WINDOW")
		
		self.apply_button.set_name("OPTION_BUTTON")
		self.login_button.set_name("OPTION_BUTTON")
			
	#def set-css_info
	
	
	def connect_signals(self):
			
		self.main_window.connect("destroy",Gtk.main_quit)
		
		self.apply_button.connect("clicked",self.apply_button_clicked)
		
		self.login_button.connect("clicked",self.login_clicked)
		self.entry_password.connect("activate",self.entries_press_event)
		self.entry_server.connect("activate",self.entries_press_event)
		
		self.switch_moodle.connect("notify::active",self.activate_apply_button)
		self.switch_pmb.connect("notify::active",self.activate_apply_button)
		self.switch_jclic.connect("notify::active",self.activate_apply_button)
		
	#def connect_signals

	# SIGNALS #######################################################	
	
	def entries_press_event(self,entry):
		
		self.login_clicked(None)
		
	#def entries_press_event
	
	def activate_apply_button(self,entry,event):
		
		self.apply_button.set_sensitive(True)
		self.txt_apply.set_markup("")
		
	#def activate_apply_button
	
	def login_clicked(self,button):
		
		self.login_button.set_sensitive(False)
		self.login_msg_label.set_text(_("Validating user..."))
		
		user=self.entry_user.get_text()
		password=self.entry_password.get_text()
		#user="netadmin"
		#password="lliurex"
		self.user_val=(user,password)
		server=self.entry_server.get_text()
		
		self.n4d_man.set_server(server)
		
		self.validate_user(user,password)
		# HACKED DELETE THIS LINE and delete commnet before
		#self.initial_state=self.n4d_man.read_export_sites(self.user_val,self.web_sites)
		#self.dprint(self.initial_state[1])
		#for service in self.web_sites:
		#	self.dprint("Testing if is active service: %s "%service)
		#	self.dprint(self.initial_state[1][service])
		#	state=self.initial_state[1][service]["install"]
		#	exec("self.switch_%s.set_active(state)"%service)
		#self.apply_button.set_sensitive(False)
		
		#self.stack.set_visible_child_name("main")
		
	#def login_clicked
	
	def validate_user(self,user,password):
		
		t=threading.Thread(target=self.n4d_man.validate_user,args=(user,password,))
		t.daemon=True
		t.start()
		GLib.timeout_add(500,self.validate_user_listener,t)
		
	#def validate_user
	
	def validate_user_listener(self,thread):
			
		if thread.is_alive():
			return True
				
		
		if not self.n4d_man.user_validated:
			self.login_msg_label.set_markup("<span foreground='red'>"+_("Invalid user, please only net admin users.")+"</span>")
			self.login_button.set_sensitive(True)
		else:
			group_found=False
			for g in ["admins"]:
				if g in self.n4d_man.user_groups:
					group_found=True
					break
					
			if group_found:

				# ***START LOG
				self.dprint("")
				self.dprint("** START EXPORT WEB SITES GUI **")
				self.dprint("   ---------------------")
				self.dprint("")
				self.initial_state=self.n4d_man.read_export_sites(self.user_val,self.web_sites)
				self.dprint(self.initial_state[1])
				for service in self.web_sites:
					self.dprint("Testing if is active service: %s "%service)
					self.dprint(self.initial_state[1][service])
					state=self.initial_state[1][service]["install"]
					exec("self.switch_%s.set_active(state)"%service)
				self.apply_button.set_sensitive(False)
				self.stack.set_visible_child_name("main")
				# ##########
				
				self.stack.set_visible_child_name("main")
				
			else:
				self.login_msg_label.set_markup("<span foreground='red'>"+_("Invalid user, please only netadmin users.")+"</span>")
				self.login_button.set_sensitive(True)
		
	#validate_user_listener



	
	def apply_button_clicked(self,widget=True):
		
		try:			
			self.apply_button.set_sensitive(False)
			self.switch_moodle.set_sensitive(False)
			self.switch_jclic.set_sensitive(False)
			self.switch_pmb.set_sensitive(False)
				
			export={}
			export[self.moodle]=False
			export[self.jclic]=False
			export[self.pmb]=False
			
			self.dprint("")
			self.dprint("RESUME APPLY")
			self.dprint("-------------")
			export[self.moodle]=self.switch_moodle.get_active()
			if export[self.moodle]:
				self.dprint("Export Moodle....")
			else:
				self.dprint("Unexport Moodle....")
			export[self.jclic]=self.switch_jclic.get_active()
			if export[self.jclic]:
				self.dprint("Export jclic")
			else:
				self.dprint("Unexport Jclic....")
			export[self.pmb]=self.switch_pmb.get_active()
			if export[self.pmb]:
				self.dprint("Export pmb")	
			else:
				self.dprint("Unexport Pmb....")
			
			self.dprint("")
			
			self.apply_export_web_sites_thread(export)
			
		except Exception as e:
			self.dprint(e)
			print ("[ExportWebSitesGUI] %s"%e)
			return [False,str(e)]
		
	#def check_changes
	
	
	
	def apply_export_web_sites_thread(self,export):
		
		t=threading.Thread(target=self.apply_export_web_sites,args=(export,))
		t.daemon=True
		t.start()
		self.spinner.start()
		GLib.timeout_add(500,self.sure_export,t)
		
	#apply_delete_methods_thread
	
		
	def sure_export(self,thread):
		
		try:
			if thread.is_alive():
				self.apply_button.set_sensitive(False)
				return True
			
			self.switch_moodle.set_sensitive(True)
			self.switch_jclic.set_sensitive(True)
			self.switch_pmb.set_sensitive(True)
				
			self.spinner.stop()
			if self.apache_error:
				self.txt_apply.set_markup("<span foreground='red'>"+_("Apache service fails. Log is found in /var/log/export-web-sites.log ")+"</span>")
			else:
				self.txt_apply.set_markup("<span foreground='blue'>"+_("Finished. Log is found in /var/log/export-web-sites.log ")+"</span>")
			
			#Gtk.main_quit()
			#sys.exit(0)
			
		except Exception as e:
			self.dprint(e)
			print ("[ExportWebSitesGUI] %s"%e)
			return [False,str(e)]
		
	#def_sure_delete
		
	
	
	def apply_export_web_sites(self,export):
		
		try:
			exec_error=False
			resume={}
			resume[self.moodle]=[]
			resume[self.jclic]=[]
			resume[self.pmb]=[]
			export_service=False
			restart_apache=False
			
			self.dprint("---------------------WORKING---------------------------")
			
			for service in self.web_sites:
				self.dprint("Service: %s "%service)
				#self.dprint(self.initial_state[1][service])
				state=self.initial_state[1][service]["install"]
				
				if ( state != export[service] ):
					self.dprint("Operating in server....")
					if export[service]:
						self.dprint("Calling N4D to export %s"%service)
						resume[service]=self.n4d_man.export_web_sites(self.user_val,service)
						export_service=True
						restart_apache=True
					else:
						self.dprint("Calling N4D to remove %s"%service)
						resume[service]=self.n4d_man.un_export_web_sites(self.user_val,service)
						restart_apache=True
					if resume[service][0]:
						self.dprint("Work in server, did it.")
					else:
						self.dprint("Something wrong")
						exec_error=True
				else:
					self.dprint("Do nothing")
			
			if export_service:
				if self.n4d_man.export_active(self.user_val)[0]:
					self.dprint("Apache Export Service is avaiable")
				else:
					self.dprint("Error with Apache Export Service")
					
			if self.n4d_man.sites_configuration(self.user_val)[0]:
				self.dprint("Sites-configuration is configured")
			else:
				self.dprint("Error Sites-configuration")
			
			
			if restart_apache:
				apache2_restart=self.n4d_man.apache2_restart(self.user_val)
				self.dprint(apache2_restart)
				if ( apache2_restart[2] == "" ):
					self.dprint("Apache Service has been restarted")
				else:
					self.apache_error=True
					self.dprint("Apache Service has a problem please contact with adminsitrator")
					self.dprint("Apache Service Status: %s"%apache2_restart[1])
					self.dprint("Apache Service Error: %s"%apache2_restart[2])
			
			self.dprint("")
			self.dprint("---------------------RESUME---------------------------")
			
			self.initial_state=self.n4d_man.read_export_sites(self.user_val,self.web_sites)
			self.dprint("---------------------FINISHED---------------------------")
			self.dprint("")
			return[True,resume,exec_error]
					
		except Exception as e:
			self.dprint(e)
			print ("[ExportWebSitesGUI] %s"%e)
			return [False,str(e)]
		
		
	#def_apply_delete_methods


#class LliurexPerfilreset


if __name__=="__main__":
	
	pass
	
