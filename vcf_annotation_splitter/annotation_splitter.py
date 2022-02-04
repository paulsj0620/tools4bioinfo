import argparse

def vcf_splitter(input, linecount, outprefix) :
    input_vcf_file = open(input, 'r')

    header_list = []
    variant_line_list = []

    chr_cursor = None
    file_count = 1
    for line in input_vcf_file :
        if line.startswith("#") : #this is header line.
            header_list.append(line)

        else : #this is data line. 
            split_line = line.rstrip("\r\n").split("\t")
            chr = split_line[0]
            pos = split_line[1]

            if chr_cursor == None :
                chr_cursor = chr
                start_pos = pos
                variant_line_list.append(line)

            elif chr_cursor == chr and len(variant_line_list) < linecount :
                variant_line_list.append(line)
                end_pos = pos

            elif len(variant_line_list) >= linecount :
                output_file_name = "{0}_{1}_{2}_{3}_{4}_split.snpeff.xls".format(outprefix, chr_cursor, file_count, start_pos, end_pos)
                output_vcf_file = open(output_file_name, 'w')
                for item in header_list :
                    output_vcf_file.write(item)
                for item in variant_line_list :
                    output_vcf_file.write(item)
                output_vcf_file.close()
                file_count += 1
                variant_line_list = []
                variant_line_list.append(line)
                start_pos = pos

            elif chr_cursor != chr :
                output_file_name = "{0}_{1}_{2}_{3}_{4}_split.snpeff.xls".format(outprefix, chr_cursor, file_count, start_pos, end_pos)
                output_vcf_file = open(output_file_name, 'w')
                for item in header_list :
                    output_vcf_file.write(item)
                for item in variant_line_list :
                    output_vcf_file.write(item)
                output_vcf_file.close()
                variant_line_list = []
                variant_line_list.append(line)
                chr_cursor = chr
                start_pos = pos
                file_count = 1
    
    output_file_name = "{0}_{1}_{2}_{3}_{4}_split.snpeff.xls".format(outprefix, chr_cursor, file_count, start_pos, end_pos)
    output_vcf_file = open(output_file_name, 'w')
    for item in header_list :
        output_vcf_file.write(item)
    for item in variant_line_list :
        output_vcf_file.write(item)
    output_vcf_file.close()
                    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='VCF File Handling')
    parser.add_argument('-i', '--input', metavar='path', required=True, help='Input fasta file')
    parser.add_argument('-c', '--linecount', metavar='linecount', required=True, help='Split line count')
    parser.add_argument('-o', '--outprefix', metavar='outprefix', required=True, help='Output prefix')
    args = parser.parse_args()

    vcf_splitter(args.input, int(args.linecount), args.outprefix)
