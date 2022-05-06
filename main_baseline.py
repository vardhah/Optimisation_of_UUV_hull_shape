import argparse
import os
import numpy as np
from utils import *
import pandas as pd
import shutil
import glob 
import subprocess
import time
#from run_dexof import *
import sys 
from cfd_sim.run_dexof import run_dex
from cfd_sim.dexof_reader_class import parse_dex_file
import GPyOpt


sys.dont_write_bytecode = True



input_size=2                             # input size may change if integer/ordinal type variable and represented by one-hot encoding
cad_storage_name= './cad_sim/design_points.csv'
cfd_storage_name= './cfd_sim/design_points.csv'

num_iteration=20                        # Number of iteration of sampling
init_samples=50 
budget_samples=50                        # Number of samples-our budget
ranges=[-10,0,-6.5,0]                    # ranges in form of [low1,high1,low2,high2,...]

src= './cad_sim/stl_repo'
dst='./cfd_sim/stl_cfd'


def delete_dir(loc):
    print('*Deleted directory:',loc)
    shutil.rmtree(loc)

def copy_dir(src,dst):
	print('*Copied directory from',src,'to destination:',dst)
	shutil.copytree(src, dst)

def deletefiles(loc):
	print('Deleted files from location:',loc)
	file_loc= loc+'/*'
	files = glob.glob(file_loc)
	for f in files:
		os.remove(f)

def copy_file(src,dst):
	print('*Copied file from',src,'to destination:',dst)
	shutil.copy(src, dst)

def save_design_points(x):
    np.savetxt(cad_storage_name,x,  delimiter=',')
    #np.savetxt(cfd_storage_name,x,  delimiter=',')

def run_cad_cfd(x):
	save_design_points(x)

	delete_dir(dst)
	subprocess.call('./cad_sim/run_cad.sh')
	copy_file(cad_storage_name,cfd_storage_name)
	copy_dir(src,dst)
	deletefiles(src)
	prev = os.path.abspath(os.getcwd()) # Save the real cwd
	print('prev is',prev)
	cfd_sim_path= prev+'/cfd_sim'
	print('func path is:',cfd_sim_path)
	os.chdir(cfd_sim_path)
	result = run_dex()
	os.chdir(prev)
	return result


if __name__=='__main__':
	
	############################
	data_file_name='lhc_minimax.csv'   
	b=654;D=191;
	dim=4;n=100
	#################################################
	#given b & D => need to find a,c,n,theta
	ranges=[10,3*D,10,3*D,10,50,1,50]    
    
	already_run = len(glob.glob(data_file_name))
	print('file exist?:',already_run)
	if already_run==1:
	    multi_runresults=np.loadtxt(data_file_name, delimiter=",",skiprows=0, dtype=np.float32)
	    multi_runresults= np.atleast_2d(multi_runresults)
	    #print('shape of multi_runresults:',multi_runresults.shape)
	max_iter  = 1
	#################################

	for i in range(max_iter):
		#ds= random_sampling(dim,n,ranges)
		ds= lhc_samples_maximin(n,dim,ranges)  #maximin LHC
		#ds= lhc_samples_corr(n,dim,ranges)     # Correlated LHC
		print('ds is:',ds.shape[0])
		for i in range(ds.shape[0]):
		 already_run = len(glob.glob(data_file_name))	
		 design_point= ds[i]	
		 print('design point is:',design_point)
		 fd=run_cad_cfd(design_point)
		 #fd=10
		 #print('fd is:',fd)
		 
		 if already_run==0:
		   multi_runresults= fd
		 else:
		   multi_runresults= np.concatenate((multi_runresults,fd),axis=0)
		 #print('multirun result:',multi_runresults)
		 np.savetxt(data_file_name,multi_runresults,  delimiter=',')
         
	

