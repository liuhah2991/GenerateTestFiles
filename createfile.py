import argparse
import os
import random
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

# 生成指定的大小的文件
def generate_file(file, size):
    bigFile=open(file,'w')
    bigFile.seek(size-1)
    bigFile.write(' ')
    bigFile.close()

# 填充指定文件到指定大小
def fill_file(sfile, size, ofile=None):
    sfile_size = os.stat(sfile).st_size

    if sfile_size >= size:
        print("源文件大小已超过目标大小，无法填充")
        return

    #tmpfile =  'E:\\Test\\tmpfile' + str(random.randint(1000, 9999))
    tmpfile = os.getcwd() + '\\output\\tmpfile' + str(random.randint(1000, 9999))
    generate_file(tmpfile, size - sfile_size)

    if ofile == None:
        command = "copy /b " + sfile + "+" + tmpfile + " " + sfile
    else:
        command = "copy /b " + sfile + "+" + tmpfile + " " + ofile

    os.system(command)
    os.remove(tmpfile)

# 生成指定的大小的纯文本文件
def generate_text(file, size, text=None):
    if text == None:
        with open(file, 'wb') as targetfile:
            targetfile.write(os.urandom(size))
    else:
        count = len(list(''.join([char for char in text if '\u4e00' <= char <= '\u9fff']))) # 统计汉字的字数，计算位数的时候减去
        text_size_bytes = len(text.encode('utf-8')) - count # 每个重复的文本的大小（以字节为单位）

        repetitions = size // text_size_bytes  # 需要重复的次数
        remainder = size % text_size_bytes  # 剩余的字节数
        with open(file, 'w') as targetfile:
            for _ in range(repetitions):
                targetfile.write(text)
            if remainder > 0:
                targetfile.write(text[:remainder])

# 生成指定的大小的图片
def generate_img(file, width, heigh, bgc, size=None):
    image = Image.new(mode='RGB', size=(width, heigh), color=(bgc[0], bgc[1], bgc[2]))

    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font='resources/Font/CALIFR.TTF', size=20)

    draw.text(xy=(10, 10), text= 'image_size:\n' + str(width) +'*' + str(heigh), fill=(255, 255, 255), font=font)
    image.save(file, format=None)
    if size != None:
        fill_file(file, size)

# 根据输入计算文件大小，单位转换为B
def calculate_size(size,size_type):
    if size_type == 'B':
        return size
    elif size_type == 'KB':
        return size * 1024
    elif size_type == 'MB':
        return size * 1024 * 1024
    elif size_type == 'GB':
        return size * 1024 * 1024 * 1024

# 输出该工具的用法示例
def print_usage_examples():
    # 打开文本文件
    with open('resources/usage.txt', 'r', encoding='utf-8') as file:
        for line in file:
            print(line,end='')

# 工具的参数解析
def tool_argparse():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['any', 'fill', 'text', 'img', 'usage'])
    parser.add_argument('-sf', '--source_file', type=str, dest='source_file', help='源文件,需要输入已存在文件的路径和名称')
    parser.add_argument('-tf', '--target_folder', type=str, dest='target_folder', default='.\output\\', help='目标文件夹,默认当前目录下的output目录')
    parser.add_argument('-tfn', '--target_file_name', type=str, dest='target_file_name', help='目标文件名')
    parser.add_argument('-s', '--size', type=int,dest='size', help='目标文件大小')
    parser.add_argument('-st', '--size_type', choices=['B', 'KB', 'MB', 'GB'], dest='size_type', default='B', help='大小单位,默认为B')
    parser.add_argument('-t', '--text', type=str, dest='text',help='重复的文本,默认为空，填充随机字符')
    parser.add_argument('-iw', '--image_width', default=200, type=int, dest='image_width', help='图片的宽,默认200,仅img模式下有用')
    parser.add_argument('-ih', '--image_height', default=200, type=int, dest='image_height', help='图片的高,默认200,仅img模式下有用')
    parser.add_argument('-ic', '--image_color', default=[128,128,128], nargs=3, type=int, dest='image_color', help='图片的背景颜色,默认[128,128,128],仅img模式下有用')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0')
    return parser.parse_args()

# 用户输入检查
def pre_check(args):
    #  检查项1：如果选择填充模式，则源文件必须存在,且非目录文件
    if args.mode == 'fill':
        if not os.path.exists(args.source_file):
            print("如果选择fill模式，则源文件必须存在")
            return False
        elif not os.path.isfile(args.source_file):
            print("源文件不能是一个目录文件")
            return False

    #  检查项2： 除了fill模式外，用户必须指定目标文件
    if args.mode != 'fill' and args.target_file_name is None:
        print("除了fill模式外，用户必须指定目标文件，请检查。")
        return False

    #  检查项3： 若指定了输出的目标文件，则该文件必须不存在
    if not args.target_file_name is None:
        file = args.target_folder + args.target_file_name
        if os.path.exists(file):
            print("目标文件已存在，请更换名称。")
            return False

    # 检查项4： 若指定的输出目录不存在则先创建该目录
    if not os.path.exists(args.target_folder):
        # 如果目录不存在则创建该目录
        os.makedirs(args.target_folder)

    #  检查项5： 除了img模式外，用户必须指定输出文件大小
    if args.mode != 'img' and args.size is None:
        print("除了img模式外，用户必须指定输出文件大小")
        return False

    return True

# 入口函数
if __name__ == "__main__":
    args = tool_argparse()
    if args.mode == 'usage':
        print_usage_examples()
    elif pre_check(args):
        if not args.size is None:
            file_size = calculate_size(args.size, args.size_type)
        if not args.target_file_name is None:
            target_file = args.target_folder + args.target_file_name

        if args.mode == 'any':
            generate_file(target_file, file_size)
            print("目标文件生成成功")
        elif args.mode == 'fill' and args.target_file_name is None:
            fill_file(args.source_file, file_size)
            print("源文件填充成功")
        elif args.mode == 'fill':
            fill_file(args.source_file, file_size, target_file)
            print("目标文件已生成且填充成功")
        elif args.mode == 'text':
            generate_text(target_file, file_size, args.text)
            print("目标文本文件生成成功")
        elif args.mode == 'img' and args.size is None:
            generate_img(target_file, args.image_width, args.image_height, args.image_color)
            print("目标图片文件生成成功")
        elif args.mode == 'img':
            generate_img(target_file, args.image_width, args.image_height, args.image_color, file_size)
            print("目标图片文件生成成功")
        else:
            print_usage_examples()


