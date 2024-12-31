# -------------------------------------------------------------------------------------
# Python script to replace LAS Null values in multiple LAS files  e.g. -9999 into -999.25
# take input CWLS LAS format from "curr_dir" and save the edited in the "output_dir"  
# 2022-02-24
#--------------------------------------------------------------------------------------
import glob
import ntpath
import os

curr_dir = r'C:\LogStream\las'  #directory location where LAS files located
output_dir = "output"  #assign output directory to save edited LAS files

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

for f in glob.glob(curr_dir + "\*.las"):
    with open(f, 'r') as inputfile:
        with open('%s/%s' % (output_dir, ntpath.basename(f)), 'w') as outputfile:
            for line in inputfile:
                outputfile.write(line.replace('-9999', '-999.25'))                
                