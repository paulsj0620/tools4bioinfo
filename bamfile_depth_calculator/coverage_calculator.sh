#!/bin/bash
sample_id=$1
project_path=/Project
bam_path=$project_path/$sample_id/
bam_file=$bam_path/$sample_id.printrecal.bam
bed_file=Target.bed

out_path=$project_path/$sample_id/
mkdir -p $out_path

date
echo "chr	start	end	gene	$sample_id" > $out_path/$sample_id.count.txt
/BiO/BioTools/bedtools/bedtools-2.17.0/bin/coverageBed \
    -abam $bam_file \
    -b $bed_file \
    -d | \
    sort -k1,1 -k2,2n | /BiO/BioTools/bedtools/bedtools-2.17.0/bin/groupBy -g 1,2,3,4 -c 6 -o mean >> $out_path/$sample_id.count.txt 
date
