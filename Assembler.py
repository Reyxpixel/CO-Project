import sys

def sext(num,length):
    num=int(num)
    if num>=0:
        result=format(num,f'0{length}b')
    else:
        result=format(num&((1<<length)-1),f'0{length}b')
    return result

def main():
    rgs={
        'zero': '00000','ra': '00001','sp': '00010','gp': '00011',
        'tp': '00100','t0': '00101','t1': '00110','t2': '00111',
        's0': '01000','s1': '01001','a0': '01010','a1': '01011',
        'a2': '01100','a3': '01101','a4': '01110','a5': '01111',
        'a6': '10000','a7': '10001','s2': '10010','s3': '10011',
        's4': '10100','s5': '10101','s6': '10110','s7': '10111',
        's8': '11000','s9': '11001','s10': '11010','s11': '11011',
        't3': '11100','t4': '11101','t5': '11110','t6': '11111'
    }
    ops={
        'add': ['000','0000000','0110011','R'],
        'sub': ['000','0100000','0110011','R'],
        'slt': ['010','0000000','0110011','R'],
        'srl': ['101','0000000','0110011','R'],
        'or':  ['110','0000000','0110011','R'],
        'and': ['111','0000000','0110011','R'],
        'lw':  ['010','0000011','I'],
        'addi':['000','0010011','I'],
        'jalr':['000','1100111','I'],
        'sw':  ['010','0100011','S'],
        'beq': ['000','1100011','B'],
        'bne': ['001','1100011','B'],
        'jal': ['1101111','J'],
        'rst':['00000000000000000000000000000000','bonus'],
        'halt':['11111111111111111111111111111111','bonus']
    }
    
    a=sys.argv[1]
    b=sys.argv[2]
    f1=open(a,'r')
    f2=open(b,'w')
    labels={}     
    num=0
    for l in f1:
        l=l.strip()
        if l=="":
            continue
        if ':' in l:  
            label=l.split(':',1)[0].strip()  
            labels[label]=num  
            l=l.split(':',1)[1].strip()
        if l:
            num+=1  
    f1.seek(0) 
    num=0
    results=[]
    error=False
    for l in f1:
        num+=1
        l=l.strip()
        if l=="":
            continue
        if ':' in l:
            l=l.split(':',1)[1].strip()
        l=l.replace('(',' ')
        l=l.replace(')',' ')
        p=l.replace(',',' ').split()
        if len(p)==0:
            continue
        op=p[0]
        if op not in ops:
            print(f"Error: Wrong operation found at line {num}!")
            error=True
            return
        type=ops[op][-1]
        
        if type=='R':
            f3,f7,opcd,type=ops[op]
            if len(p)!=4:
                print(f"Error: Wrong number of arguments found at line {num}!")
                error=True
                return
            x,y,z=p[1],p[2],p[3]
            if x not in rgs or y not in rgs or z not in rgs:
                print(f"Error: Bad register found at line {num}!")
                error=True
                return
            r1,r2,r3=rgs[x],rgs[y],rgs[z]
            bincode=f7+r3+r2+f3+r1+opcd

        elif type=="I":
            f3,opcd,type=ops[op]
            if op=="lw":
                x,z,y=p[1],p[2],p[3]
            else:
                x,y,z=p[1],p[2],p[3]
            if x not in rgs or y not in rgs:
                print(f"Error: Bad register found {num}!")
                error=True
                return
            if len(p)!=4:
                print(f"Error: Wrong number of arguments found {num}!")
                error=True
                return
            r1,r2=rgs[x],rgs[y]
            imm=sext(z,12)
            bincode=imm+r2+f3+r1+opcd

        elif type=="S":
            f3,opcd,type=ops[op]
            x,z,y=p[1],p[2],p[3]
            if x not in rgs or y not in rgs:
                print(f"Error: Bad register found at line {num}!")
                error=True
                return
            if len(p)!=4:
                print(f"Error: Wrong number of arguments found at line {num}!")
                error=True
                return
            r2,r1=rgs[x],rgs[y]
            imm=sext(z,12)
            bincode=imm[:7]+r2+r1+f3+imm[7:]+opcd

        elif type=="B":
            f3,opcd,type=ops[op]
            x,y,z=p[1],p[2],p[3]
            if x not in rgs or y not in rgs:
                print(f"Error: Bad register found at line {num}!")
                error=True
                return
            if len(p)!=4:
                print(f"Error: Wrong number of arguments found at line {num}!")
                error=True
                return
            
            if z in labels:
                offset=4*(labels[z] - num +1)
            else:
                offset=int(z)
            
            r1,r2=rgs[x],rgs[y]
            imm=sext(offset, 13)
            bincode=imm[0]+imm[2:8]+r2+r1+f3+imm[8:12]+imm[1]+opcd
            
        elif type=="J":
            opcd,type=ops[op]
            x,z=p[1],p[2]
            if x not in rgs:
                print(f"Error: Bad register found at line {num}!")
                error=True
                return
            if len(p)!=3:
                print(f"Error: Wrong number of arguments found at line {num}!")
                error=True
                return
            r1=rgs[x]
            
            if z in labels:
                offset=4*(labels[z] - num +1)
            else:
                offset=int(z)
                
            imm=sext(offset,21)
            bincode=imm[0]+imm[10:20]+imm[9]+imm[1:9]+r1+opcd

        elif type=="bonus":
            bincode=ops[op][0]

        if len(bincode)!=32:
            print(f"Error: 32 bits not made at line {num}")
            error=True
            return
            
        results.append(bincode)
        
    if not error:
        for i in results:
            f2.write(i+'\n')
    f1.close()
    f2.close()
main()
