import sys
sys.path.append(".././VirtualModelTester/Assets/NonUnityFolder/RawFileFormatReader")
from rawFileFormatHandler import *
import mmap
import struct
import numpy as np
import csv

UNITY_IPC_SYNC = 1  # NOTE(KARAN): SET THIS TO 0 IF NO SYNC IS REQUIRED
START = 0
SIZE = 1
frame = 0

class Memory:
    def __init__(self, memoryName, layoutFile):
        self.layout = {}
        sections = []
        self.memorySize = 0

        memoryLayoutDescriptorHandle = open(layoutFile, 'r')
        memoryLayoutDescriptor = csv.reader(memoryLayoutDescriptorHandle)

        columnNames = next(memoryLayoutDescriptor)

        print("Memory Layout:")
        print(columnNames)

        for section in memoryLayoutDescriptor:
            sections.append(section)

        for i in range(0, len(sections)):
            print(sections[i][0], " | ", sections[i][1], " | ", sections[i][2])
            self.memorySize += int(sections[i][2])
            self.layout[sections[i][0]] = [int(sections[i][1]), int(sections[i][2])]

        self.file = mmap.mmap(-1, self.memorySize, memoryName)


def BytesToInt32(byte0, byte1, byte2, byte3):
    integer = byte0
    integer = (byte1 << 8) | integer
    integer = (byte2 << 16) | integer
    integer = (byte3 << 24) | integer
    return integer


def BytesArrayToInt32(fourBytesArray):
    return BytesToInt32(fourBytesArray[0], fourBytesArray[1], fourBytesArray[2], fourBytesArray[3])


def ReadInt(memory, sectionName):
    fourBytes = bytearray(memory.file[memory.layout[sectionName][START]: memory.layout[sectionName][START] + 4])
    return BytesArrayToInt32(fourBytes)


def ReadByte(memory, sectionName):
    return memory.file[memory.layout[sectionName][START]]


def WriteByte(memory, sectionName, value):
    memory.file[memory.layout[sectionName][START]] = value


def ReadByteArray(memory, sectionName):
    return memory.file[
           memory.layout[sectionName][START]: memory.layout[sectionName][START] + memory.layout[sectionName][SIZE]]


def ReadFloatArray(memory, sectionName):
    result = []
    sizeOfFloat = 4
    sizeOfArray = memory.layout[sectionName][SIZE]
    byteArray = ReadByteArray(memory, sectionName)
    numFloats = sizeOfArray // sizeOfFloat
    for i in range(0, numFloats):
        start = i * 4
        packedFloat = byteArray[start: start + 4]
        result.append(struct.unpack('f', packedFloat)[0])
    return result


def WriteFloatArray(memory, sectionName, floatArray):
    sectionOnePastEnd = memory.layout[sectionName][START] + memory.layout[sectionName][SIZE]
    for i in range(0, len(floatArray)):
        packedFloat = struct.pack('f', floatArray[i])
        start = memory.layout[sectionName][START] + (i * 4)
        assert (start + 4 <= sectionOnePastEnd)
        memory.file[start: start + 4] = packedFloat


def WriteByteArray(memory, sectionName, source):
    memory.file[
    memory.layout[sectionName][START]: memory.layout[sectionName][START] + memory.layout[sectionName][SIZE]] = source


def ReadImage(memory, sectionName):
    imageWidth = ReadInt(memory, sectionName + 'ImageWidth')
    imageHeight = ReadInt(memory, sectionName + 'ImageHeight')
    bytesPerPixel = ReadInt(memory, sectionName + 'BytesPerPixel')

    imageStart = memory.layout[sectionName][START]
    imageSize = memory.layout[sectionName][SIZE]
    imageByteData = bytearray(memory.file[imageStart: imageStart + imageSize])

    return BytesToNumpy(imageByteData, imageWidth, imageHeight, bytesPerPixel)
