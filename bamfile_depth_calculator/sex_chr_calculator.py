file = open("chrX_depth.txt", 'r')
list_sum = 0
region = 0
for i in file :
    i = i.rstrip()
    each_line = i.split("\t")
    list_sum += int(each_line[7])
    region += 1
chrx_depth = list_sum/region
file.close

region = 0
file = open("chrY_depth.txt", 'r')
list_sum = 0
for i in file :
    i = i.rstrip()
    each_line = i.split("\t")
    list_sum += int(each_line[7])
    region += 1
chry_depth = list_sum/region
file.close
ratio = chrx_depth/chry_depth
print("chrX Depth : %s" % chrx_depth)
print("chrY Depth : %s" % chry_depth)
print("Ratio : %s" % ratio)