from PIL import Image, ImageDraw, ImageFont
import os, sys
import shutil

symbols = list("$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/|()1{}[]?-_+~<>i!lI;:,\"^`'. ")


def ascii_art_convert(src_dir, dest_dir):
    print('开始生成...')
    picts_list = sorted(os.listdir(src_dir))
    len_picts = len(picts_list)

    i = 0

    for picture in picts_list:
        (pixels, x_size, y_size) = load_picture(os.path.join(src_dir, picture))

        #生成字符画图片
        create_ascii_picture(pixels, symbols, os.path.join(dest_dir, picture), x_size, y_size)

        print('正在生成中... {0}/{1}'.format(i, len_picts))
        i += 1

def create_thumbnail(src_dir, dst_dir):
    picts_list = sorted(os.listdir(src_dir))

    for picture in picts_list:
        base_name = os.path.basename(picture)
        img = Image.open(os.path.join(src_dir, picture))
        size = 200, 200
        img.thumbnail(size, Image.ANTIALIAS)
        img.save(os.path.join(dst_dir, base_name))


def load_picture(filename):

    # Gray = R*0.299 + G*0.587 + B*0.114
    img = Image.open(filename).convert('L')
    (x, y) = img.size

    pixels = list(img.getdata())
    img.close()
    return (pixels, x, y)


def create_ascii_picture(pixels, symbols, dest_name, x_size, y_size):
    scale = 4    # 长宽扩大倍数
    border = 1  # 边框宽度

    interval_pixel = 2     #原图片间隔多少个像素点来填充

    img = Image.new('L',
                    (x_size*scale + 2*border,
                     y_size*scale + 2*border),
                    255)
    fnt = ImageFont.truetype('DejaVuSansMono.ttf', int(scale*3))
    #fnt = ImageFont.load_default().font
    t = ImageDraw.Draw(img)

    x = border
    y = border
    for j in range(0, y_size, interval_pixel):
        for i in range(0, x_size, interval_pixel):
            t.text( (x, y),
                    symbols[int(pixels[j*x_size + i]/256 * len(symbols))],
                    font=fnt,
                    fill=0
                    )
            x += scale * interval_pixel
        x = border
        y += scale * interval_pixel

    img.save(dest_name, "JPEG")


def start_convert(src_file):

    if not os.path.exists('temp_pic'):
        os.mkdir('temp_pic')

    if not os.path.exists('temp_thum'):
        os.mkdir('temp_thum')

    if not os.path.exists('temp_ascii'):
        os.mkdir('temp_ascii')


    #分离音频
    slice_audio_cmd = 'ffmpeg -i {0} -vn temp.mp3'.format(src_file)
    os.system(slice_audio_cmd)


    #切割成图片
    slice_pic_cmd = 'ffmpeg -i {0} -r 24 temp_pic/%06d.jpeg'.format(src_file)
    os.system(slice_pic_cmd)

    #生成缩略图
    create_thumbnail('temp_pic', 'temp_thum')

    #生成字符画
    ascii_art_convert('temp_thum', 'temp_ascii')


    #合成字符视频
    dst_name = os.path.join(os.path.dirname(src_file), 'ascii_' + os.path.basename(src_file))
    merge_ascii_video_cmd = 'ffmpeg -threads 2 -start_number 000001 -r 24 -i {0}/%06d.jpeg -i temp.mp3 -vcodec mpeg4 {1}'.format('temp_ascii', dst_name)
    os.system(merge_ascii_video_cmd)

    print('生成完成！')


    if os.path.exists('temp_pic'):
        shutil.rmtree('temp_pic')

    if os.path.exists('temp_thum'):
        shutil.rmtree('temp_thum')

    #if os.path.exists('temp_ascii'):
        #shutil.rmtree('temp_ascii')

    if os.path.exists('temp.mp3'):
        os.remove('temp.mp3')


if __name__ == '__main__':
    src_file = sys.argv[1]
    start_convert(src_file)