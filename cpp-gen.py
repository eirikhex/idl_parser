##!/usr/bin/env python3

import re
from idl_parser import parser
import idl_parser

def  generate_cpp(idl_str):

    _parser = parser.IDLParser()
    _parser._verbose=True
    _parser.global_module._verbose=True

    output_string = ""

    # idl = _parser.load(idl_str, include_dirs=[])
    _parser.parse(["idls\multi_module_test.idl"],["idls"])
    idl = _parser.global_module
    print(idl.modules[0].structs[0].name)
    #idl_dict = idl.to_dic()
    for module in idl.modules:
        output_string += generate_module(module)

    print(output_string)

def add_tab(string):
    if string == "":
        return ""
    else:
        return "    ".join(('\n'+string.lstrip()).splitlines(True))

def is_filepath_same_as_parent(idl_type):
    return idl_type.parent.filepath == idl_type.filepath

def get_namespace(idl_type):
    namespace = []
    parent = idl_type.parent
    while not parent.name == "__global__":
        if parent.classname == "IDLModule":
            namespace.append(parent.name)

        parent = parent.parent

    namespace.reverse()
    return namespace



def generate_module(parent_module):
    if not is_filepath_same_as_parent(parent_module):
        return ""

    out = "namespace " + parent_module.name +"\n{"
    for module in parent_module.modules:
        out += add_tab(generate_module(module))

    for struct in parent_module.structs:
        out += add_tab(generate_struct(struct))

    for enum in parent_module.enums:
        out += add_tab(generate_enum(enum))



    out += "\n};\n"
    return out

def generate_struct(struct):
    if not is_filepath_same_as_parent(struct):
        return ""

    print(get_namespace(struct))

    out = "struct " + struct.name +"\n{"

    for member in struct.members:
        out += add_tab(generate_member(member))


    out += "\n};"
    return out

def generate_conversion_struct(struct):

    # namespace here, or outside?

    typename = struct.type.name
    ddstype = typename + "_" # check this, might be redundant to dds namespace
    fileBasename = typename + 'Converter'

    out = "#include \""+ fileBasename + ".h\" \n #include <utility>\n\n"
    out += ddstype + "toDds("+typename +"inMsg)\n"
    out += "{\n"
    out += ddstype + " outMsg;\n"
    for member in struct.members:
        if member.type.is_primitive:
            out +="outMsg."+member.name+"(inMsg."+member.name+");"
        elif member.type.is_array:
            pass
        elif member.type.is_sequence:
            pass
        else:
            out += "outMsg."+member.name +"= fromDds(inMsg."+member.name+"());"



    out += "return outMsg;\n"
    out += "}\n"



    #  base conversion
    # conversion forwarders for subscribers
    # conversion forwarders for publishers


    return out

def generate_enum(enum_dict):
    return ""

def generate_union(union_dict):
    return ""

def generate_member(member):
    if not is_filepath_same_as_parent(member):
        return ""




    init_value = ""
    out = ""
    member_type = ""
    array = ""

    if(member.is_const):
        member_type += "const "

    print(member.name)
    if member.type.is_enum or member.type.is_struct or member.type.is_union:
        print("Compare:")
        member_namespace = get_namespace(member)
        type_namespace = get_namespace(member.type)
        if member_namespace != type_namespace:
            member_type = "::".join(type_namespace) + "::" +member.type.name
        else:
            member_type = member.type.name
    # if type(member.type) is idl_parser.type.IDLPrimitive:
    elif member.type.is_primitive:
        member_type = str(member.type)
        if member_type.startswith("@default"):
            strings = member_type.split(" ")
            init_value = re.findall("value=\d",member_type.strip())[0].replace("value", "")
            member_type = generate_type(strings[-1])
        else:
            member_type = generate_type(member_type)
    elif member.type.is_sequence:
        member_type = "std::vector<"+str(member.type.inner_type) + ">"
    elif member.type.is_array:
        member_type = str(member.type.inner_type)
        array = "["+ str(member.type.size) + "]"
    else:
        member_type = member.type.name

    out = member_type + " " + member.name +array + init_value + ";"

    return out

def generate_type(idl_type):

    if idl_type == "boolean":
        return "bool"
    elif idl_type == "string":
        return "std::string"
    elif idl_type == "octet":
        return "uint8_t"
    elif idl_type == "short":
        return "int16_t"
    elif idl_type == "unsigned short":
        return "uint16_t"
    elif idl_type == "long long":
        return "int64_t"
    elif idl_type == "unsigned long long":
        return "uint64_t"
    elif type(idl_type) is idl_parser.struct.IDLStruct:
        return idl_type.type
    else:
        return idl_type





if __name__ == '__main__':
    import getopt, sys


    # Remove 1st argument from the
    # list of command line arguments
    argumentList = sys.argv[1:]

    inputfile = ""
    outputfile = ""

    # Options
    options = "hi:o:"

    # Long options
    long_options = ["Help", "Input=", "Output="]

    try:
        # Parsing argument
        arguments, values = getopt.getopt(argumentList, options, long_options)

        # checking each argument
        for currentArgument, currentValue in arguments:

            if currentArgument in ("-h", "--Help"):
                print ("Displaying Help")

            elif currentArgument in ("-i", "--Input"):
                inputfile = currentValue

            elif currentArgument in ("-o", "--Output"):
                print (("Enabling special output mode (% s)") % (currentValue))

    except getopt.error as err:
        # output error, and return with an error code
        print (str(err))

    # if inputfile == "":
    #     print("No input file specified.. Exiting")
    #     exit()

    # idl_content = ""
    # with open(inputfile) as reader:
    #     idl_content = reader.read()


    outputstring = generate_cpp(inputfile)