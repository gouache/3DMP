#!/usr/bin/env python

import math
import re

class GcodeParser:

    def __init__(self):
        self.model = GcodeModel(self)
        self.lineNb = 0

    def parseFile(self, path):
        # read the gcode file
        with open(path, 'r') as f:
            # init line counter
            self.lineNb = 0
            # for all lines
            for line in f:
                # inc line counter
                self.lineNb += 1
                # remove trailing linefeed
                self.line = line.rstrip()
                # parse a line
                self.parseLine()

        self.model.postProcess()
        return self.model

    def parseLine(self):
        # strip comments:
        ## first handle round brackets
        #self.line = line.rstrip()
        command = re.sub("\([^)]*\)", "", self.line)
        ## then semicolons
        idx = command.find(';')
        if idx >= 0:
            command = command[0:idx].strip()

        ## detect line nunmber
        idx = command.find('N')
        if idx >= 0:
            number = command.split(None, 1)
            num = number[0] if (len(number)>0) else None
            command = number[1] if (len(number)>1) else None
            self.warn("num '%s'"%num)
            self.warn("command '%s'"%command)

        ## detect crc
        idx = command.find('*')
        if idx >= 0:
            csrc = command.split('*', 1)
            command = csrc[0] if (len(csrc)>0) else None
            crc = csrc[1] if (len(csrc)>1) else None
            self.warn("command '%s'"%command)
            self.warn("crc '%s'"%crc)

        ## detect unterminated round bracket comments, just in case
        idx = command.find('(')
        if idx >= 0:
            self.warn("Stripping unterminated round-bracket comment")
            command = command[0:idx].strip()

        # TODO strip logical line number & checksum

        # code is fist word, then args
        comm = command.split(None, 1)
        code = comm[0] if (len(comm)>0) else None
        args = comm[1] if (len(comm)>1) else None

        if code:
            if hasattr(self, "parse_"+code):
                getattr(self, "parse_"+code)(args)
            else:
                self.warn("Unknown code '%s'"%code)
        self.lineNb += 1
    def parseArgs(self, args):
        dic = {}
        if args:
            bits = args.split()
            for bit in bits:
                letter = bit[0]
                try:
                    coord = float(bit[1:])
                except ValueError:
                    coord = 1
                dic[letter] = coord
        return dic

    def parse_G0(self, args):
        # G0: Rapid move
        # same as a controlled move for us (& reprap FW)
        self.parse_G1(args, "G0")

    def parse_G1(self, args, type="G1"):
        # G1: Controlled move
        self.model.do_G1(self.parseArgs(args), type)

    def parse_G20(self, args):
        # G20: Set Units to Inches
        self.error("Unsupported & incompatible: G20: Set Units to Inches")

    def parse_G21(self, args):
        # G21: Set Units to Millimeters
        # Default, nothing to do
        pass

    def parse_G28(self, args):
        # G28: Move to Origin
        self.model.do_G28(self.parseArgs(args))

    def parse_G90(self, args):
        # G90: Set to Absolute Positioning
        self.model.setRelative(False)

    def parse_G91(self, args):
        # G91: Set to Relative Positioning
        self.model.setRelative(True)

    def parse_G92(self, args):
        # G92: Set Position
        self.model.do_G92(self.parseArgs(args))

    def warn(self, msg):
        print ("[WARN] Line %d: %s (Text:'%s')" % (self.lineNb, msg, self.line))

    def error(self, msg):
        print ("[ERROR] Line %d: %s (Text:'%s')" % (self.lineNb, msg, self.line))
        raise Exception("[ERROR] Line %d: %s (Text:'%s')" % (self.lineNb, msg, self.line))

class GcodeModel:

    def __init__(self, parser):
        # save parser for messages
        self.parser = parser
        # latest coordinates & extrusion relative to offset, feedrate
        self.relative = {
            "X":0.0,
            "Y":0.0,
            "Z":0.0,
            "F":0.0,
            "E":0.0}
        # offsets for relative coordinates and position reset (G92)
        self.offset = {
            "X":0.0,
            "Y":0.0,
            "Z":0.0,
            "E":0.0}
        # if true, args for move (G1) are given relatively (default: absolute)
        self.isRelative = False
        # the segments
        self.segments = []
        self.layers = None
        self.distance = None
        self.extrudate = None

    def do_G1(self, args, type):
        # G0/G1: Rapid/Controlled move
        # clone previous coords
        coords = dict(self.relative)
        # update changed coords
        for axis in args.keys():
            #if coords.has_key(axis):
            if axis in coords:
                if self.isRelative:
                    coords[axis] += args[axis]
                else:
                    coords[axis] = args[axis]
            else:
                self.warn("Unknown axis '%s'"%axis)
        # build segment
        absolute = {
            "X": self.offset["X"] + coords["X"],
            "Y": self.offset["Y"] + coords["Y"],
            "Z": self.offset["Z"] + coords["Z"],
            "F": coords["F"],   # no feedrate offset
            "E": self.offset["E"] + coords["E"]
        }

        # update model coords
        self.relative = coords
        print(absolute)
        #print("isRelative = %d"%self.isRelative)
        #print(len(self.segments))

    def do_G28(self, args):
        # G28: Move to Origin
        self.warn("G28 unimplemented")

    def do_G92(self, args):
        # G92: Set Position
        # this changes the current coords, without moving, so do not generate a segment

        # no axes mentioned == all axes to 0
        if not len(args):
            args = {"X":0.0, "Y":0.0, "Z":0.0, "E":0.0}

        # update specified axes
        for axis in args.keys():
            #if self.offset.has_key(axis):
            if axis in self.offset:
                # transfer value from relative to offset
                self.offset[axis] += self.relative[axis] - args[axis]
                self.relative[axis] = args[axis]
            else:
                self.warn("Unknown axis '%s'"%axis)

    def setRelative(self, isRelative):
        self.isRelative = isRelative

    def addSegment(self, segment):
        self.segments.append(segment)
        #print segment

    def warn(self, msg):
        self.parser.warn(msg)

    def error(self, msg):
        self.parser.error(msg)

if __name__ == 'builtins':
    path = "xyzCalibration_cube.gcode"

    parser = GcodeParser()
    model = parser.parseFile(path)

    print (model)
