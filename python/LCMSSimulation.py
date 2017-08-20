# -*- coding: utf-8 -*-
"""
Created on Wed Aug 16 08:14:15 2017

@author: zmzhang
"""


import subprocess, sys, os
import pyopenms
import pandas as pd
from FPIC import data2mzxml
from _pymass import mzXMLParser
import _pymass as pm

def simulation(fasta, contaminants, out, out_cntm,
               simulator = 'C:/Program Files/OpenMS/bin/MSSimulator.exe'):   
    """
        Should copy "C:\Program Files\OpenMS\share\OpenMS\examples" to working directory of Python
    """ 
   
    subprocess.call([simulator, '-in', fasta, '-out', out, '-out_cntm',out_cntm, 
               '-algorithm:MSSim:RawSignal:contaminants:file', contaminants,
               '-algorithm:MSSim:Ionization:mz:lower_measurement_limit', '10',
               '-algorithm:MSSim:Ionization:mz:upper_measurement_limit', '1000',
               '-algorithm:MSSim:RT:total_gradient_time', '1000',
               '-algorithm:MSSim:RT:sampling_rate', '0.1',
               '-algorithm:MSSim:RT:scan_window:min', '0',
               '-algorithm:MSSim:RT:scan_window:max', '1000'])

def parse_featureXML_GT(feature_file):
    featuremap = pyopenms.FeatureMap()
    featurexml = pyopenms.FeatureXMLFile()
    featurexml.load(feature_file, featuremap)
    
    hulls = pd.DataFrame(columns=['rt_min', 'rt_max', 'mz_min', 'mz_max', 'detected', 'pic_id'])   
    for i in range(featuremap.size()):
        feature = featuremap[i]
        chs = feature.getConvexHulls()
        for j in range(len(chs)):
            pts = chs[j].getHullPoints()
            hulls.loc[len(hulls)] = [pts.min(0)[0], pts.max(0)[0], pts.min(0)[1], pts.max(0)[1], False, str(-1)]
    return hulls

def FeatureFindingMetabo1(mzfile):
    exp = pyopenms.MSExperiment()
    pyopenms.MzXMLFile().load(mzfile, exp)
    
    mtd_params = pyopenms.MassTraceDetection().getDefaults()
    mtd = pyopenms.MassTraceDetection()
    mtd.setParameters(mtd_params)
    mass_traces=[]
    mtd.run(exp, mass_traces)
    
    epdet_params = pyopenms.ElutionPeakDetection().getDefaults()
    epdet = pyopenms.ElutionPeakDetection()
    epdet.setParameters(epdet_params)
    splitted_mass_traces = []
    epdet.detectPeaks(mass_traces, splitted_mass_traces)
    
    ffm_params = pyopenms.FeatureFindingMetabo().getDefaults()
    ffm = pyopenms.FeatureFindingMetabo()
    ffm.setParameters(ffm_params)
    feature_map = pyopenms.FeatureMap()
    ffm.run(splitted_mass_traces, feature_map)
    return feature_map

def FeatureFindingMetabo(mzfile):
    finder = 'C:/Program Files/OpenMS/bin/FeatureFinderMetabo.exe'
    feature_file = 'tmp.featureXML'
    subprocess.call([finder, '-in', mzfile, '-out', feature_file, 
               '-algorithm:common:noise_threshold_int', '10',
               '-algorithm:common:chrom_peak_snr', '3',
               '-algorithm:common:chrom_fwhm', '5',
               '-algorithm:mtd:mass_error_ppm', '20',
               '-algorithm:mtd:reestimate_mt_sd', 'true',
               '-algorithm:epd:width_filtering', 'off'])  
    featuremap = pyopenms.FeatureMap()
    featurexml = pyopenms.FeatureXMLFile()
    featurexml.load(feature_file, featuremap)
    #os.remove(feature_file)
    return featuremap

def parse_featureXML_FFM(featuremap):   
    df = pd.DataFrame(columns=['rt', 'mz', 'intensity'])   
    for i in range(featuremap.size()):
        feature = featuremap[i]
        isotope_distances = feature.getMetaValue(b'isotope_distances')
        rt = feature.getRT()
        mz = feature.getMZ()
        intensity = feature.getIntensity()
        for j in range(feature.getMetaValue(b'num_of_masstraces')):
            if j == 0:
                df.loc[len(df)] = [rt, mz, intensity]
            else:
                mz_delta = isotope_distances[j-1]
                df.loc[len(df)] = [rt, mz + mz_delta, intensity] 
    return df


def params2df(params):
    params_df = pd.DataFrame(columns=['name', 'value'])
    for k, v in sorted(params.items()):
        if type(v) == type(bytes()):
            v = v.decode('utf-8')
        params_df.loc[len(params_df)] = [k.decode('utf-8'),v]
    return params_df


if __name__=="__main__":
    mm48_all = pd.read_csv('simulation/MM48_annotations.csv')
    mm48_all['charge'] = [1] * mm48_all.shape[0]
    mm48_all['shape'] = ['gauss'] * mm48_all.shape[0]
    mm48_all['source'] = ['ESI'] * mm48_all.shape[0]
    mm48 = mm48_all[['Name', 'Formel','RT','RT2','Intensity','charge','shape','source']]
    mm48.to_csv('simulation/MM48_MSSimulator.csv', header=False, index=False)
    
    simulation('simulation/test.fasta','simulation/MM48_MSSimulator.csv',
               'MM48_MSS_Profile.mzML', 'MM48_MSS.featureXML' )
    
    
    peak_picker = 'C:/Program Files/OpenMS/bin/PeakPickerHiRes.exe'
    subprocess.call([peak_picker,'-in', 'MM48_MSS_Profile.mzML',
                    '-out', 'MM48_MSS.mzML'])
    
    data2mzxml('./')
    
    hulls = parse_featureXML_GT('MM48_MSS.featureXML')
    
    mzfile =  "MM48_MSS.mzxml"
    mzMLfile =  "MM48_MSS.mzML"

    parser=mzXMLParser()
    lcms = parser.parseFile(mzfile.encode(sys.getfilesystemencoding()))
    pics_c = pm.FPICs(lcms, 10.0, 200.0, 0.5)
    
    for i,pic in enumerate(pics_c):
        idx = pic[:,2].argmax()
        rt  = pic[idx,0]
        mz  = pic[idx,1]
        for i in range(len(hulls)):
            if(rt >= hulls.at[i, 'rt_min'] and rt <= hulls.at[i, 'rt_max'] and
               mz >= hulls.at[i, 'mz_min']-0.01 and mz <= hulls.at[i, 'mz_max']+0.01
               ):
                hulls.at[i, 'detected'] = True
                hulls.at[i, 'pic_id'] = str(i)
    
    feature_map = FeatureFindingMetabo(mzMLfile)
    df = parse_featureXML_FFM(feature_map)
    
    params = params2df(pyopenms.FeatureFindingMetabo().getDefaults())