"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.ram = [0] * 256
        self.pc = 0
        self.sp = 7
        self.reg[self.sp] = 0xF4
        self.flag = 0b00000000

    def load(self):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        with open(sys.argv[1]) as f:
            for line in f:
                string_val = line.split("#")[0].strip()
                if string_val == '':
                    continue
                v = int(string_val, 2)
                self.ram_write(address, v)
                address += 1
            
    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.flag = 0b00000001
            if self.reg[reg_a] < self.reg[reg_b]:
                self.flag = 0b00000100
            if self.reg[reg_a] > self.reg[reg_b]:
                self.flag = 0b00000010
        else:
            raise Exception("Unsupported ALU operation")


    def ram_read(self, mar):
        return self.ram[mar]

    def ram_write(self, mar, mdr):
        self.ram[mar] = mdr

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        instruction = self.ram[self.pc]
        LDI = 0b10000010
        PRN = 0b01000111
        ADD = 0b10100000
        MUL = 0b10100010
        CMP = 0b10100111
        PUSH = 0b01000101
        POP = 0b01000110
        CALL = 0b01010000
        RET = 0b00010001
        HLT = 0b00000001
        JEQ = 0b01010101
        JNE = 0b01010110
        JMP = 0b01010100

        halted = False
        while not halted:
            instruction = self.ram[self.pc]
            opr_a = self.ram_read(self.pc + 1)
            opr_b = self.ram_read(self.pc + 2)

            if instruction == LDI:
                self.reg[opr_a] = opr_b
                self.pc += 3

            elif instruction == PRN:
                print(self.reg[opr_a])
                self.pc +=2

            elif instruction == ADD:
                reg_a = self.ram[self.pc+1]
                reg_b = self.ram[self.pc+2]
                self.alu("ADD", reg_a, reg_b)
                self.pc +=3
            
            elif instruction == MUL:
                reg_a = self.ram[self.pc+1]
                reg_b = self.ram[self.pc+2]
                self.alu("MUL", reg_a, reg_b)
                self.pc +=3

            elif instruction == CMP:
                reg_a = self.ram[self.pc+1]
                reg_b = self.ram[self.pc+2]
                self.alu("CMP", reg_a, reg_b)
                self.pc +=3

            elif instruction == JMP:
                self.pc = self.reg[opr_a]

            elif instruction == JEQ:
                if self.flag == 0b00000001:
                    self.pc = self.reg[opr_a]
                else:
                    self.pc +=2

            elif instruction == JNE:
                if self.flag != 0b00000001:
                    self.pc = self.reg[opr_a]
                else:
                    self.pc +=2

                
            elif instruction == PUSH:
                self.reg[self.sp] -= 1
                reg_num = opr_a
                val = self.reg[reg_num]
                top_of_stack_address = self.reg[self.sp]
                self.ram[top_of_stack_address] = val
                self.pc += 2

            elif instruction == POP:
                top_of_stack_address = self.reg[self.sp]
                val = self.ram[top_of_stack_address]
                reg_num = opr_a
                self.reg[reg_num] = val

                self.reg[self.sp] += 1
                self.pc +=2

            elif instruction == CALL:
                return_addr = self.pc + 2
                self.reg[self.sp] -=1
                top_of_stack_address = self.reg[self.sp]
                self.ram[top_of_stack_address] = return_addr
                reg_num = opr_a
                subroutine_addr = self.reg[reg_num]
                self.pc = subroutine_addr

            elif instruction == RET:
                top_of_stack_address = self.reg[self.sp]
                return_addr = self.ram[top_of_stack_address]
                self.reg[self.sp] +=1
                self.pc = return_addr
            


            elif instruction == HLT:
                halted = True

            else:
                print(f'unknown instruction {instruction} at address {self.pc}')
                sys.exit(1)
        
