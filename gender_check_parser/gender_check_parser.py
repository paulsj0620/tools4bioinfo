
input_gender_check = open("GENDER.txt", 'r')
input_sample_list = open("sample.list.txt", 'r')

Sample_OUTPUT = []
Sample_ID = {}

for line in input_sample_list :
    split_line = line.rstrip("\r\n").split("\t")
    TBI_ID = split_line[0]
    CST_ID = split_line[1]

    Sample_ID[TBI_ID] = CST_ID

print("Theragen_ID\tDelivery_ID\tAutosomeDP\tX_ChromosomeDP\tY_ChromosomeDP\tEstimate_Gender")

for line in input_gender_check :
    split_line = line.rstrip("\r\n").split(" ")
    if split_line[0] == "Autosome" :
        Sample_OUTPUT = []
        Sample_OUTPUT.append(split_line[4])

    elif split_line[0] == "X" :
        Sample_OUTPUT.append(split_line[5])

    elif split_line[0] == "Y" :
        Sample_OUTPUT.append(split_line[5])

    elif split_line[0] == "SAMPLE_NAME" :
        Sample_OUTPUT.insert(0, split_line[2])
        Sample_OUTPUT.insert(1, Sample_ID[split_line[2]])

    elif split_line[0] == "ESTIMATE" :
        Sample_OUTPUT.append(split_line[4])
        print("\t".join(Sample_OUTPUT))
        
