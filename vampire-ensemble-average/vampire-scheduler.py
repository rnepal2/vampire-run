# This program creates input files for the vampire scripts in different 
# folders and those programs are submitted in parallel. This script is
# written for the ensemble averaging i.e. running the same program for 
# N times and taking average of the ouputs. We calculate the magnon current
# correlators out of the ouput of this averaging. Only random number in the
# vampire input file is changed in each of the ensemble, rest of the paramters 
# are same in all the files - input, material.mat and kagome.ucf files.
# We can change other parameters according requirement through replace files
# in the program below.

import math
import os, sys
from joblib import Parallel, delayed
import random 

# Creating vampire input and material files with different randomSeed
def createInputFiles(N):
	inputTemplate = open("input-template", "rt").read()
	matTemplate = open("material-template.mat", "rt").read()
	ucfTemplate = open("kagome.ucf", "rt").read()
	vampire_files_dir = []
	for i in range(N):
		# Create directories to place input and material files
		input_dir_path = '/home/rabindra/EnsembleAveraging/' + 'ensemble-{}/'.format(i)
		if not os.path.exists(input_dir_path):
			os.makedirs(input_dir_path)
		replaceInput = {"randomSeed": random.randint(0,1000000)}
		replaceMaterial = {}
		replaceUCF = {}
		inputFileName = input_dir_path + 'input'
		materialFileName = input_dir_path + 'material.mat'
		ucfFileName = input_dir_path + 'kagome.ucf'
		#Creating the required vampire files for each ensemble
		with open(inputFileName, "wt") as input_file:
			input_file.write(inputTemplate % replaceInput)	
		input_file.close()
		
		with open(materialFileName, "wt") as material_file:
			material_file.write(matTemplate % replaceMaterial)
		material_file.close()
		
		with open(ucfFileName, "wt") as ucf_file:
			ucf_file.write(ucfTemplate % replaceUCF)
		ucf_file.close()
		
		vampire_files_dir.append(input_dir_path)
	return vampire_files_dir

# To avoid printing long vampire default run message on terminal
def block_terminal_message():
	sys.stdout = open(os.devnull, 'w')

def enable_terminal_message():
	sys.stdout = sys.__stdout__

# Runs a single vampire script file
def run_vampire_script(script):
	# printing the running vampire file
	script_path = script.split("/")
	ensemble_to_run = script_path[4]
	print("Running vampire script for: ", ensemble_to_run)
	# Running the vampire input file
	block_terminal_message()
	os.system("cd " + script + "&&" + "nice -n 20 vampire-serial")
	enable_terminal_message()

# Dispatch parallel mumax3 jobs
def dispatchingJobs(total_jobs, batch_num):
	input_dir_list =  createInputFiles(total_jobs)
	print("Dispatching parallel jobs.....")
	Parallel(n_jobs=total_jobs, batch_size=batch_num, verbose=batch_num)
			(delayed(run_vampire_script)(script) for script in input_dir_list)		
	# verbose=batch_num => prints the progress after each batch is done!
	
	
total_jobs = int(input("Number of ensembles to average over: "))
batch_num = int(input("Number of batches to run (should be = N/(Number of cores to assign)): "))
dispatchingJobs(total_jobs, batch_num)
# Finished
print("Program completed successfully!")