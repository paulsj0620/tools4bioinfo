[USAGE]

python bedfile_modifier.py -i <Design_ID.Raw.bed> -o <Design_ID.Modified.bed>

[PARAMETER]

-i, --input  : input bed file path
-o, --output : output bed file path

[PURPOSE]

This script converts 'Raw Target Bed file' into 'Modified Target Bed file' used to Pipeline Module Running.
Module Example : 
    BED File has ONLY CHROMOSOME, START/END POSITION - Qualimap gtf Target Region input
    BED File has GENESYMBOL - Bedtools Coverage Calculation
