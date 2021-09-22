#!/bin/python
import argparse

def bed_file_modify(input_bed, output_bed) :

    file_opener = open(input_bed, 'r')
    file_saver  = open(output_bed, 'w')

    for line in file_opener :
        split_line = line.rstrip("\r\n").split("\t")
        if 'browser' in line :
            continue
        if 'track' in line :
            continue

        chromosome = split_line[0]
        chromStart = split_line[1]
        chromEnd   = split_line[2]
        name       = split_line[3]

        try :
            score = split_line[4]
        except IndexError :
            score = 0

        try :
            strand = split_line[5]
        except IndexError :
            strand = '.'
        file_saver.write("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\n".format(chromosome, chromStart, chromEnd, name, score, strand))

def main() :
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_bed')
    parser.add_argument('-o', '--output_bed')
    args = parser.parse_args()

    bed_file_modify(args.input_bed, args.output_bed)

if __name__ == '__main__':
    main()