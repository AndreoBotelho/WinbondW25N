import memdrive
import shutil
import os

sourcename = '/flash/bg.bmp'
destname = '/flash2/bg{}.bmp'

src = open(sourcename,'r')

samples = 1000

for i in range(samples):
    try:
        os.remove(destname.format(i))
    except:
        pass
#     dst = open(destname.format(i+600),'w')
#     shutil.copyfileobj(src,dst)
#     src.seek(0)
#     dst.close()
    
