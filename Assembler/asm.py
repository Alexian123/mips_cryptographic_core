import sys
import re
from enum import Enum

class Assembler:    
    
    class NumericBase(Enum):
        HEX = 16
        BIN = 2

    __REGISTERS = {
        'acc':  0b00,
        'x':    0b01,
        'y':    0b10,
        'sp':   0b11
    }

    __INSTRUCTIONS = {
        # Cryptography
        'decc': 0b001111,
        'encc': 0b001110,
        'de64': 0b001101,
        'en64': 0b001100,

        # ALU
        'and':  0b000000,
        'or':   0b000001,
        'xor':  0b000010,
        'add':	0b000011,
        'sub':  0b000111,
        'andi':	0b010000,
        'ori':	0b010001,
        'xori':	0b010010,
        'addi': 0b010011,
        'subi':	0b010111,

        # BRANCH
        'bra':	0b100000,
        'brz':	0b100001,
        'brc':	0b100010,
        'bro':	0b100011,
        'brn':	0b100100,
        'bnz':	0b100101,
        'bnc':	0b100110,
        'bno':	0b100111,
        'brp':	0b101000,

        # MEMORY
        'ldw':	0b110000,
        'stw':	0b111111
    }

    def __init__(self):
        self.__machine_code_instructions = []
        self.__label_addresses = {}
        self.__INSTRUCTION_TYPE_HANDLERS = {
                0b00: self.__encode_R_instruction,
                0b01: self.__encode_I_instruction,
                0b10: self.__encode_J_instruction,
                0b11: self.__encode_R_instruction
        }
    
    def assemble(self, asm_code: str):
        lines, line_no = asm_code.split('\n'), 0
        self.__store_label_addresses(lines)
        for line in lines:
            line_no += 1
            asm_line = line.lstrip()
            if asm_line == "" or asm_line.isspace() or asm_line.startswith('#'):  # ignore comments and empty lines
                continue
            machine_code = self.__encode_instruction(asm_line, line_no)
            self.__machine_code_instructions.append(machine_code)

    def get_machine_code_as_str(self, header=True, addresses=True, base=NumericBase.HEX):
        code, i = '', 0
        if header:
            print(('Address\t\tData\t\tLabel' if addresses else 'Data\t\tLabel'))
            print('------------------------------------------')
        for instruction in self.__machine_code_instructions:
            code += (f'0x{i:02x}\t\t' if addresses else '')
            if base is self.NumericBase.HEX:
                code += f'{int(instruction):04x}'
            elif base is self.NumericBase.BIN:
                code += f'{int((instruction & 0xF000) >> 12):04b} {int((instruction & 0xF00) >> 8):04b} {int((instruction & 0xF0) >> 4):04b} {int((instruction & 0xF)):04b}'
            try:
                label = (list(self.__label_addresses.keys()) [list(self.__label_addresses.values()).index(i)])
                code += f'\t\t{label}\n'
            except ValueError as e:
                code += f'\t\t-\n'
            i += 1
        return code
        
    def generate_logisim_img(self, name='a.out', header='v2.0 raw'):
        img_file, i = open(name, 'w'), 1
        img_file.write(f'{header}\n')
        for instruction in self.__machine_code_instructions:
            img_file.write(f'{int(instruction):x}')
            img_file.write('\n' if i % 8 == 0 else ' ')
            i += 1
        img_file.close()
    

    def __store_label_addresses(self, asm_lines: list[str]):
        address = 0
        for line in asm_lines:
            asm_line = line.lstrip()
            if asm_line == "" or asm_line.isspace() or asm_line.startswith('#'):  # ignore comments and empty lines
                continue
            tokens = re.findall(r"[\w':#]+", line)
            if str(tokens[0]).endswith(':'):
                self.__label_addresses[str(tokens[0])[:-1]] = address    # store label address
            address += 1

    def __encode_instruction(self, asm_line: str, line_no: int):
        tokens = re.findall(r"[\w':#]+", asm_line)
        try:
            if str(tokens[0]).endswith(':'):    # skip label
                tokens.remove(tokens[0])
            opcode = Assembler.__INSTRUCTIONS[str(tokens[0]).lower()]
            type_bits = (opcode >> 4) & 0b11
            return self.__INSTRUCTION_TYPE_HANDLERS[type_bits](opcode, tokens[1:])
        except (KeyError, IndexError) as e:
            print(f'ERROR on line {line_no}: invalid mnemonic')
            print(f'code: {asm_line}')
            sys.exit(1)
        except ValueError as e:
            print(f'ERROR on line {line_no}: invalid immediate value')
            print(f'code: {asm_line}')
            sys.exit(1)
        except SyntaxError as e:
            print(f'ERROR on line {line_no}: {e.msg}')
            print(f'code: {asm_line}')
            sys.exit(1)
        except Exception as e:
            print(e.with_traceback())
            print(f'code: {asm_line}')
            sys.exit(1)

    def __encode_R_instruction(self, opcode: int, operands: list):
        if len(operands) < 2 or (len(operands) >= 3 and not str(operands[2]).startswith('#')):
            raise SyntaxError('R-Type instruction requires 2 registers as arguments')
        dest_reg = Assembler.__REGISTERS[str(operands[0]).lower()]
        src_reg = Assembler.__REGISTERS[str(operands[1]).lower()]
        return ((((opcode << 2) | dest_reg) << 2) | src_reg) << 6   # 6 'unused' bits

    def __encode_I_instruction(self, opcode: int, operands: list):
        if len(operands) < 2 or (len(operands) >= 3 and not str(operands[2]).startswith('#')):
            raise SyntaxError('I-Type instruction requires a register and an 8-bit signed integer as arguments')
        dest_reg = Assembler.__REGISTERS[str(operands[0]).lower()]
        sign_imm = int(operands[1])
        return (((opcode << 2) | dest_reg) << 8) | (sign_imm & 0x00FF)

    def __encode_J_instruction(self, opcode: int, operands: list):
        if len(operands) < 1 or (len(operands) >= 2 and not str(operands[1]).startswith('#')):
            raise SyntaxError('J-Type instruction requires a label as the argument')
        if operands[0] not in self.__label_addresses.keys():
            raise SyntaxError(f'label {operands[0]} not found')
        return (opcode << 10) | self.__label_addresses[operands[0]]


def main():
    if len(sys.argv) < 2:
        print(f'Usage: python {sys.argv[0]} <asm_source_file> [<output_file>]')
        exit(1)

    asm_code = open(sys.argv[1], 'r').read()

    assembler = Assembler()
    assembler.assemble(asm_code)

    print(assembler.get_machine_code_as_str())

    if len(sys.argv) >= 3:
        assembler.generate_logisim_img(sys.argv[2])

if __name__ == "__main__":
    main()
