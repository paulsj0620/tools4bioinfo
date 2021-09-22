#classification list 
meta   = []
header = []
data   = []

def classification(row): #VCF file classification
    flag = row[:2]
    if flag == '##': #meta information classification
        meta.append(row)
    elif '#' in flag : #header classification
        header.append(row)
    elif flag != '\n' and flag != '':  
        data.append(row) #data classification
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

file = open('AllgVCFsGenotyped.multisample.vcf','r')
for line in file :  
    classification(line)   
    if not line: 
        break    
file.close()
data_count = len(data)
print('DATA Count : %s' % data_count)
snpindel(data)

