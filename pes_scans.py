#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pDynamoWrapper.pDynamoWrapper import Wrapper, Unpickle
from init_systems import get_folder_name, get_pkl_names

import os,sys
from pBabel import ImportCoordinates3, ImportSystem



def RUN2D(_variation,qm_region, hamiltonian,_forces=[1200.0,400.0],mark="F1",initial_crd=None):
    _qm_region=str(qm_region)
    folder_name = _variation+"/PES2D_QMMM"+"/"+hamiltonian+"_QM"+_qm_region+"_"+mark
  
    _pkl_file_name = _variation+"/QMMM"+_qm_region+"/"+hamiltonian+"/opt_qcmm_QM"+_qm_region+hamiltonian+".pkl"
    _parameters = {
        "Input_Type":"pkl",
        "pkl_file":_pkl_file_name,
        "atoms_rc1":["*:SOL.18938:OW","*:SOL.18938:HW2","*:HID.329:NE2"],
		"atoms_rc2":["*:ZN.466:*", "*:SOL.18938:OW", "*:CO2.520:C"],
		"type_rc1":"Distance",
		"type_rc2":"Distance",
		"mass_constraints":["no","no"],
        "set_reaction_crd":2,
        "dincre_rc1":0.1,
		"dincre_rc2":0.1,
        "enable_debug_file": True,
        "debug_verbosity": "DEBUG",
    }
    
    if hamiltonian == "am1" and qm_region == 1:
       _parameters["atoms_rc1"]=["*:SOL.18938:OW","*:SOL.18938:HW2","*:HIE.348:ND1"]
    if _variation == "ACLI":
         _parameters["atoms_rc1"]=["*:SOL.17757:OW","*:SOL.17757:HW1","*:HID.329:NE2"]
         _parameters["atoms_rc2"]=["*:ZN.466:*", "*:SOL.17757:OW", "*:CO2.500:C7"]

    if initial_crd is not None:
       _parameters["pkl_file"] = initial_crd    
      
    
    scan_parameters = {

		"simulation_type":"Relaxed_Surface_Scan",		
		"optmizer":"ConjugatedGradient",
		"maxIterations":2200,
		"log_frequency":10,
		"nsteps_rc1":-1,
		"nsteps_rc2":40,
		"restart":"yes",
		"NmaxThreads":40,
        "dincre_rc1":0.1,
		"dincre_rc2":0.1,
		"force_constants":[_forces[0],_forces[1]]
    }

    sim = Wrapper(folder_name)
    sim.Set_System(_parameters)
    sim.Run_Simulation(scan_parameters)

#=======================================================================================
def RUN_ALL(_variation):

    _forces_RC1 = [1200.0]
    _forces_RC2 = [600.0]
    for _force1 in _forces_RC1:
        print("==============================================")
        print(f"Running RC1 with force constant: {_force1}")
        print("==============================================")
        for _force2 in _forces_RC2:
            mark = "F"+str(int(_force1))+"_"+str(int(_force2))
            print("==============================================")
            print(f"Running RC2 with force constant: {_force2} and mark: {mark}")
            print("==============================================")
            for qm_region in [1,2,3]:
                print("==============================================")
                print(f"Running QM region: {qm_region}")
                print("==============================================")
                for hamiltonian in ["am1","pm3","pm6"]:
                    print("==============================================")
                    print(f"Running Hamiltonian: {hamiltonian}")
                    print("==============================================")
                    RUN2D(_variation, qm_region, hamiltonian, [1200.0,600.0], mark=mark)


#-------------------------------------------------------------------------------------
def RUN_ALL_fromMD(_variation):


    regions = [1,2,3]
    hamiltonians = ["am1","pm3","pm6"]
    for qm_region in regions:
        print("==============================================")
        print(f"Running QM region: {qm_region}")
        print("==============================================")
        for hamiltonian in hamiltonians:
            _file = _variation+"/MD_QMMM/QM"+str(qm_region)+"_"+hamiltonian+"/trajectory.ptGeoproduction.ptGeo/mostFrequentRC2_least.pkl"
            if not os.path.exists(_file):
                 raise FileNotFoundError("Initial coordinate file not found: "+_file)
            print("==============================================")
            print(f"Running Hamiltonian: {hamiltonian}")
            print("==============================================")
            RUN2D(_variation, qm_region, hamiltonian, [1200.0,600.0],initial_crd=_file)


