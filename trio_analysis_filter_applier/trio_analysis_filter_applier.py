import os, sys
import argparse

def trio_mutation_filter(input_file, output_file, type, filt_set, trio_list) :
    input_fp = open(input_file, 'r')
    output_fp = open(output_file, 'w')
    
    PROBAND_GT_TAG = "GEN[{0}].GT".format(trio_list[0])
    FATHER_GT_TAG  = "GEN[{0}].GT".format(trio_list[1])
    MOTHER_GT_TAG  = "GEN[{0}].GT".format(trio_list[2])

    for line in input_fp :
        split_line = line.rstrip("\r\n").split("\t")
        
        if split_line[0] == "CHROM" : #This line is HEADER Line.
            idx_dic = dict()
            for idx, item in enumerate(split_line) :
                idx_dic.setdefault(item, idx)

            split_line.append("type_filter")
            split_line.append("EFFECT_filter")
            split_line.append("SIFT_filter")
            split_line.append("PHAST_filter")
            split_line.append("Freq_ExAC_filter")
            split_line.append("Freq_GNOMAD_filter")

            output_fp.write("\t".join(split_line) + "\n")
            continue

        elif split_line[0] != "CHROM" : #This line is DATA Line.
            PROBAND_GT = split_line[idx_dic[PROBAND_GT_TAG]]
            FATHER_GT  = split_line[idx_dic[FATHER_GT_TAG]]
            MOTHER_GT  = split_line[idx_dic[MOTHER_GT_TAG]]

            SIFT_LIST  = split_line[idx_dic["dbNSFP_SIFT_pred"]]
            POLY_LIST  = split_line[idx_dic["dbNSFP_Polyphen2_HDIV_pred"]]

            PHAST_LIST = split_line[idx_dic["dbNSFP_phastCons100way_vertebrate"]]

            ExAC_AF_LIST = split_line[idx_dic["ExAC_AF"]]
            GNOMAD_AF_LIST = split_line[idx_dic["GNOMAD_AF"]]

            EFFECT_LIST  = split_line[idx_dic["ANN[*].EFFECT"]]
            EFFECT_PRESET = ["chromosome", "exon_loss_variant", "frameshift_variant", "rare_amino_acid_variant", "splice_acceptor_variant", \
                    "splice_donor_variant", "stop_lost", "start_lost", "stop_gained", "coding_sequence_variant", "inframe_insertion", \
                    "disruptive_inframe_insertion", "inframe_deletion", "disruptive_inframe_deletion", "missense_variant"]
            
            
            #This is TYPE FILTER : dominant | recessive | denovo
            if (PROBAND_GT == "1/1" or PROBAND_GT == "1|1") and (FATHER_GT == "0/1" or FATHER_GT == "0|1") and (MOTHER_GT == "0/1" or MOTHER_GT == "0|1") :
                split_line.append("recessive")
            elif (PROBAND_GT == "1/1" or PROBAND_GT == "1|1") and (FATHER_GT == "0/0" or FATHER_GT == "0|0") and (MOTHER_GT == "0/0" or MOTHER_GT == "0|0") :
                split_line.append("denovo")
            else :
                continue
            #elif type == "dominant" : #Father / Mother Phenotype Check
            #    if {(PROBAND_GT == "0/1" or PROBAND_GT == "0|1") and (FATHER_GT == "0/1" or FATHER_GT == "0|1") and (MOTHER_GT == "0/0" or MOTHER_GT == "0|0")} or  \
            #        {(PROBAND_GT == "0/1" or PROBAND_GT == "0|1") and (FATHER_GT == "0/0" or FATHER_GT == "0|0") and (MOTHER_GT == "0/1" or MOTHER_GT == "0|1")} :
            #        print(split_line)
            
            if "EFFECT" in filt_set :
                effect_count = 0
                for EFFECT in EFFECT_LIST.split("&") :
                    if EFFECT in EFFECT_PRESET :
                        effect_count += 1
                if effect_count >= 1 :
                    split_line.append("O")
                else :
                    split_line.append("X")
                
                

            #Apply the filter by Filt Set
            if "SIFT" in filt_set :
                if ("D" in SIFT_LIST) or ("P" in POLY_LIST) or ("D" in POLY_LIST) :
                    split_line.append("O")
                else :
                    split_line.append("X")

            if "PHAST" in filt_set :
                phast_count = 0
                for PHAST in PHAST_LIST.split(",") :
                    if PHAST != "." :
                        if float(PHAST) >= float(0.2) :
                            phast_count += 1
                    elif PHAST == "." :
                        phast_count += 1
                if phast_count >= 1 :
                    split_line.append("O")
                else :
                    split_line.append("X")

            if "Freq_ExAC" in filt_set :
                exac_count = 0
                for exac_af in ExAC_AF_LIST.split(",") :
                    if exac_af == "." :
                        exac_count += 1
                    elif float(exac_af) < 0.01 :
                        exac_count += 1
                if exac_count >= 1 :
                    split_line.append("O")
                else :
                    split_line.append("X")

            if "Freq_GNOMAD" in filt_set :
                gnomad_count = 0
                for gnomad_af in GNOMAD_AF_LIST.split(",") :
                    if gnomad_af == "." :
                        gnomad_count += 1
                    elif float(gnomad_af) < 0.00025 :
                        gnomad_count += 1
                if gnomad_count >= 1 :
                    split_line.append("O")
                else :
                    split_line.append("X")
        output_fp.write("\t".join(split_line) + "\n")

def filter_append(filter_select) :
    filter_list = []
    filters = filter_select
    split_filt = filters.split(",")
    for item in split_filt :
        filter_list.append(item)
    return filter_list

def usage() :
    message='''
[USAGE]
python %s -i multi.snpeff.tsv -o multi.snpeff.filtered -t recessive -a EFFECT,SIFT,PHAST -p TBI_ID -f TBI_ID -m TBI_ID

[PARAMETER]
-i, --input              : input file path
-o, --output             : output prefix
-t, --trio_mutation_type : dominant | recessive | denovo (Choose Only One)
-a, --apply_filter       : EFFECT | SIFT | PHAST | Freq_ExAC | Freq_GNOMAD (Seperate by ,)
-p, --proband_sampleID   : TBI_ID (TN-) 
-f, --father_sampleID    : TBI_ID (TN-)
-m, --mother_sampleID    : TBI_ID (TN-)

[PURPOSE]
''' %sys.argv[0]
    print(message)

def main() :
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_snpeff_tsv')
    parser.add_argument('-o', '--output_prefix')
    parser.add_argument('-t', '--trio_mutation_type')
    parser.add_argument('-a', '--apply_filter')
    parser.add_argument('-p', '--proband_sampleID')
    parser.add_argument('-f', '--father_sampleID')
    parser.add_argument('-m', '--mother_sampleID')
    args = parser.parse_args()

    try : 
        len(args.input_snpeff_tsv) > 0

    except :
        usage()
        sys.exit(2)

    trio_set = [args.proband_sampleID, args.father_sampleID, args.mother_sampleID]
    filter_set = filter_append(args.apply_filter)
    trio_mutation_filter(args.input_snpeff_tsv, args.output_prefix, args.trio_mutation_type, filter_set, trio_set)

if __name__ == '__main__' :
    main()