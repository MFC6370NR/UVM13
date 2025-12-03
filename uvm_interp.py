import argparse
import xml.etree.ElementTree as ET


def mask(n):
    return ((2 ** n) - 1)


def execute(bytecode):
    memory = [0] * 32
    regs = [0] * 32
    for i in range(0, len(bytecode), 4):
        command = bytecode[i:i + 4]
        command = int.from_bytes(command, 'little')
        op = command & 0B111

        if op == 2:
            const = (command >> 3) & mask(16)
            address = (command >> 19) & mask(5)
            regs[address] = const
        elif op == 5:
            src_addr = (command >> 3) & mask(11)
            dst_addr = (command >> 14) & mask(5)
            value = memory[src_addr]
            regs[dst_addr] = value
        elif op == 6:
            src_addr = (command >> 3) & mask(5)
            indirect_addr = (command >> 8) & mask(5)
            value = regs[src_addr]
            memory[regs[indirect_addr]] = value
        elif op == 4:
            src_indirect_addr = (command >> 3) & mask(5)
            dst_addr = (command >> 8) & mask(5)
            value =  memory[regs[src_indirect_addr]]
            result = -value
            regs[dst_addr] = result
    return regs, memory


def save_memory_dump(memory, filename, mem_range):
    root = ET.Element("memory_dump")
    start, end = map(int, mem_range.split('-'))

    for i in range(start, end + 1):
        cell = ET.SubElement(root, "cell")
        ET.SubElement(cell, "address").text = str(i)
        ET.SubElement(cell, "value").text = str(memory[i])

    tree = ET.ElementTree(root)
    tree.write(filename, encoding='utf-8', xml_declaration=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', required=True)
    parser.add_argument('-o', '--output', required=True)
    parser.add_argument('-r', '--range', required=True)
    args = parser.parse_args()

    with open(args.input, "rb") as file:
        bytecode = file.read()

    stack, memory = execute(bytecode)
    save_memory_dump(memory, args.output, args.range)

    print(f"Регистры: {stack}")
    print(f"Память: {memory}")


if __name__ == "__main__":
    main()