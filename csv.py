
path = './data/google_transit/'

def read(file_name, operation):
    with open(path + file_name, 'r') as file:
        column_names = file.readline().rstrip().split(',')
        for line in file:
            line_values = line.rstrip().split(',')
            values = {}
            for column in column_names:
                values[column] = line_values[column_names.index(column)]
            operation(values)
