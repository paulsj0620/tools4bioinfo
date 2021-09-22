import glob
import itertools
from itertools import combinations

class VCFClass :
    def file_open(self, input_path, opt) : #file open
        meta = []
        header = []
        data = []

        file = open(input_path, 'r')
        for line in file :
            flag = line[:2]
            if flag == "##" :
                meta.append(line)
            elif '#' in flag :
                header.append(line)
            elif flag != '\n' and flag != '' :
                data.append(line)
            if not line :
                break
        if opt == "m" :
            return meta
        elif opt == "h" :
            return header
        elif opt == "d" : 
            return data
        file.close()

    def vcf_dic(self, data_list, chr_index, pos_index, ref_index, info_index) :
        list_dic = {}
        for temp_d in data_list :
            line = temp_d.split('\t')
            if len(line[ref_index]) == 1 and len(line[ref_index+1]) == 1 :
                temp_col = line[info_index+1].split(":")
                geno_index = temp_col.index("GT")
                geno_col = line[info_index+2].split(":")
                geno_list = geno_col[geno_index]
                combi = line[chr_index] + ' ' + line[pos_index]
                list_dic[combi] =  line[ref_index:ref_index+2], geno_list
            else :
                pass
        return list_dic

def find(data_list, column_name) :
    head_temp = data_list[0].split('\t')
    index_info = head_temp.index(column_name)
    return index_info

def concordance(dic1, dic2) :
    total = 0
    con = 0
    pro = 0
    for i in dic1.keys() :
        if i in dic2 :
            total += 1
            if dic1[i] == dic2[i] :
                con += 1
            elif dic1[i] != dic2[i]:
                pro += 1
                pass
        else :
            pass
    if total != 0 :
        rate = (float(con/total))*100
        print("Total : %s" % total)
        print("Matched : %s" % con)
        print("Unmatched : %s" % pro)
        print("%0.6f" % rate + "% concordance\n")
    else :
        print("total is 0")
    
def total_concordance(file1, file2) :
    vcf1 = VCFClass()
    vcf2 = VCFClass()

    vcf1_header = vcf1.file_open(file1, "h")
    vcf2_header = vcf2.file_open(file2, "h")


    vcf1_data = vcf1.file_open(file1, "d")
    vcf2_data = vcf2.file_open(file2, "d")

    vcf1_pos = find(vcf1_header, "POS")
    vcf2_pos = find(vcf2_header, "POS")

    vcf1_ref = find(vcf1_header, "REF")
    vcf2_ref = find(vcf1_header, "REF")

    vcf1_chr = find(vcf1_header, "#CHROM")
    vcf2_chr = find(vcf2_header, "#CHROM")

    vcf1_info = find(vcf1_header, "INFO")
    vcf2_info = find(vcf2_header, "INFO")

    dic1 = vcf1.vcf_dic(vcf1_data, vcf1_chr, vcf1_pos, vcf1_ref, vcf1_info)
    dic2 = vcf2.vcf_dic(vcf2_data, vcf2_chr, vcf2_pos, vcf2_ref, vcf2_info)

    print("%s : %s" % (file1, file2))
    concordance(dic1, dic2)

file_list = []
for filename in glob.glob('*.vcf') :
    file_list.append(filename)

for i in list(combinations(file_list, 2)) : 
    total_concordance(i[0], i[1])