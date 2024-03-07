import numpy as np

import sys


from julia import MAGEMin_C

from UWGarnetDiffusion.functions.bulk_rock_functions import *


def generate_2D_grid_endmembers(P, T, data, X, Xoxides, sys_in):
    """
    generate_2D_grid_endmembers generates a 2D grid of garnet endmember mole fractions by calling MAGEMin.

    It takes pressure (P), temperature (T), MAGEMin data object (data), bulk composition (X), 
    bulk oxide composition (Xoxides), and MAGEMin system definition (sys_in) arrays as input.

    It returns arrays containing the garnet mole fractions (gt_mol_frac), weight fractions (gt_wt_frac),
    volume fractions (gt_vol_frac), and endmember mole fractions for pyrope (py_arr), 
    almandine (alm_arr), spessartine (spss_arr), grossular (gr_arr), and khoharite (kho_arr).

    This allows generating a full 2D grid of garnet compositions from MAGEMin.
    """   
    out     =   MAGEMin_C.multi_point_minimization(P, T, data, X=X, Xoxides=Xoxides, sys_in=sys_in)

    ### flush julia output
    sys.stdout.flush()
    sys.stderr.flush()

    gt_mol_frac    = np.zeros_like(P)
    gt_wt_frac    = np.zeros_like(P)
    gt_vol_frac    = np.zeros_like(P)

    py_arr  = np.zeros_like(P) # pyrope (py) = MgO
    alm_arr  = np.zeros_like(P) # almandine (alm) = FeO
    spss_arr  = np.zeros_like(P) # spessartine (sp) = MnO
    gr_arr  = np.zeros_like(P) # grossular (gr) = CaO
    kho_arr  = np.zeros_like(P) # khoharite (kho) = MgO




    for i in range(len(T)):
        ### get garnet data
        gt_mol_frac[i] = ( extract_phase_mol_frac(phase="g", MAGEMinOutput=out[i]) )
        gt_wt_frac[i]  = ( extract_phase_wt_frac(phase="g", MAGEMinOutput=out[i])  )
        gt_vol_frac[i] = ( extract_phase_vol_frac(phase="g", MAGEMinOutput=out[i]) )
        

        ### get end member data of the garnet
        py_arr[i]   = (extract_end_member_mol_frac(phase="g", MAGEMinOutput=out[i], end_member="py"))  
        alm_arr[i]  = (extract_end_member_mol_frac(phase="g", MAGEMinOutput=out[i], end_member="alm")) 
        spss_arr[i] = (extract_end_member_mol_frac(phase="g", MAGEMinOutput=out[i], end_member="spss")) 
        gr_arr[i]   = (extract_end_member_mol_frac(phase="g", MAGEMinOutput=out[i], end_member="gr")) 
        kho_arr[i]  = (extract_end_member_mol_frac(phase="g", MAGEMinOutput=out[i], end_member="kho")) 



    
    return gt_mol_frac, gt_wt_frac, gt_vol_frac, py_arr, alm_arr, spss_arr, gr_arr, kho_arr

def generate_2D_grid_elements(P, T, data, X, Xoxides, sys_in):
    Mgi = np.zeros_like(P)
    Mni = np.zeros_like(P)
    Fei = np.zeros_like(P)
    Cai = np.zeros_like(P)

    gt_mol_frac, gt_wt_frac, gt_vol_frac, py_arr, alm_arr, spss_arr, gr_arr, kho_arr = generate_2D_grid_endmembers(P, T, data, X, Xoxides, sys_in)

    for i in range(len(py_arr)):
        garnet_fractions = {"py": py_arr[i], "alm": alm_arr[i], "gr": gr_arr[i], "spss": spss_arr[i], "kho": kho_arr[i]}

        # ### Calculate molar fractions of Mg, Ca, Fe, and Mn
        mole_fractions = calculate_molar_fractions(garnet_fractions)

        # ### append to lists for each element
        Mgi[i] = (mole_fractions["Mg"])
        Mni[i] = (mole_fractions["Mn"])
        Fei[i] = (mole_fractions["Fe"])
        Cai[i] = (mole_fractions["Ca"])

    return gt_mol_frac, gt_wt_frac, gt_vol_frac, Mgi, Mni, Fei, Cai


    


