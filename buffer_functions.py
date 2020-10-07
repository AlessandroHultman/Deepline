

def read(buffer, filename):
    with open(filename, "r") as f:
	    file_contents = f.readlines()
        
        #buffer.currentine_index


def write(buffer):
    pass

def print(buffer):
    for line in buffer.lines:
        print(line)