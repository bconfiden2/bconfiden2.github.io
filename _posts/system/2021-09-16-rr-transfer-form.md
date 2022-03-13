---
layout: post
title: "Register-Register Transfer Form"
tags: system
---

### Fetch and Decoding (Default)
```
MAR = PC
memoryRead()
IR = MDR
```

### LDA (1__)
```
MAR = ADDR
memoryRead()
A = MDR
```

### STA (2__)
```
MAR = ADDR
MDR = A
memoryWrite()
```

### ADDA (3__)
```
MAR = ADDR
memoryRead()
A = alu('+', A, MDR)
```

## SUBA (4__)
```
MAR = ADDR
memoryRead()
A = alu('-', A, MDR)
```

## SKZ (511)
```
#$ programStatus("Z")
#$= true
PC = PC + 1
```

### SKP (512)
```
#$ (not programStatus("S")) and (not programStatus("Z"))
#$= true
PC = PC + 1
```

### SKN (513)
```
#$ (programStatus("S")) and (not programStatus("Z"))
#$= true
PC = PC + 1
```

### JMP (6__)
```
#! handcounter false
PC = ADDR
```

### SWAPAX (505)
```
swapReg(A, X)
```

### LDA #IMMED (52_)
```
A = IMMED
```

### ADDA #IMMED (53_)
```
A = alu('+', A, IMMED)
```

### SUBA #IMMED (54_)
```
A = alu('-', A, IMMED)
```

### ADDA *ADDR (7__)
```
MAR = ADDR
memoryRead()
MAR = MDR
memoryRead()
A = alu('+', A, MDR)
```

### ADDA @ADDR (8__)
```
MAR = ADDR + X
memoryRead()
A = alu('+', A, MDR)
```