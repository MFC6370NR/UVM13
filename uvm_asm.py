import argparse
import json
import pprint

def asm_load_const(const1: int, address1: int):
    output = 0
    output |= 2

    const1_masked = const1 & 0xFFFF
    output |= (const1_masked << 3)
    address1_masked = address1 & 0x1F
    output |= (address1_masked << 19)

    return output.to_bytes(4, 'little')

def asm_read_value(src_addr: int, dst_addr: int):
    output = 0
    output |= 5
    output |= (src_addr & 0x7FF) << 3
    output |= (dst_addr & 0x1F) << 14
    return output.to_bytes(4, 'little')

def asm_write_value(src_addr: int, indirect_addr: int):
    output = 0
    output |= 6
    output |= (src_addr & 0x1F) << 3
    output |= (indirect_addr & 0x1F) << 8
    return output.to_bytes(4, 'little')

def asm_unar_minus(src_indirect_addr: int, dst_addr: int):
    output = 0
    output |= 4
    output |= (src_indirect_addr & 0x1F) << 3
    output |= (dst_addr & 0x1F) << 8
    return output.to_bytes(4, 'little')

def asm(IR):
    bytecode = bytes()
    for instruction in IR:
        op = instruction[0]
        args = instruction[1:]

        if op == 'load_const':
            bytecode += asm_load_const(const1=args[0], address1=args[1])
        elif op == 'read_value':
            bytecode += asm_read_value(src_addr=args[0], dst_addr=args[1])
        elif op == 'write_value':
            bytecode += asm_write_value(src_addr=args[0], indirect_addr=args[1])
        elif op == 'unar_minus':
            bytecode += asm_unar_minus(src_indirect_addr=args[0], dst_addr=args[1])
        else:
            print("ERROR ASM FUNC")
    return bytecode

def test():
    assert list(asm_load_const(const1=148, address1=8)) == [0xA2, 0x04, 0x40, 0x00]
    assert list(asm_read_value(src_addr=40, dst_addr=25)) == [0x45, 0x41, 0x06, 0x00]
    assert list(asm_write_value(src_addr=1, indirect_addr=16)) == [0x0E, 0x10, 0x00, 0x00]
    assert list(asm_unar_minus(src_indirect_addr=3, dst_addr=28)) == [0x1C, 0x1C, 0x00, 0x00]

def json_to_ir(json_data):
    IR = []
    for instruction in json_data:
        command = instruction["command"]
        if command == "load_const":
            IR.append(('load_const', instruction["args"][0], instruction["args"][1]))
        elif command == "read_value":
            IR.append(('read_value', instruction["args"][0], instruction["args"][1]))
        elif command == "write_value":
            IR.append(('write_value', instruction["args"][0], instruction["args"][1]))
        elif command == "unar_minus":
            IR.append(('unar_minus', instruction["args"][0], instruction["args"][1]))
    return IR

def full_asm(program_text):
    lines = program_text.strip().split('\n')
    IR = []
    for line in lines:
        if not line.strip():
            continue
        parts = line.split(';')
        op = parts[0]
        args = list(map(int, parts[1:]))
        IR.append((op, *args))
    bytecode = asm(IR)
    return bytecode, IR


def main():
    test()
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', required=True)
    parser.add_argument('-o', '--output', required=True)
    parser.add_argument('-t', '--test', required=True)
    args = parser.parse_args()
    print(args.input, args.output, args.test)

    with open(args.input) as file:
        json_data = json.load(file)

    IR = json_to_ir(json_data)
    bytecode = asm(IR)

    with open(args.output, 'wb') as output_file:
        output_file.write(bytecode)
    print(len(IR))

    if args.test == '1':
        pprint.pprint(IR)
        print(*[hex(i) for i in bytecode])

if __name__ == "__main__":
    main()