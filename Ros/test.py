import math
obj = -0.2
ansdiff = 0
for i in range(-10,11):
    z = i/10.0
    if(abs(z-obj)>1):
        diff = 2-abs(z-obj)
        print(z," ",obj," ",2-abs(z-obj))
    else:
        print(z," ",obj," ",abs(z-obj))
        diff = abs(z-obj)
    if(ansdiff-diff)>0:
        print(-1)
    else:
        print(1)
    ansdiff= diff
    
    
