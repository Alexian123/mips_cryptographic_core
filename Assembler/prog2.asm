		# X := 'b' and store at Mem[0]
		ADDI X, 98
		STW X, ACC

		# Encrypt X with Caesar's Cypher and store at Mem[1]
		ENCC Y, X
		ADDI ACC, 1
		STW Y, ACC

		# Load encrypted value into X
		LDW X, ACC

		# Decrypt X with Caesar's Cypher
		DECC Y, X

		# Load initial value from Mem[0] into X
		XOR ACC, ACC	# ACC := 0
		LDW X, ACC

		# Check if Decrypted value == Initial value
		SUB X, Y
		BRZ EQUAL1	# if equal: continue
STOP1:	BRA STOP1	# else:	stop here

EQUAL1:	ADD X, Y	# restore X ('b')

		# Encrypt X with Base64 and store at Mem[2]
		ADDI ACC, 2
		EN64 Y, X
		STW Y, ACC
		
		# Load encrypted value into X
		LDW X, ACC
		
		# Decrypt X with Base64
		DE64 Y, X
		
		# Load initial value from Mem[0] into X
		XOR ACC, ACC	# ACC := 0
		LDW X, ACC
		
		# Check if Decrypted value == Initial value
		SUB X, Y
		BRZ EQUAL2	# if equal: continue
STOP2:	BRA STOP2	# else:	stop here

		# Store 0xFFFF at Mem[3] to show program ran successfully
EQUAL2:	ORI X, 65535	# X := 0xFFFF
		ADDI ACC, 3
		STW X, ACC
END:	BRA END		# stop here