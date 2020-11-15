from PIL import Image
import glob
from moviepy.editor import *
from moviepy.video.tools.credits import credits1

plt_path = '.\\result\\pic\\plt_x.png'  # 读路径
pie_path = '.\\result\\pic\\pie_x.jpg'
whu_path = '.\\result\\video\\whu'
txt_path = '.\\result\\text.txt'
title_path = '.\\title.png'

clips1 = []
clips2 = []
ending = []
ary_pie = []
ary_plt = []

pie_number = len(glob.glob(pathname='.\\result\\pic\\*.jpg'))


def pic2slides():
    for i in range(pie_number - 1):
        img1 = Image.open(pie_path.replace('x', str(i)))
        img2 = Image.open(plt_path.replace('x', str(i)))
        img1.paste(img2, (0, img1.height - 400))
        img1.save(pie_path.replace('x', str(i)))
        print(i)
        ary_pie.append(pie_path.replace('x', str(i)))  # ary for gif
        clips1.append(ImageClip(pie_path.replace('x', str(i))).set_duration(0.8))

    video1 = concatenate(clips1, method='compose')

    gif = ImageSequenceClip(ary_pie, fps=3)  # 做gif
    gif.write_gif(".\\result\\video\\slides.gif")

    PLT_clip = ImageClip(plt_path).set_duration(8)
    title = ImageClip(title_path).set_duration(3)

    q_length = float(video1.duration)
    print(q_length)
    video = CompositeVideoClip([
        title.resize((2000, 1200)),
        video1.set_start(3),
        PLT_clip.set_start(q_length + 3.0).crossfadein(2)
    ])

    video.write_videofile(".\\result\\video\\slides.mp4", fps=24)


def background():
    end = ImageClip(".\\whu.png").set_duration(30)
    end.write_videofile(whu_path + '.mp4', fps=24)


def subtitle():
    ending_clip = VideoFileClip(whu_path + '.mp4', audio=False)

    credits = credits1('.\\result\\text.txt', 3 * ending_clip.w / 4, stroke_color='pink',
                       stroke_width=3, )
    scrolling_credits = credits.set_pos(lambda t: ('center', -30 * t))

    tail = CompositeVideoClip([ending_clip,
                               scrolling_credits,
                               ], duration=30)

    tail.write_videofile(whu_path + '1.mp4')


if __name__ == '__main__':
    # pic2slides()
    # quit()
    background()
    # quit()
    subtitle()
    # quit()
    start_clip = VideoFileClip('.\\result\\video\\slides.mp4', audio=False)
    length = float(start_clip.duration)

    end_clip = (VideoFileClip(whu_path + '1.mp4', audio=False))
    final_video = CompositeVideoClip([
        start_clip,
        end_clip.resize((2000, 1200)).set_start(length),
    ], duration=length + 30)

    A_clip = AudioFileClip(".\\bgm.mp3")
    Audio = A_clip.subclip(0, length + 30)
    final_clip = final_video.set_audio(Audio)  # 加音频
    final_clip.write_videofile(".\\result\\video\\final.mp4", fps=24)
