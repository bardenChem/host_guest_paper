#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os,sys
from pDynamoWrapper.pDynamoWrapper import Wrapper

def run_refinement_from_MD(_variation, qm_region, hamiltonian, _temperature=293.15):


    folder_name = _variation+"/RefineMopac/QM"+str(qm_region)+"_"+hamiltonian+"_"+str(_temperature)
    _pkl_file_name = _variation+"/QMMM"+str(qm_region)+"/"+hamiltonian+"/opt_qcmm_QM"+str(qm_region)+hamiltonian+".pkl"
    _traj_source = _variation+"/MD_QMMM/QM"+str(qm_region)+"_"+hamiltonian+"_"+str(_temperature)+"/trajectory.ptGeoproduction.ptGeo/"
    _parameters = {
        "Input_Type":"pkl",
        "pkl_file":_pkl_file_name,
        "atoms_rc1":[ "*:ZN.466:*","*:CO2.520:C"],
        "atoms_rc2":["*:ZN.466:*","*:HID.304:NE2"],
        "type_rc1":"Distance",
        "type_rc2":"Distance",
        "mass_constraints":["no","no"],
        "set_reaction_crd":2,
        "ndim":2,
        "dincre_rc1":0.0,
        "dincre_rc2":0.0        
    }
    
    simulation_parameters = {
                  "simulation_type":"Energy_Refinement",
                  "xnbins":1000,
                  "Software":"mopac",
                  "source_folder":_traj_source,
                  "nMaxThreads":16,
                  "sampling_factor":10,
                  "methods_lists":["pm7"],
                  "software_path":"/usr/bin/mopac",
                  "folder":folder_name
                  
    }
    sim = Wrapper(folder_name)
    sim.Set_System(_parameters)
    sim.Run_Simulation(simulation_parameters)

#============================================
if __name__ == "__main__":
    _variation = sys.argv[1]
    qm_region = int(sys.argv[2])
    hamiltonian = sys.argv[3]
    _temperature = float(sys.argv[4])
    run_refinement_from_MD(_variation, qm_region, hamiltonian, _temperature)