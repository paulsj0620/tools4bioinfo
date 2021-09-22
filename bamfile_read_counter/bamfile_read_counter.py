import glob

input_f = open("example.per_t_metrics.txt", 'r')

on_tar_read = 0

for line in input_f : 
    line = line.rstrip('\n').split('\t')
    if line[0] == 'chrom' :
        idx_read_count = line.index("read_count")
        pass
    else :
        read_count = line[idx_read_count]
        on_tar_read += int(read_count)
print(on_tar_read)