#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pDynamoWrapper.pDynamoWrapper import Wrapper

import os,sys

#======================================================
def get_pkl_names(_variation,_simulation_folder):
    pkl_file_name = "ac_system.pkl"
    if _variation == "AC":                    
        pkl_file_name = "AC/"+_simulation_folder+"/ac_system.pkl"           
    elif _variation == "AC_contaminants":     
        pkl_file_name = "AC_cnt/"+_simulation_folder+"/ac_cnt_system.pkl"
    elif _variation == "ACLI":                
        pkl_file_name = "ACLI/"+_simulation_folder+"/acli_system.pkl"
    elif _variation == "ACLI_QS":             
        pkl_file_name = "ACLI_QS/"+_simulation_folder+"/acli_qs_system.pkl"
    elif _variation == "ACLI_QS_contaminants":
        pkl_file_name = "ACLI_QS_cnt/"+_simulation_folder+"/acli_qs_cnt_system.pkl"
    elif _variation == "ACLI_contaminants":     
        pkl_file_name = "ACLI_cnt/"+_simulation_folder+"/acli_cnt_system.pkl"
    
    return pkl_file_name
#------------------------------------------------------
def get_folder_name(_variation, _simulation_type):
    folder_name = _simulation_type
    if _variation == "AC":                      folder_name = "AC/"+_simulation_type
    elif _variation == "AC_contaminants":       folder_name = "AC_cnt/"+_simulation_type
    elif _variation == "ACLI":                  folder_name = "ACLI/"+_simulation_type
    elif _variation == "ACLI_QS":               folder_name = "ACLI_QS/"+_simulation_type
    elif _variation == "ACLI_QS_contaminants":  folder_name = "ACLI_QS_cnt/"+_simulation_type
    elif _variation == "ACLI_contaminants":     folder_name = "ACLI_cnt/"+_simulation_type

    return folder_name
#======================================================
def PrepareSystems(_variation= "AC"):

    '''
    This functions prepares the systems for QM/MM simulations, by setting up the system parameters and saving the system objects for each variation of the system. The variations include:
- AC: Carbonic anhydrase system with CO2 and Zn2+ in the active site, prepared for MM simulations.
- AC_contaminants: Carbonic anhydrase system with CO2 and Zn2+ in the active site, prepared for MM simulations, with contaminants
- ACLI: Carbonic anhydrase system with CO2 and Zn2+ in the active site, prepared for MM simulations, with Ionic liquids
- ACLI_QS: Carbonic anhydrase system with CO2 and Zn2+ in the active site, for investigating chemissorption on the ionic liquids
- ACLI_QS_contaminants: Carbonic anhydrase system with CO2 and Zn2+ in the active site, for investigating chemissorption on the ionic liquids, with contaminants
- ACLI_contaminants: Carbonic anhydrase system with CO2 and Zn2+ in the active site, with ionic liquids and contaminants
    '''

    _parameters = {
		"Input_Type":"amber",
		"crd_file":"AC/ac_rep0.crd",
		"top_file":"AC/ac_topology_amber.top",
		"set_initial_crd":"AC/analysisZN_CO2_0.pdb"
	}
    _save_name = "ac_system"
    _topol_file = "AC/ac_topology_amber.top"
    _crd_file = "AC/ac_rep0.crd"
    _initial_crd = "AC/analysisZN_CO2_0.pdb"
    save_name = "ac_system"
    if _variation == "AC_contaminants":
        _topol_file = "AC_cnt/ac_cnt_topology_amber.top"
        _crd_file = "AC_cnt/ac_cnt_rep0.crd"
        _initial_crd = "AC_cnt/analysisZN_CO2_0.pdb"
    elif _variation == "ACLI":
        _topol_file = "ACLI/ac_li.top"
        _crd_file = "ACLI/ac_li.crd"
        _initial_crd = "ACLI/analysisZN_CO2_10.pdb"
        save_name = "acli_system"
    elif _variation == "ACLI_QS":
        _topol_file = "ACLI_QS/ac_li.top"
        _crd_file = "ACLI_QS/ac_li.crd"
        _initial_crd = "ACLI_QS/analysisZN_CO2_10.pdb"
        save_name = "acli_qs_system"
    elif _variation == "ACLI_QS_contaminants":
        _topol_file = "ACLI_QS_cnt/ac_li_cnt.top"
        _crd_file = "ACLI_QS_cnt/ac_li_cnt.crd"
        _initial_crd = "ACLI_QS_cnt/analysisZN_CO2_10.pdb"
    elif _variation == "ACLI_contaminants":
        _topol_file = "ACLI_cnt/ac_li_cnt.top"
        _crd_file = "ACLI_cnt/ac_li_cnt.crd"
        _initial_crd = "ACLI_cnt/analysisZN_CO2_10.pdb"

    _parameters["top_file"] = _topol_file
    _parameters["crd_file"] = _crd_file
    _parameters["set_initial_crd"] = _initial_crd

    folder_name = get_folder_name(_variation, "Prep_MM")
    sim = Wrapper(folder_name)
    sim.Set_System(_parameters)
    sim.SaveSystem(_cname=save_name)   
        
#---------------------------------------------------
def RunMMopts(_variation= "AC"):
    '''
    '''
    pkl_file_name = get_pkl_names(_variation, "Prep_MM")
    if not os.path.exists(pkl_file_name):
        PrepareSystems(_variation)  

    folder_name = get_folder_name(_variation, "OPT_MM")   

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
    pkl_file_name = get_folder_name(_variation, "OPT_MM")+"/opt_mm.pkl"
    if not os.path.exists(pkl_file_name):
        RunMMopts(_variation)  

    folder_name = get_folder_name(_variation, "QMMM"+str(_qm_region)+"/"+_hamiltonian)
    
    center_atom = "*:ZN.466:ZN"
    radius = 4.7
    _parameters = {}
    if _qm_region == 1:
        center_atom = "*:ZN.466:ZN"
    elif _qm_region == 2:
        center_atom = "*:CO2.520:C"
        if _variation == "ACLI":
            center_atom = "*:CO2.500:C7"
    elif _qm_region == 3:
        center_atom = "*:SOL.18938:OW"
        radius = 4.0
        if _variation == "ACLI":
            center_atom = "*:SOL.17757:OW"
            radius = 5.0

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
    if _variation == "AC_LI":
        _parameters["spherical_prune_radius"] = 40.0
	
    if not os.path.exists( folder_name) or not os.path.exists(folder_name+"/opt_PrunedFixed"+_hamiltonian+".pkl"):
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

    if not _qm_region == 4:
        _qc_mmpars["center_atom"] = center_atom
        _qc_mmpars["radius"] = radius
    else:
        if _variation == "AC":
            _qc_mmpars["residue_patterns"] = ["*:ZN.466:*","*:SOL.18938:*","*:CO2.520:*","*:HID.329:*", "*:HIE.348:*","*:HID.331:*","*:HID.304:*","*:GLU.335:*","*:TYR.245:*","*:THR.414:*"]
            _qc_mmpars["select_waters"] = 5.0
        elif _variation == "ACLI":
            _qc_mmpars["residue_patterns"] = ["*:ZN.466:*","*:CO2.500:*","*:HID.329:*", "*:HIE.348:*","*:HID.331:*","*:HID.304:*","*:GLU.335:*","*:TYR.245:*","*:THR.414:*"]
            _qc_mmpars["select_waters"] = 5.0

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