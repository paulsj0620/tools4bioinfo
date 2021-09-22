ref_file = open("Taxonomy.Annotation.xls", 'r')

scaffold_list = []

for line in ref_file : 
    line = line.rstrip('\n').split('\t')
    if line[5] == 'Homo_sapiens' :
        scaffold_list.append(line[0])

ref_file.close()
print(scaffold_list)
"""
input_file = open("Scaffold_nt.megablast")

for line in input_file :
    pars = line.rstrip('\n').split('\t')
"""