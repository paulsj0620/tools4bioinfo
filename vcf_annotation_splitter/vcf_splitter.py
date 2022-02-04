import argparse

def vcf_splitter(input, linecount, outprefix) :
    input_vcf_file = open(input, 'r')

    header_list = []
    
    small_contig = []
    large_contig = []

    lc_variant_line_list = []
    sc_variant_line_list = []

    chr_cursor = None
    file_count = 1
    for line in input_vcf_file :
        if line.startswith("#") : #this is header line.
            header_list.append(line)
            if line.startswith("##contig") :
                split_contig_line = line.rstrip("\r\n").split(">")[0].split(",")
                contig_name = split_contig_line[0].split("ID=")[1]
                length      = int(split_contig_line[1].split("length=")[1])
                if length < 100000 :
                    small_contig.append(contig_name)
                elif length >= 100000 :
                    large_contig.append(contig_name)

        else : #this is data line. 
            split_line = line.rstrip("\r\n").split("\t")
            chr = split_line[0]
            pos = split_line[1]

            if chr in large_contig :
                if chr_cursor == None :
                    chr_cursor = chr
                    start_pos = pos
                    lc_variant_line_list.append(line)

                elif chr_cursor == chr and len(lc_variant_line_list) < linecount :
                    lc_variant_line_list.append(line)
                    end_pos = pos

                elif len(lc_variant_line_list) >= linecount :
                    output_file_name = "{0}_{1}_{2}_{3}_{4}_split.vcf".format(outprefix, chr_cursor, file_count, start_pos, end_pos)
                    output_vcf_file = open(output_file_name, 'w')
                    for item in header_list :
                        output_vcf_file.write(item)
                    for item in lc_variant_line_list :
                        output_vcf_file.write(item)
                    output_vcf_file.close()
                    file_count += 1
                    lc_variant_line_list = []
                    lc_variant_line_list.append(line)
                    start_pos = pos

                elif chr_cursor != chr :
                    output_file_name = "{0}_{1}_{2}_{3}_{4}_split.vcf".format(outprefix, chr_cursor, file_count, start_pos, end_pos)
                    output_vcf_file = open(output_file_name, 'w')
                    for item in header_list :
                        output_vcf_file.write(item)
                    for item in lc_variant_line_list :
                        output_vcf_file.write(item)
                    output_vcf_file.close()
                    lc_variant_line_list = []
                    lc_variant_line_list.append(line)
                    chr_cursor = chr
                    start_pos = pos
                    file_count = 1

            elif chr in small_contig :
                sm_file_count = 1
                if len(sc_variant_line_list) < linecount : 
                    sc_variant_line_list.append(line)
                elif len(sc_variant_line_list) >= linecount :
                    output_smfile_name = "{0}_small_{1}_split.vcf".format(outprefix, sm_file_count)
                    for item in header_list :
                        output_smfile_name.write(item)
                    for item in sc_variant_line_list :
                        output_smfile_name.write(item)
                    output_smfile_name.close()
                    sm_file_count += 1

    if small_contig != [] :
        output_smfile_name = "{0}_small_{1}_split.vcf".format(outprefix, sm_file_count)
        for item in header_list :
            output_smfile_name.write(item)
        for item in sc_variant_line_list :
            output_smfile_name.write(item)
        output_smfile_name.close()
    
    output_file_name = "{0}_{1}_{2}_{3}_{4}_split.vcf".format(outprefix, chr_cursor, file_count, start_pos, end_pos)
    output_vcf_file = open(output_file_name, 'w')
    for item in header_list :
        output_vcf_file.write(item)
    for item in lc_variant_line_list :
        output_vcf_file.write(item)
    output_vcf_file.close()
                    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='VCF File Handling')
    parser.add_argument('-i', '--input', metavar='path', required=True, help='Input fasta file')
    parser.add_argument('-c', '--linecount', metavar='linecount', required=True, help='Split line count')
    parser.add_argument('-o', '--outprefix', metavar='outprefix', required=True, help='Output prefix')
    args = parser.parse_args()

    vcf_splitter(args.input, int(args.linecount), args.outprefix)