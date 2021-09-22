#!/usr/bin/python

import os, sys
import argparse

#print(sys.version)

def bed_file_modifier(input_fp, output_fp) :
    input_bed_file = open(input_fp, 'r')
    output_bed_file = open(output_fp, 'w')

    for line in input_bed_file :
        split_line = line.rstrip("\r\n").split("\t")

        if split_line[0].startswith("browser") or split_line[0].startswith("track") :
            #This line is FUNCTIONAL HEADER.
            continue

        elif split_line[0].startswith("#") :
            #This line is DESCRIPTIVE HEADER.
            continue

        elif 'chr' in split_line[0] :
            #This line is DATA.
            tmp_list = []
            CHROMO   = split_line[0]
            START_P  = split_line[1]
            END_P    = split_line[2]
            tmp_list.append(CHROMO)
            tmp_list.append(START_P)
            tmp_list.append(END_P)

            if len(split_line) == 3 :
                #This bed file has only CHROMOSOME & START/END POSITION DATA.
                GENE_SYM = "."
                SCORE    = "0"            
                STRAND   = "."
                tmp_list.append(GENE_SYM)
                tmp_list.append(SCORE)
                tmp_list.append(STRAND)

                output_bed_file.write("\t".join(tmp_list) + "\n")

            elif len(split_line) == 4 : 
                #This bed file has GENESYMBOL DATA.
                GENE_SYM = split_line[3]
                SCORE    = "0"            
                STRAND   = "."
                tmp_list.append(GENE_SYM)
                tmp_list.append(SCORE)
                tmp_list.append(STRAND)

                output_bed_file.write("\t".join(tmp_list) + "\n")

            elif len(split_line) == 6 : 
                #This bed file has GENESYMBOL + SCORE + STARND DATA.
                GENE_SYM = split_line[3]
                SCORE    = split_line[4]          
                STRAND   = split_line[5]
                tmp_list.append(GENE_SYM)
                tmp_list.append(SCORE)
                tmp_list.append(STRAND)
                
                output_bed_file.write("\t".join(tmp_list) + "\n")
            
def usage() :
    message='''
[USAGE]
python %s -i <Design_ID.Raw.bed> -o <Design_ID.Modified.bed>

[PARAMETER]
-i, --input  : input bed file path
-o, --output : output bed file path

[PURPOSE]
This script converts 'Raw Target Bed file' into 'Modified Target Bed file' used to Pipeline Module Running.
Module Example : 
    BED File has ONLY CHROMOSOME, START/END POSITION - Qualimap gtf Target Region input
    BED File has GENESYMBOL - Bedtools Coverage Calculation
'''%sys.argv[0]
    print(message)

def main() :
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input')
    parser.add_argument('-o', '--output')
    args = parser.parse_args()
    try : 
        len(args.input) > 0
    except :
        usage()
        sys.exit(2)
    
    bed_file_modifier(args.input, args.output)

if __name__ == '__main__' :
    main()