def gt_single_point_calc_endmembers(P, T, data, X, Xoxides, sys_in):
    """
    Calculate garnet endmember mole fractions for a single P-T point.

    Takes pressure, temperature, bulk composition data, and system definition as input. 
    Calls MAGEMin to perform single point minimization and extract garnet endmember mole fractions.

    Returns mole fraction, weight fraction, volume fraction, and endmember mole fractions for garnet.
    Also returns full MAGEMin output object containing results for all phases.

    Intended as a utility function for quick garnet endmember calculation without a full grid.
    """

    ### do calculation
    out = MAGEMin_C.single_point_minimization(P, T, data, X=X, Xoxides=Xoxides, sys_in=sys_in)

    ### flush julia output
    sys.stdout.flush()
    sys.stderr.flush()

    gt_frac = gt_wt = gt_vol = py = alm = spss = gr = kho = 0.

    if 'g' in out.ph:
        gt_frac  = extract_phase_mol_frac(phase="g", MAGEMinOutput=out)
        gt_wt   = extract_phase_wt_frac(phase="g", MAGEMinOutput=out)
        gt_vol  = extract_phase_vol_frac(phase="g", MAGEMinOutput=out)

        py  = extract_end_member_mol_frac(phase="g", MAGEMinOutput=out, end_member="py")
        alm = extract_end_member_mol_frac(phase="g", MAGEMinOutput=out, end_member="alm")
        spss= extract_end_member_mol_frac(phase="g", MAGEMinOutput=out, end_member="spss")
        gr  = extract_end_member_mol_frac(phase="g", MAGEMinOutput=out, end_member="gr")
        kho = extract_end_member_mol_frac(phase="g", MAGEMinOutput=out, end_member="kho")


    return gt_frac, gt_wt, gt_vol, py, alm, spss, gr, kho, out


def gt_single_point_calc_elements(P, T, data, X, Xoxides, sys_in):
    """
    Calculate garnet endmember element mole fractions for a single P-T point.

    Takes pressure, temperature, bulk composition data, and system definition as input.  
    Calls gt_single_point_calc_endmembers() to calculate endmember mole fractions.
    Extracts molar fractions of Mg, Mn, Fe, and Ca from the endmember fractions.

    Returns mole fraction, weight fraction, volume fraction, and molar fractions 
    for Mg, Mn, Fe, Ca in garnet. Also returns full MAGEMin output object.

    Utility function to get garnet element fractions from endmember fractions.
    """


    ### use the previous function to get the EM fractions
    gt_frac, gt_wt, gt_vol, py, alm, spss, gr, kho, out = gt_single_point_calc_endmembers(P, T, data, X=X, Xoxides=Xoxides, sys_in=sys_in)

    Mg = Mn = Fe = Ca = 0.

    garnet_fractions = {"py": py, "alm": alm, "gr": gr, "spss": spss, "kho": kho}

    ### Calculate molar fractions of Mg, Ca, Fe, and Mn
    mole_fractions = calculate_molar_fractions(garnet_fractions)
    #### append to lists for each element
    Mg = (mole_fractions["Mg"])
    Mn = (mole_fractions["Mn"])
    Fe = (mole_fractions["Fe"])
    Ca = (mole_fractions["Ca"])

    return gt_frac, gt_wt, gt_vol, Mg, Mn, Fe, Ca, out



