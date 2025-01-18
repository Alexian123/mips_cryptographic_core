# START: ACC=0, X=0, Y=0, data memory is empty

	ADDI X, 1		# X val to store
	STW X, ACC		# store X at Mem[0]

	ADDI Y, 2		# Y val to store
	ADDI ACC, 2		# ACC=2
	STW Y, ACC		# store Y at Mem[2]

	SUB X, Y		# X = X - Y, set FLAGS
	BRN L1			# if X < Y goto L1

	XOR ACC, ACC	# clear ACC
	ADDI ACC, 4		# ACC=4
	STW Y, ACC		# store Y at Mem[4]
	BRA L2			# goto L2

L1:	XOR ACC, ACC	# clear ACC
	LDW X, ACC		# load Mem[0] in X (restore old)
	ADDI ACC, 4		# ACC=4
	STW X, ACC		# store X at Mem[4]
	
L2:	BRA L2			# goto L2 (infinite loop)