#-------------------------------------------------------------------------------------
def Pick_path(_variation, qm_region, hamiltonian, mark="F1"):
    folder_name = _variation+"/PES2D_QMMM"+str(qm_region)+"/"+hamiltonian+"_"+mark
    _pkl_file_name = _variation+"/QMMM"+str(qm_region)+"/"+hamiltonian+"/opt_qcmm_QM"+str(qm_region)+hamiltonian+".pkl"
 
    _parameters = {
		"Input_Type":"pkl",		
		"pkl_file":_pkl_file_name,
		"set_reaction_crd":2,	
		"type_rc1":"Distance",
		"type_rc2":"Distance",
		"mass_constraints":["no","no"]
	}
    _parameters["atoms_rc1"] = ["*:SOL.18938:OW", "*:SOL.18938:HW2", "*:HID.329:NE2"]
    _parameters["atoms_rc2"] = ["*:ZN.466:ZN", "*:SOL.18938:OW", "*:CO2.520:C"]	
    
    if qm_region == 3:
        _parameters["atoms_rc2"] = ["*:SOL.18938:HW2","*:SOL.18938:OW", "*:CO2.520:C"]

    _path   = "PES2D_QMMM"+str(qm_region)+"/"+hamiltonian+"_"+mark+"/ScanTraj.ptGeo"

    analysis_parameters = {
		"analysis_type":"Energy_Plots",
		"log_name":"PES2D_QMMM"+str(qm_region)+"/"+hamiltonian+"_"+mark+"/ScanTraj.log",
		"retrieve_path":_path,
		"xsize":-1,
		"ysize":-1,
		"contour_lines":18,
		"MEP_method":"SimpleMEP",
		"max_points":25,
		"min_points":23,
		"folder":"PES2D_QMMM"+str(qm_region)+"/"+hamiltonian+"_"+mark,
		"type":"2D",
		"in_point" :[0,0],
		"fin_point":[-1,-1]
	}				
    test_01 = Wrapper(folder_name)
    test_01.Set_System(_parameters)
    test_01.Run_Analysis(analysis_parameters)
    test_01.SaveSystem()

#--------------------------------------------------------------------------
def pick_path_all(_variation):
    for qm_region in [1,2,3]:
        for hamiltonian in ["am1","pm3","pm6"]:
            for _force1 in [1200.0, 1600.0, 800.0]:
                for _force2 in [400.0,600.0,200.0]:
                    mark = "F"+str(int(_force1))+"_"+str(int(_force2))
                    Pick_path(_variation, qm_region, hamiltonian, mark=mark)

#======================================================================================
if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--scan2D":
            qm_region = int(sys.argv[3])
            hamiltonian = sys.argv[4]
            forces = [float(x) for x in sys.argv[5].split(",")]
            mark = sys.argv[6] if len(sys.argv) > 6 else None
            initial_crd = sys.argv[7] if len(sys.argv) > 7 else None
            RUN2D(sys.argv[2], qm_region, hamiltonian, forces, mark=mark, initial_crd=initial_crd)
        elif sys.argv[1] == "--scan_all":
            RUN_ALL(sys.argv[2])
        elif sys.argv[1] == "--pick_path":
            qm_region = int(sys.argv[3])
            hamiltonian = sys.argv[4]
            mark = sys.argv[5] if len(sys.argv) > 5 else "F1"
            Pick_path(sys.argv[2], qm_region, hamiltonian, mark=mark)
        elif sys.argv[1] == "--pick_path_all":
            pick_path_all(sys.argv[2])
        elif sys.argv[1] == "--scan_all_md":
            RUN_ALL_fromMD(sys.argv[2])
