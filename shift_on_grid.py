"""
This file implements a function that takes a numpy array and shifts all the points onto a grid set by multiples of 16.
Returns an array.
Author: Abhishek K
"""


def parse_z(curr_z, Lines):
    # parses the unique z value for all x and y coordinates that belong to that z
    # then puts them into lists and grids them.
    global output_data
    x_cords = []
    y_cords = []

    for line in Lines:
        if (float(line[2]) == curr_z):
            x_cords.append(float(line[0]))
            y_cords.append(float(line[1]))
            
            
    # parse into y rows with x values   
    dimensions = []
    curr_y = y_cords[0]
    found_indices = []
    unique_y = []
    index = 0;


    for l in range(len(y_cords)):
        if (y_cords[l] != -1):
            curr_y = y_cords[l]
            for j in range(len(y_cords)):
                if (y_cords[j] == curr_y):
                    found_indices.append(j)
                    y_cords[j] = -1 # done with it
            dimensions.append([])
            unique_y.append(curr_y) # unique y
            for ix in found_indices:
                dimensions[index].append(x_cords[ix]) # add x cords
            index += 1
            found_indices = []


    # sort lists in ascending order
    for y in range(len(dimensions)):
        dimensions[y].sort()

    # shifting points
    base_x = dimensions[0][0] # grid will be based on this

    # make sure first point is on grid
    if (base_x % 16 >=8):
        base_x += 16 - (base_x % 16)
    if (base_x % 16 < 8):
        base_x -= (base_x%16)



    difference = 0
    for y in range(len(dimensions)):
        # print("now working on layer " + str(y) + " " + str(unique_y[y]) + " and x" + str(dimensions[y][0]))
        for x in range(len(dimensions[y])):
            difference = dimensions[y][x] % 16
            if difference >= 8:
                dimensions[y][x] = dimensions[y][x] + (16-difference)
                # print(16-difference)
            else:
                dimensions[y][x] = dimensions[y][x] - (difference)
                # print(difference)



    # putting back into plottable lists
    backupx = []
    backupy = []
    for y in range(len(dimensions)):
        for m in range(len(dimensions[y])):
            backupy.append(unique_y[y])
            backupx.append(dimensions[y][m])

    """
    output to file version
    for y in range(len(dimensions)):
        for m in range(len(dimensions[y])):
            # x y z 128 128 128 
            ofile.write(str(dimensions[y][m]) + " " + str(unique_y[y]) + " " + str(curr_z) + " 128 128 128")
            ofile.write('\n')
    """

    # prepare for output
    for y in range(len(dimensions)):
        for m in range(len(dimensions[y])):
            # x y z 128 128 128 
            output_data.append([dimensions[y][m], unique_y[y], curr_z, 128, 128, 128])


curr_z = 0
output_data = []
def shift_on_grid(input_data):
    global output_data
    global curr_z
    # Lines = ifile.readlines()
    Lines = input_data
    print("parsing each line")
    for line in Lines:
        # reading_z = line.split()[2]
        reading_z = line[2]
        
        if (float(reading_z) != float(curr_z)):
            # print("z-value: " + str(reading_z))
            parse_z(float(reading_z), Lines)
            curr_z = float(reading_z)
    print("end of parsing each line")
    print("-------")

    print("removing duplicates and returning output")
    output_data = list(map(list, set(map(tuple, output_data))))
    return output_data