def garnet_over_path(P, T, data, X, Xoxides, sys_in, fractionate=0):
    """
    Calculates garnet composition and fractionation along a P-T path.

    Takes arrays of pressure (P) and temperature (T) along a P-T path, 
    bulk composition data, initial bulk composition oxides, and system 
    definition as input. Calls gt_single_point_calc_endmembers() to calculate
    garnet endmember fractions at each point. Converts endmembers to element
    oxides. Can optionally fractionate bulk composition due to garnet growth.

    Returns arrays of garnet mole fraction, weight fraction, volume fraction, 
    change in mole/weight fraction, and element molar fractions along the P-T path.
    """



    gt_wt_frac    = np.zeros(len(P))
    gt_mol_frac   = np.zeros(len(P))
    gt_vol_frac   = np.zeros(len(P))

    d_gt_mol_frac = np.zeros(len(P))
    d_gt_wt_frac = np.zeros(len(P))

    Mgi = np.zeros(len(P))  # pyrope (py) & Khoharite (kho) = MgO
    Fei = np.zeros(len(P)) # almandine (alm) = FeO
    Mni = np.zeros(len(P))  # spessartine (sp) = MnO
    Cai = np.zeros(len(P))  # grossular (gr) = CaO

    py_arr   = np.zeros(len(P))
    alm_arr  = np.zeros(len(P))
    spss_arr = np.zeros(len(P))
    gr_arr   = np.zeros(len(P))
    kho_arr  = np.zeros(len(P))

    for i in range(len(P)):
        gt_frac, gt_wt, gt_vol, py, alm, spss, gr, kho, out = gt_single_point_calc_endmembers(P[i], T[i], data, X, Xoxides, sys_in)

        py_arr[i] = py
        alm_arr[i] = alm
        spss_arr[i] = spss
        gr_arr[i] = gr
        kho_arr[i] = kho

        ### convert end members to Fe, Mg, Mn, Ca amounts
        garnet_fractions = {"py": py, "alm": alm, "gr": gr, "spss": spss, "kho": kho}


        ### Calculate molar fractions of Mg, Ca, Fe, and Mn
        mole_fractions = calculate_molar_fractions(garnet_fractions)

        # ### append to lists for each element
        Mgi[i] = (mole_fractions["Mg"])
        Mni[i] = (mole_fractions["Mn"])
        Fei[i] = (mole_fractions["Fe"])
        Cai[i] = (mole_fractions["Ca"])


        # ### get garnet data
        if i ==0:
            gt_mol_frac_initial = gt_frac
            gt_wt_frac_initial = gt_wt
            gt_vol_frac_initial = gt_vol
        
         ## The first gt_frac must be 0, we will call it reduction (we neglect the previous history - we recommend starting from a zero field of garnet)
        gt_mol_frac[i] = gt_frac - gt_mol_frac_initial
        gt_wt_frac[i] = gt_wt - gt_wt_frac_initial
        gt_vol_frac[i] = gt_vol - gt_vol_frac_initial


        ### Fractionate the bulk rock due to the garnet growth
        if fractionate == True:
            """
            This approach is based on the assumption that the change in garnet fraction from one 
            P-T point to the next represents the amount of garnet growth (or reduction) 
            that occurs due to the changes in pressure and temperature. 

            We use the output from MAGEMin to calculate the change in the bulk rock oxides
            as MAGEMin produces the oxides contained in the garnet.
            """
            if i == 0:
                d_gt_mol_frac[i] = gt_mol_frac[0] ### Initial point is zero
                d_gt_wt_frac[i] = gt_wt_frac[0] ### Initial point is zero
            else:
                d_gt_mol_frac[i] = gt_mol_frac[i] - gt_mol_frac[i-1] ### for every other point along the PT path
                d_gt_wt_frac[i] = gt_wt_frac[i] - gt_wt_frac[i-1] ### for every other point along the PT path

            ### only fractionate if garnet is being created
            if gt_frac > 0:
                garnet_ind = out.ph.index("g")

                Xoxides =  out.oxides
                if sys_in == "wt":
                    X = out.bulk_wt - (out.bulk_wt * out.SS_vec[garnet_ind].Comp_wt * d_gt_wt_frac[i])
                elif sys_in == "mol":
                    X = out.bulk - (out.bulk * out.SS_vec[garnet_ind].Comp * d_gt_mol_frac[i])
                # else:
                #     print("sys_in must be either 'wt' or 'mol")

                


            

    # ### release the data
    # MAGEMin_C.Finalize_MAGEMin(data)



    return gt_mol_frac, gt_wt_frac, gt_vol_frac, d_gt_mol_frac, d_gt_wt_frac, Mgi, Mni, Fei, Cai, 


def extract_end_member_mol_frac(phase, MAGEMinOutput, end_member):
    """
    Extracts end member data from MAGEMinOutput based on phase and end member.
    Args:
        phase (str): The phase to extract data for.
        MAGEMinOutput (MAGEMinOutput): The MAGEMinOutput object containing the data.
        endMember (str): The end member to extract data for.
    Returns:
        float: The molar fraction of the specified end member for the given phase. If the specified
        phase or end member is not found, returns 0.0.
    """
    try:
        phase_ind = MAGEMinOutput.ph.index(phase)
        em_index = MAGEMinOutput.SS_vec[phase_ind].emNames.index(end_member)
        data = MAGEMinOutput.SS_vec[phase_ind].emFrac[em_index]
    except:
        data = 0.
    return data

