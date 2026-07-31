#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pDynamoWrapper.pDynamoWrapper import Wrapper

import os,sys


#======================================================
def PrepareSystems(_variation= "ACO"):

    '''
    This functions prepares the systems for QM/MM simulations, by setting up the system parameters and saving the system objects for each variation of the system. The variations include:
    '''

    _parameters = {
		"Input_Type":"amber",
		"crd_file":"ACO/FF_ACO_4pDynamo.crd",
		"top_file":"ACO/FF_ACO_4pDynamo.top",
	}
    if _variation == "IMI":               
        _parameters["top_file"] = "IMI/FF_IMI_4pDynamo.top"
        _parameters["crd_file"] = "IMI/FF_IMI_4pDynamo.crd"

    folder_name = os.path.join(_variation, "Prep_MM")
    save_name   = _variation+"_system"

    sim = Wrapper(folder_name)
    sim.Set_System(_parameters)
    sim.SaveSystem(_cname=save_name)   
        
#---------------------------------------------------
def RunMMopts(_variation= "AC"):
    '''
    '''
    pkl_file_name = os.path.join(_variation, "Prep_MM", _variation+ "_system.pkl")
    if not os.path.exists(pkl_file_name):
        PrepareSystems(_variation)  

    folder_name = os.path.join(_variation, "OPT_MM")   

    _parameters = {
        "Input_Type":"pkl",
        "pkl_file": pkl_file_name,
        "simulation_type":"Geometry_Optimization",
        "save_frequency":10,
        "log_frequency":10,
        "save_format":".dcd",
        "rmsGradient":0.5,
        "optmizer":"ConjugatedGradient",
        "maxIterations":5000,
    }
	
    sim = Wrapper(folder_name)
    sim.Set_System(_parameters)
    sim.Run_Simulation(_parameters)
    sim.SaveSystem(_cname="opt_mm")
#-------------------------------------------------------------------------
def SET_QMMM(_variation= "AC", _qm_region = 1, _hamiltonian = "am1"):
    '''
    '''
    pkl_file_name = os.path.join(_variation, "OPT_MM","opt_mm.pkl")
    if not os.path.exists(pkl_file_name):
        RunMMopts(_variation)  

    folder_name = os.path.join(_variation, "QMMM"+str(_qm_region)+"/"+_hamiltonian)
    
    center_atom = "*:CO2.415:C"
    radius = 5.0
    _parameters = {}   
    if _qm_region == 2:
        center_atom = "*:CO2.413:C"
    elif _qm_region == 3:
        center_atom = "*:CO2.414:C"

    _parameters = {
		"Input_Type":"pkl",
		"pkl_file": pkl_file_name,
		"simulation_type":"Geometry_Optimization",
		"save_frequency":10,
		"log_frequency":10,
		"save_format":".dcd",
		"rmsGradient":0.1,
		"maxIterations":5000,
		"spherical_prune":center_atom,
		"spherical_prune_radius":30,
		"set_fixed_atoms":center_atom,
		"free_atoms_radius":20.0
	}
	
    if not os.path.exists(folder_name) or not os.path.exists(folder_name+"/opt_PrunedFixed"+_hamiltonian+".pkl"):
        sim = Wrapper(folder_name)
        sim.Set_System(_parameters)
        sim.Run_Simulation(_parameters)
        sim.SaveSystem(_cname="opt_PrunedFixed"+_hamiltonian)

    _pkl_file_name = folder_name+"/opt_PrunedFixed"+_hamiltonian+".pkl"

    _qc_mmpars = {
		"Input_Type":"pkl",
		"pkl_file": _pkl_file_name,
		"set_energy_model":"QM",
		"Hamiltonian":_hamiltonian,
		"method_class":"SMO",
		"set_qc_region":"yes",		
		"correct_QMMM_charge":"yes",
		"QCcharge":0,
		"save_format":".dcd",
		"save_frequency":20,
		"log_frequency":10,
		"rmsGradient":0.1,
		"maxIterations":2200,
		"simulation_type":"Geometry_Optimization"
	}
    
    sim = Wrapper(folder_name)
    sim.Set_System(_qc_mmpars)
    sim.Run_Simulation(_qc_mmpars)
    sim.SaveSystem(_cname="opt_qcmm_QM"+str(_qm_region)+_hamiltonian)
#----------------------------------------------------------------------------
def SET_QMMM_ALL(_variation= "AC", qm_regions=[1], _hamiltonians = ["am1"]):
    '''
    '''
    import pymp
    from itertools import product

    pairs = list(product(qm_regions, _hamiltonians))
    with pymp.Parallel(9) as p:
        for i in p.range(len(pairs)):
            qm_region, hamiltonian = pairs[i]
            SET_QMMM(_variation, qm_region, hamiltonian)


#====================================================
if __name__ == "__main__":
    if sys.argv[1] == "--opt":
        if int(sys.argv[2]) == 1:
            PrepareSystems(sys.argv[3])
        elif int(sys.argv[2]) == 2:
            RunMMopts(sys.argv[3])
        elif int(sys.argv[2]) == 3:
            SET_QMMM(sys.argv[3], int(sys.argv[4]), sys.argv[5])
    elif sys.argv[1] == "--opt_all":
        qm_regions = [int(x) for x in sys.argv[3].split(",")]
        hamiltonians = sys.argv[4].split(",")
        print(qm_regions, hamiltonians)
        SET_QMMM_ALL(sys.argv[2], qm_regions, hamiltonians)