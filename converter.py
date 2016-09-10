import struct
import numpy as np

inputfile = "C:\\Users\\Kateryna\\data.npy"
outputfile = "C:\\Users\\Kateryna\\data.bin"

# load from the file
mat = np.load(inputfile)

# create a binary file
binfile = file(outputfile, 'wb')
# and write out two integers with the row and column dimension
header = struct.pack('2I', mat.shape[0], mat.shape[1])
binfile.write(header)
# then loop over columns and write each
for i in range(mat.shape[1]):
    data = struct.pack('%id' % mat.shape[0], *mat[:,i])
    binfile.write(data)
binfile.close()
