import os
import re
from binascii import b2a_hex

from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTFigure, LTTextBox, LTTextLine, LTImage
#from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
#from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser,PDFDocument,PDFPage

#view image type
def determine_image_type (stream_first_4_bytes):
    """Find out the image file type based on the magic number comparison of the first 4 (or 2) bytes"""
    file_type = None
    bytes_as_hex = b2a_hex(stream_first_4_bytes).decode()
    if bytes_as_hex.startswith('ffd8'):
          file_type = '.jpeg'
    elif bytes_as_hex == '89504e47':
          file_type = '.png'
    elif bytes_as_hex == '47494638':
          file_type = '.gif'
    elif bytes_as_hex.startswith('424d'):
          file_type = '.bmp'
    return file_type

def save_image(lt_image,pdfDir,imgcount):
 """Try to save the image data from this LTImage object, and return the file name, if successful"""
 result=None
 if lt_image.stream:
   file_stream=lt_image.stream.get_rawdata()
   file_ext=determine_image_type(file_stream[0:4])
   if file_ext:
      # init filename
      # file_name='img_'+ lt_image.name + file_ext
      file_name=f"img_{imgcount}"+file_ext
      #写入到文件
      if write_file(str(pdfDir), file_name, lt_image.stream.get_rawdata()):
        result = file_name
 return result

def write_file(folder, filename, filedata, flags='wb'):
 """Write the file data to the folder and filename combination
 ( flags: 'w' for write text, 'wb' for write binary, use 'a' instead of 'w' for append )"""
 result=False
 if os.path.isdir(folder):
    try:
        file_obj=open(os.path.join(folder, filename), flags)
        file_obj.write(filedata)
        file_obj.close()
        result=True
    except IOError:
        pass
 return result

#convert pdf file to txt
def pdf2txt(path):
    fpName = ''
    fp = open(path, 'rb')
    #获取pdf文件原来文件名 不含扩展名 作为 图片文件夹的文件夹名
    fpName = os.path.basename(fp.name).rstrip(".pdf")
    #要判断是否已创建同名文件夹，不然会出错，try except Exception as e: finally:
    if os.path.isdir(fpName)!=True:
       pdfDir=os.mkdir(fpName)
    #初始化输出的txt变量
    txt = ''
    imgcount=0
    parser = PDFParser(fp)
    doc = PDFDocument(parser)
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    #处理文档每一页.
    for page in doc.get_pages():
    #for page in PDFPage.create_pages(doc):
        interpreter.process_page(page)
        layout = device.get_result()
        for lt_obj in layout:
            imgcount+=1
            if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
                #combile text_content
                txt+=lt_obj.get_text()
                # find images in pdf file 's layout
            if isinstance(lt_obj, LTImage):
                save_image(lt_obj,fpName,imgcount)
                #pass
            if isinstance(lt_obj, LTFigure):
                #image=Image.frombytes('RGB', (200,500),lt_obj.stream.get_rawdata(), 'raw')
                #with open(lt_obj.name+'.jpeg', 'wb') as fp:
                #    image.save(fp)
                # find images in pdf file 's layout
                for lt_obj in lt_obj:
                    if isinstance(lt_obj, LTImage):
                        save_image(lt_obj,fpName,imgcount)

    return(txt)

pdf_res =pdf2txt("C:\\ccnp.pdf")


pdf_res =re.sub("inline","",pdf_res)


matches =re.finditer(r"(?sm)^QUESTION ([0-9]+)(.*?|Select and Place:.*?)(^A.\B.*?)(Answer: [A-Z]+|(?<!Answer):\B|\Z)",pdf_res, re.MULTILINE)
#print(pattern.search(pdf_res))
for matchNum, match in enumerate(matches, start=1):
    #print(match.group())
    for groupNum in range(0, len(match.groups())):
        groupNum=groupNum+1
        print(match.group(groupNum))
    print("*"*20)
