import sys
import os
comp_table = {
    "0":"0101010" , "1":"0111111" , "-1":"0111010" , "D":"0001100" , "A":"0110000" , "!D":"0001101" ,
    "!A":"0110001" , "-D":"0001111" , "-A":"0110011" , "D+1":"0011111" , "A+1":"0110111" , "D-1":"0001110" ,
    "A-1":"0110010" , "D+A":"0000010" , "D-A":"0010011" , "A-D":"0000111" , "D&A":"0000000" , "D|A":"0010101" ,
    "M":"1110000" , "!M":"1110001" , "-M":"1110011" , "M+1":"1110111" , "M-1":"1110010" , "D+M":"1000010" ,
    "D-M":"1010011" ,"M-D":"1000111" , "D&M":"1000000" , "D|M":"1010101" , "D<<" : "0110000" , "A<<":"0100000",
    "M<<":"1100000","D>>":"0010000","A>>":"0000000","M>>":"1000000"}
dest_table = {
    "null":"000" , "M":"001" , "D":"010" , "MD":"011" , "A":"100" , "AM":"101" , "AD":"110" , "AMD":"111"
}
jump_table = {
    "null":"000" , "JGT":"001" , "JEQ":"010" , "JGE":"011" , "JLT":"100" , "JNE":"101" , "JLE":"110" , "JMP":"111"
}
predefined_table = {
    "SP":0 , "LCL":1 , "ARG":2 , "THIS":3 , "THAT":4 , "SCREEN":16384 , "KBD":24576 ,
    "R0":0 , "R1":1 , "R2":2 , "R3":3 , "R4":4 , "R5":5 , "R6":6 , "R7":7 , "R8":8 ,
    "R9":9 , "R10":10 , "R11":11 , "R12":12 , "R13":13 , "R14":14 , "R15":15
}
variable_table = {}
label_table = {}

def fix_line(line):
    """ This function receives a line and erases the white spaces and comments """
    if line.startswith("//") or line == "\n":
        return -1
    line = line.strip()
    line = line.replace(' ','')
    comment=line.find("//")
    if (comment >= 0):
        line=line[:comment]
    return line

def a_instruction(line):
    """ This function receives a line which represents an a instruction and returns the binary code """
    if line.isdigit():
        return str(bin(int(line))[2:].zfill(16))
    else:
        if line in predefined_table:
            return str(bin(int(predefined_table[line]))[2:].zfill(16))
        if line in label_table:
            return str(bin(int(label_table[line]))[2:].zfill(16))
        if line in variable_table:
            return str(bin(int(variable_table[line]))[2:].zfill(16))

def c_instruction(line):
    """ This function receives a line which represents an c instruction and returns the binary code """
    equal = line.find("=")
    comma = line.find(";")
    if (line.find(">>") >= 0 or line.find("<<") >= 0):
        dest=line[:equal]
        comp=line[equal+1:]
        return "101" + comp_table[comp] + dest_table[dest] + jump_table["null"]
    if equal >=0 and comma >= 0:
        dest = line[:equal]
        comp = line[equal+1:comma]
        jump = line[comma+1:]
        return "111" + comp_table[comp] + dest_table[dest] + jump_table[jump]
    if equal >= 0 and comma == -1:
        dest = line[:equal]
        comp = line[equal+1:]
        return "111" + comp_table[comp] + dest_table[dest] + jump_table["null"]
    if comma >= 0 and equal == -1:
        comp=line[:comma]
        jump=line[comma+1:]
        return "111" + comp_table[comp] + dest_table["null"] + jump_table[jump]

def label_command(line, linecounter):
    """ This function receives a line which represents a label , a line counter and saves the label into the table """
    label_name = line[1:-1]
    label_table[label_name] = linecounter

def second_pass(inputfile):
    """ This function receives a file , reads it and saves the variables from it into a table """
    file = open(inputfile)
    line = file.readline()
    table_counter = 16
    while line:
        if fix_line(line) != -1:
            line = fix_line(line)
            if line.startswith("@"):
                if not line[1:].isdigit():
                    if line[1:] not in predefined_table and line[1:] not in label_table \
                            and line[1:] not in variable_table:
                        variable_table[line[1:]] = table_counter
                        table_counter += 1
        line = file.readline()
    file.close()

def first_pass(inputfile):
    """ This function receives a file , reads it and saves the labels from it into a table """
    file = open(inputfile)
    line = file.readline()
    linecounter = 0
    while line:
        if fix_line(line) != -1:
            line = fix_line(line)
            if line.startswith("("):
                label_command(line, linecounter)
                line = file.readline()
                continue
            linecounter += 1
        line = file.readline()
    file.close()

def write_hack(inputfile):
    """ This function gets the file , reads the instruction from it and converts it to binary code
    by the a_instruction and c_instruction and finally writes the translated command to an out file called xxx.hack"""
    point = inputfile.find(".")
    name = inputfile[:point]
    name = name + '.hack'
    outfile = open(name,'w')
    file = open(inputfile,'r')
    line = file.readline()
    while line:
        if fix_line(line) != -1 :
            line = fix_line(line)
            if line.startswith("@"):
                outfile.write(a_instruction(line[1:])+"\n")
            elif line.startswith("("):
                line = file.readline()
                continue
            else:
                outfile.write(c_instruction(line)+"\n")
        line = file.readline()
    file.close()
    outfile.close()

def main():
    """ The main function which runs the code """
    inputfile = sys.argv[1]
    if(os.path.isdir(inputfile)):
        for file in os.listdir(inputfile):
            first_pass(file)
            second_pass(file)
            write_hack(file)
    else:
        first_pass(inputfile)
        second_pass(inputfile)
        write_hack(inputfile)

if __name__ == '__main__':
    main()