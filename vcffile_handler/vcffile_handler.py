import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='VCF File Handling')
    parser.add_argument('-i', '--input', metavar='path', required=False, help='Input the Path')
    parser.add_argument('-o', '--option', metavar='option', required=False, help='1:SNP/INDEL Count 2:Hetero&Homo 3:Ts/Tv A:All Result')
    args = parser.parse_args()

def classification(row): #VCF file classification
    flag = row[:2]
    if flag == '##': #meta information classification
        meta.append(row)
    elif '#' in flag : #header classification
        header.append(row)
    elif flag != '\n' and flag != '':  
        data.append(row) #data classification

#classification list 
meta   = []
header = []
data   = []

#file open -> classification
file = open(args.input, 'r')
for line in file :  
    classification(line)   
    if not line: 
        break    
file.close()
data_count = len(data)
print('DATA Count : %s' % data_count)

#definition for find index
#------------------------------------------------------
def find(header_col) :
    head_spl = header[0].split('\t')
    index_info = head_spl.index(header_col)
    return index_info+1

#SNP / INDEL Count
#------------------------------------------------------
def snpindel(data) : 
    header_index = find("REF")
    snp_count = 0   
    ins_count = 0
    del_count = 0
    for i in range(len(data)):
        column = data[i].split('\t')
        if ',' in column[header_index] :
            dic = column[header_index].split(',')
            for i in dic :
                if len(column[header_index-1]) == len(i) == 1 :
                    snp_count += 1
                elif len(column[header_index-1]) < len(i) :
                    ins_count += 1
                elif len(column[header_index-1]) > len(i) :
                    del_count += 1
                elif len(column[header_index-1]) == len(i) :
                    if column[header_index-1] == i :
                        pass
                    elif column[header_index-1] != i :
                        temp1 = list(column[header_index-1])
                        temp2 = list(i)
                        for j in range(len(temp1)) :
                            if temp1[j] == temp2[j] :
                                pass
                            elif temp1[j] != temp2[j] :
                                snp_count += 1
        else :
            if len(column[header_index-1]) == len(column[header_index]) :     
                snp_count += 1
            elif len(column[header_index-1]) < len(column[header_index]) :
                ins_count += 1
            elif len(column[header_index-1]) > len(column[header_index]) :
                del_count += 1      
    print('SNP : %d' % snp_count)
    print('Insertion : %d' % ins_count)
    print('Deletion : %d' % del_count)
#------------------------------------------------------

#Hetero / Homo Variants Count
#------------------------------------------------------
def hetehomo(data) :
    header_index = find("INFO")
    
    homo_ref = 0
    homo_alt = 0
    hetero = 0
    unmap = 0

    for i in range(len(data)) :
        column = data[i].split('\t')
        temp_col = column[header_index].split(':')
        geno_index = temp_col.index("GT")
        geno_col = column[header_index+1].split(':')
        geno_list = geno_col[geno_index].split('/')
        if geno_list[0] != '0|0' :
            if geno_list[0] == geno_list[1] and geno_list[0] == '0' :
                homo_ref += 1
            elif geno_list[0] == geno_list[1] and geno_list[0] == '.' : #./. : unmapped
                unmap += 1
            elif geno_list[0] == geno_list[1] and geno_list[0] != '0' :
                homo_alt += 1
            elif geno_list[0] != geno_list[1] : 
                hetero += 1
            else :
                print('This allele' + geno_list[1]) 
        else :
            homo_ref += 1
    print('Homozygous Variants : %d' % homo_alt)
    print('Homozygous Reference : %d' % homo_ref) #Homozygous Reference
    print('Heterozygous Variants : %d' % hetero)
    print('Unmapped : %d' % unmap)
#------------------------------------------------------

#Ts/Tv Ratio 
#------------------------------------------------------
def tstv(data) :
    transition = 0
    transversion = 0
    header_index = find("REF")

    for i in range(len(data)) :
        column = data[i].split('\t') 
        if len(column[header_index-1]) == len(column[header_index]) :     
            if column[header_index-1] == 'A' and column[header_index] == 'G' :
                transition += 1
            elif column[header_index-1] == 'G' and column[header_index] == 'A' :
                transition += 1
            elif column[header_index-1] == 'C' and column[header_index] == 'T' :
                transition += 1
            elif column[header_index-1] == 'T' and column[header_index] == 'C' :
                transition += 1
            else :
                transversion += 1

    ratio = (float(transition) / float(transversion))
    print('Ts/Tv ratio : %f' % ratio)
#------------------------------------------------------

#VCF Pass Filter
#------------------------------------------------------
def passfilter(data) :
    pass_count = 0
    low_quality = 0
    
    header_index = find("FILTER")

    for i in range(len(data)) :
        column = data[i].split('\t') 
        if column[header_index-1] == 'PASS' :
            pass_count += 1
        elif column[header_index-1] == 'LowQual' :
            low_quality += 1
    print("PASS Filter : %d" % pass_count)
    print("Low Quality : %d" % low_quality)
#------------------------------------------------------

if args.option == '1' :
    snpindel(data)
elif args.option == '2' :
    hetehomo(data)
elif args.option == '3' :
    tstv(data)
elif args.option == '4' :
    passfilter(data)
elif args.option == 'A' or args.option == 'a' :
    snpindel(data)
    hetehomo(data)
    tstv(data)
    #passfilter(data)
else :
    print('Choose 1~3')  