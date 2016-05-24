import glob
import numpy as np
from subprocess import call
import re
import os

# Constants
M_Earth_g = 5.97e27
R_Earth_cm =6.37e8

M_Sun_g = 1.99e33
R_Sun_cm = 6.96e10

LSun_erg_s = 3.9e33
TSun_K = 5.78e3

AU_cm = 1.496e13

F_Earth_erg_cm2s =  LSun_erg_s /  AU_cm**2 / 4.  /  np.pi

who =os.popen("whoami") 
if who.readline().strip() =='samuelhadden':
	print "On laptop..."
	topdir = "/Users/samuelhadden/26_MESA/"
	work_dir = topdir+"/mesa-r8118/star/work"
	inlists_dir = topdir+"Planets_With_MESA/PlanetModelInlistFiles"
else:
	print "On Quest..."
	topdir = "/projects/p20783/sjh890/"
	work_dir = topdir+"/mesa/star/work"
	inlists_dir = topdir+"/01_MESA_Projects/Planets_With_MESA/PlanetModelInlistFiles"
who.close()


def line_read(finame):
	with open(finame,"r") as fi:
		return fi.readlines()

	

class PlanetModel(object):

	
	def __init__(self, directory , name, total_mass, core_mass,core_density, flux, age):

		self._INLIST = ""
		self._DIR = directory

		self._CREATE_MODEL =  name + "_create.mod"
		self._CREATE_MODEL = "'"+self._CREATE_MODEL+"'"

		self._CORE_MODEL =  name + "_core.mod"
		self._CORE_MODEL = "'"+self._CORE_MODEL+"'"

		self._MASS_RELAX_MODEL = name + "_mass_relax.mod"
		self._MASS_RELAX_MODEL = "'"+self._MASS_RELAX_MODEL+"'"

		self._EVOLVE_MODEL = name + "_evolve.mod"
		self._EVOLVE_MODEL = "'"+self._EVOLVE_MODEL+"'"

		self._INITIAL_RADIUS = 20.0 * R_Earth_cm
		self._INITIAL_MASS = np.max([ total_mass  , 1.0e-4 * M_Sun_g] )

		self._PLANET_MASS  = total_mass * M_Earth_g / M_Sun_g
		self._CORE_MASS = core_mass * M_Earth_g / M_Sun_g 

		self._CORE_DENSITY = core_density

		self._FLUX = flux * F_Earth_erg_cm2s 
		
		self._AGE = age

		self._Z = 0.02
		self._Y = 0.25
		self._RADIATION_COLUMN_DEPTH = 10.
	
		self.Reset_Property_Dictionary()
		

	def Reset_Property_Dictionary(self):
		self.Property_Dictionary ={\
				"INLIST":self._INLIST,\
				"CREATE_MODEL":self._CREATE_MODEL,\
				"CORE_MODEL":self._CORE_MODEL,\
				"MASS_RELAX_MODEL":self._MASS_RELAX_MODEL,\
				"EVOLVE_MODEL":self._EVOLVE_MODEL,\
				"INITIAL_RADIUS":self._INITIAL_RADIUS,\
				"INITIAL_MASS":self._INITIAL_MASS,\
				"PLANET_MASS":self._PLANET_MASS,\
				"CORE_MASS":self._CORE_MASS,\
				"CORE_DENSITY":self._CORE_DENSITY,\
				"FLUX":self._FLUX,\
				"AGE":self._AGE,\
				"Z":self._Z,\
				"Y":self._Y,\
				"RADIATION_COLUMN_DEPTH":self._RADIATION_COLUMN_DEPTH\
				}

	def SetCreateModel(self,model):
		self._CREATE_MODEL = model
		self.Reset_Property_Dictionary()
		self.ResetInlists()
	def SetCoreModel(self,model):
		self._CORE_MODEL = model
		self.Reset_Property_Dictionary()
		self.ResetInlists()
	def SetMassRelaxModel(self,model):
		self._MASS_RELAX_MODEL = model
		self.Reset_Property_Dictionary()
		self.ResetInlists()
	def SetEvolveModel(self,model):
		self._EVOLVE_MODEL = model
		self.Reset_Property_Dictionary()
		self.ResetInlists()

	
	def SubstitutePropertyInString(self,string):
		match= re.search("<<(\w+)>>",string)
		if match:
			property_value = self.Property_Dictionary[match.groups()[0]]
			return re.sub("<<\w+>>",str(property_value),string)
		else:
			return string


	def SetupDirectory(self):
		command= ["cp","-r", work_dir , self._DIR ]
		call(command)
		self.ResetInlists()
		for fi in glob.glob(inlists_dir+"/*columns.list" ):
			command= ["cp", fi, self._DIR ]
			call(command)
			
	def ResetInlists(self):
		inlists = ['inlist','inlist_create','inlist_core','inlist_mass_relax','inlist_evolve']
		for inlist in inlists:
			lines = map(self.SubstitutePropertyInString,line_read(inlists_dir+"/"+inlist))
			with open(self._DIR+"/"+inlist,"w") as fi:
				for l in lines:
					fi.write(l)

		
	def SetCurrentInlist(self,inlist):
		self._INLIST = "'"+inlist+"'"
		self.Property_Dictionary["INLIST"]=self._INLIST
		lines = map(self.SubstitutePropertyInString,line_read(inlists_dir+"/inlist"))
		with open(self._DIR+"/inlist","w") as fi:
			for l in lines:
				fi.write(l)
	
	def Create(self):
		self.SetCurrentInlist("inlist_create")		
		cwd = os.getcwd()		
		os.chdir(self._DIR)
		call(["./mk"])
		call(["./rn"])		
		os.chdir(cwd)
	def Core(self):
		self.SetCurrentInlist("inlist_core")		
		cwd = os.getcwd()		
		os.chdir(self._DIR)
		call(["./mk"])
		call(["./rn"])		
		os.chdir(cwd)
	def RelaxMass(self):
		self.SetCurrentInlist("inlist_mass_relax")		
		cwd = os.getcwd()		
		os.chdir(self._DIR)
		call(["./mk"])
		call(["./rn"])
		os.chdir(cwd)
	def Evolve(self):
		self.SetCurrentInlist("inlist_evolve")
		cwd = os.getcwd()		
		os.chdir(self._DIR)
		call(["./mk"])
		call(["./rn"])		
		os.chdir(cwd)