def extract_end_member_wt_frac(MAGEMinOutput, phase, end_member):
    """
    Extracts the weight fraction of a specified end member for a given phase from the input MAGEMinOutput.

    Args:
        MAGEMinOutput: The input MAGEMinOutput object.
        phase: The phase for which the end member weight fraction is to be extracted.
        end_member: The end member for which the weight fraction is to be extracted.

    Returns:
        The weight fraction of the specified end member for the given phase. If the specified
        phase or end member is not found, returns 0.0.
    """

    try:
        phase_ind = MAGEMinOutput.ph.index(phase)
        em_index = MAGEMinOutput.SS_vec[phase_ind].emNames.index(end_member)
        data = MAGEMinOutput.SS_vec[phase_ind].emFrac_wt[em_index]
    except:
        data = 0.
    return data


def extract_phase_mol_frac(phase, MAGEMinOutput):
    """
    Extracts the phase mol from the MAGEMinOutput.

    Args:
        phase: The phase to extract.
        MAGEMinOutput: The MAGEMinOutput object containing phase information.

    Returns:
        The extracted phase molar fraction, or 0. if not found.
    """
    try:
        phase_ind = MAGEMinOutput.ph.index(phase)
        data = (MAGEMinOutput.ph_frac[phase_ind])
    except:
        data = 0.
    return data

def extract_phase_wt_frac(phase, MAGEMinOutput):
    """
    Function to extract phase weight from MAGEMinOutput.
    
    Parameters:
    - phase: the phase to extract weight for
    - MAGEMinOutput: the MAGEMinOutput object
    
    Returns:
    - data: the weight fraction of the specified phase, or 0. if not found
    """
    try:
        phase_ind = MAGEMinOutput.ph.index(phase)
        data = (MAGEMinOutput.ph_frac_wt[phase_ind])
    except:
        data = 0.
    return data

def extract_phase_vol_frac(phase, MAGEMinOutput):
    """
    Function to extract phase weight from MAGEMinOutput.
    
    Parameters:
    - phase: the phase to extract weight for
    - MAGEMinOutput: the MAGEMinOutput object
    
    Returns:
    - data: the volume % of the specified phase, or 0. if not found
    """
    ph_names = MAGEMinOutput.ph
    n_ph = len(ph_names)
    V = np.zeros((n_ph, 1))

    for i, ph in enumerate(ph_names):
        id = [j for j, p in enumerate(MAGEMinOutput.ph) if p == ph]
        if id:
            rho = sum(MAGEMinOutput.SS_vec[j].rho if j < MAGEMinOutput.n_SS else MAGEMinOutput.PP_vec[j - MAGEMinOutput.n_SS].rho for j in id) / len(id)
            V[i, 0] = sum(MAGEMinOutput.ph_frac_wt[j] for j in id) / rho

    V /= np.sum(V)
            

    try:
        phase_ind = MAGEMinOutput.ph.index(phase)
        data = V[phase_ind]
    except:
        data = 0.

    return data

def get_phase_comp_mol(phase, MAGEMinOutput):
    """
    Function to extract phase comp in mol % from MAGEMin.
    
    Parameters:
    - phase: the phase to extract mol frac for
    - MAGEMinOutput: the MAGEMinOutput object
    
    Returns:
    - data: the composition of the phase in mol frac, or 0. if not found
    """
    try:
        phase_ind = MAGEMinOutput.ph.index(phase)
        data = (MAGEMinOutput.SS_vec[phase_ind].Comp)
    except:
        data = 0.
    return data

def get_phase_comp_wt(phase, MAGEMinOutput):
    """
    Function to extract phase comp in wt % from MAGEMin.
    
    Parameters:
    - phase: the phase to extract weight % for
    - MAGEMinOutput: the MAGEMinOutput object
    
    Returns:
    - data: the composition of the phase in wt %, or 0. if not found
    """
    try:
        phase_ind = MAGEMinOutput.ph.index(phase)
        data = (MAGEMinOutput.SS_vec[phase_ind].Comp)
    except:
        data = 0.
    return data