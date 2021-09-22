input_queue_list = open("queue.status.txt", 'r')

for line in input_queue_list :
    if line[0] == '-' : #This line is Separate Line.
        continue
    
    if "KST" in line : #This line is Time Line.
        split_line = line.rstrip("\r\n").split(" ")
        day = split_line[0]
        month = split_line[1]
        date = split_line[3]
        time = split_line[4]
        year = split_line[6][-2:]
        
        output_fn = "queue_status.{0}.{1}.{2}.{3}.xls".format(year, month, date, time)
        output_status_xls = open(output_fn, "w")

    split_line = line.rstrip("\r\n").split(" ")
    if split_line[0] == "queuename" : #This line is Header Line.
        tmp_list = []
        for item in split_line :
            if item == "" :
                continue

            elif item == "queuename" :
                tmp_list.append(item)
                tmp_list.append("hostname")

            else :
                tmp_list.append(item)

        output_status_xls.write("\t".join(tmp_list) + "\n")
    
    if "@" in split_line[0] : #This line is INFO Line.
        tmp_list = []
        for item in split_line :
            if "@" in item :
                queuename = item.split("@")[0]
                hostname  = item.split("@")[1]
                tmp_list.append(queuename)
                tmp_list.append(hostname)
            elif item == "" : 
                continue
            else :
                tmp_list.append(item)
        
        output_status_xls.write("\t".join(tmp_list) + "\n")
output_status_xls.close()
