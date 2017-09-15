import pytesseract
from PIL import Image
import io
import sys
#sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='gb18030')
import sys  
reload(sys)  
sys.setdefaultencoding('utf8') 
num = "test.jpg"
zh = "zh_baidu.png"

image = Image.open('zh.PNG')
code = pytesseract.image_to_string(image)


f=open("orc.out","w")
f.write(code)
type = sys.getfilesystemencoding()
print code.decode("utf-8")#.encode(type)
