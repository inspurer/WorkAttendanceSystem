#!Anaconda/anaconda/python
#coding: utf-8

"""
从视屏中识别人脸，并实时标出面部特征点
"""

import dlib                     # 人脸识别的库dlib
import numpy as np              # 数据处理的库numpy
import cv2                      # 图像处理的库OpenCv
import wx                       # 构造显示界面的GUI


COVER = 'camera.png'


class face_emotion(wx.Frame):

    def __init__(self,parent,title):
        wx.Frame.__init__(self,parent,title=title,size=(600,600))
        self.panel = wx.Panel(self)
        self.Center()

        # 封面图片
        self.image_cover = wx.Image(COVER, wx.BITMAP_TYPE_ANY).Scale(350,300)
        # 显示图片在panel上
        self.bmp = wx.StaticBitmap(self.panel, -1, wx.Bitmap(self.image_cover))

        start_button = wx.Button(self.panel,label='Start')
        close_button = wx.Button(self.panel,label='Close')

        self.Bind(wx.EVT_BUTTON,self.learning_face,start_button)
        self.Bind(wx.EVT_BUTTON,self.close_face,close_button)

        # 基于GridBagSizer的界面布局
        # 先实例一个对象
        self.grid_bag_sizer = wx.GridBagSizer(hgap=5,vgap=5)
        # 注意pos里面是先纵坐标后横坐标
        self.grid_bag_sizer.Add(self.bmp, pos=(0, 0), flag=wx.ALL | wx.EXPAND, span=(4, 4), border=5)
        self.grid_bag_sizer.Add(start_button, pos=(4, 1), flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, span=(1, 1), border=5)
        self.grid_bag_sizer.Add(close_button, pos=(4, 2), flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, span=(1, 1), border=5)

        self.grid_bag_sizer.AddGrowableCol(0,1)
        #grid_bag_sizer.AddGrowableCol(0,2)

        self.grid_bag_sizer.AddGrowableRow(0,1)
        #grid_bag_sizer.AddGrowableRow(0,2)

        self.panel.SetSizer(self.grid_bag_sizer)
        # 界面自动调整窗口适应内容
        self.grid_bag_sizer.Fit(self)

        """dlib的初始化调用"""
        # 使用人脸检测器get_frontal_face_detector
        self.detector = dlib.get_frontal_face_detector()
        # dlib的68点模型，使用作者训练好的特征预测器
        self.predictor = dlib.shape_predictor("model/shape_predictor_68_face_landmarks.dat")


    def _learning_face(self,event):
        #建cv2摄像头对象，这里使用电脑自带摄像头，如果接了外部摄像头，则自动切换到外部摄像头
        self.cap = cv2.VideoCapture(0)
        # 设置视频参数，propId设置的视频参数，value设置的参数值
        self.cap.set(3, 480)
        # 截图screenshoot的计数器
        self.cnt = 0

        # cap.isOpened（） 返回true/false 检查初始化是否成功
        while(self.cap.isOpened()):

            # cap.read()
            # 返回两个值：
            #    一个布尔值true/false，用来判断读取视频是否成功/是否到视频末尾
            #    图像对象，图像的三维矩阵
            flag, im_rd = self.cap.read()
            # 每帧数据延时1ms，延时为0读取的是静态帧
            self.k = cv2.waitKey(1)
            # 取灰度
            img_gray = cv2.cvtColor(im_rd, cv2.COLOR_RGB2GRAY)

            # 使用人脸检测器检测每一帧图像中的人脸。并返回人脸数rects
            faces = self.detector(img_gray, 0)

            # 待会要显示在屏幕上的字体
            font = cv2.FONT_HERSHEY_SIMPLEX

            # 如果检测到人脸
            if(len(faces)!=0):

                # enumerate方法同时返回数据对象的索引和数据，k为索引，d为faces中的对象
                for k, d in enumerate(faces):
                    # 初始化列表
                    line_brow_x = []
                    line_brow_y = []
                    # 用红色矩形框出人脸
                    cv2.rectangle(im_rd, (d.left(), d.top()), (d.right(), d.bottom()), (0, 0, 255))
                    # 计算人脸热别框边长
                    self.face_width = d.right() - d.left()

                    # 使用预测器得到68点数据的坐标
                    shape = self.predictor(im_rd, d)
                    # 圆圈显示每个特征点
                    for i in range(68):
                        cv2.circle(im_rd, (shape.part(i).x, shape.part(i).y), 2, (0, 255, 0), -1, 8)
                        #cv2.putText(im_rd, str(i), (shape.part(i).x, shape.part(i).y), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        #            (255, 255, 255))

                    # 分析任意n点的位置关系来作为表情识别的依据
                    # mouth_width = (shape.part(54).x - shape.part(48).x) / self.face_width  # 嘴巴咧开程度
                    mouth_higth = (shape.part(66).y - shape.part(62).y) / self.face_width  # 嘴巴张开程度
                    # print("嘴巴宽度与识别框宽度之比：",mouth_width_arv)
                    # print("嘴巴高度与识别框高度之比：",mouth_higth_arv)

                    # 通过两个眉毛上的10个特征点，分析挑眉程度和皱眉程度
                    brow_sum = 0  # 高度之和
                    frown_sum = 0  # 两边眉毛距离之和
                    for j in range(17, 21):
                        brow_sum += (shape.part(j).y - d.top()) + (shape.part(j + 5).y - d.top())
                        frown_sum += shape.part(j + 5).x - shape.part(j).x
                        line_brow_x.append(shape.part(j).x)
                        line_brow_y.append(shape.part(j).y)

                    # self.brow_k, self.brow_d = self.fit_slr(line_brow_x, line_brow_y)  # 计算眉毛的倾斜程度
                    tempx = np.array(line_brow_x)
                    tempy = np.array(line_brow_y)
                    z1 = np.polyfit(tempx, tempy, 1)  # 拟合成一次直线
                    self.brow_k = -round(z1[0], 3)  # 拟合出曲线的斜率和实际眉毛的倾斜方向是相反的

                    # brow_hight = (brow_sum / 10) / self.face_width  # 眉毛高度占比
                    # brow_width = (frown_sum / 5) / self.face_width  # 眉毛距离占比
                    # print("眉毛高度与识别框高度之比：",round(brow_arv/self.face_width,3))
                    # print("眉毛间距与识别框高度之比：",round(frown_arv/self.face_width,3))

                    # 眼睛睁开程度
                    eye_sum = (shape.part(41).y - shape.part(37).y + shape.part(40).y - shape.part(38).y +
                               shape.part(47).y - shape.part(43).y + shape.part(46).y - shape.part(44).y)
                    eye_hight = (eye_sum / 4) / self.face_width
                    # print("眼睛睁开距离与识别框高度之比：",round(eye_open/self.face_width,3))

                    # 分情况讨论
                    # 张嘴，可能是开心或者惊讶
                    if round(mouth_higth >= 0.08):
                        if eye_hight >= 0.056:
                            cv2.putText(im_rd, "amazing", (d.left(), d.bottom() + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                                        (0, 0, 255), 2, 4)
                        else:
                            cv2.putText(im_rd, "happy", (d.left(), d.bottom() + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                                        (0, 0, 255), 2, 4)

                    # 没有张嘴，可能是正常和生气
                    else:
                        if self.brow_k <= 0.07:
                            cv2.putText(im_rd, "angry", (d.left(), d.bottom() + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                                        (0, 0, 255), 2, 4)
                        else:
                            cv2.putText(im_rd, "nature", (d.left(), d.bottom() + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                                        (0, 0, 255), 2, 4)

                # 标出人脸数
                cv2.putText(im_rd, "Faces: "+str(len(faces)), (20,50), font, 1, (0, 0, 255), 1, cv2.LINE_AA)
            else:
                # 没有检测到人脸
                cv2.putText(im_rd, "No Face", (20, 50), font, 1, (0, 0, 255), 1, cv2.LINE_AA)

            # 添加说明
            cv2.putText(im_rd, "S: screenshot", (20, 400), font, 0.8, (0, 0, 255), 1, cv2.LINE_AA)
            cv2.putText(im_rd, "Q: quit", (20, 450), font, 0.8, (0, 0, 255), 1, cv2.LINE_AA)

            # 按下s键截图保存
            if (self.k == ord('s')):
                self.cnt += 1
                cv2.imwrite("screenshoot"+str(self.cnt)+".jpg", im_rd)

            # 按下q键退出
            if(self.k == ord('q')):
                break

            # 使用opencv会在新的窗口中显示
            # cv2.imshow("camera", im_rd)

            # 现将opencv截取的一帧图片BGR转换为RGB，然后将图片显示在UI的框架中
            # 行数、列数、色彩通道数
            height,width = im_rd.shape[:2]
            #print(im_rd.shape)
            image1 = cv2.cvtColor(im_rd, cv2.COLOR_BGR2RGB)
            pic = wx.Bitmap.FromBuffer(width,height,image1)
            # 显示图片在panel上
            self.bmp.SetBitmap(pic)
            self.grid_bag_sizer.Fit(self)

        # 释放摄像头
        self.cap.release()
        # 删除建立的窗口
        # cv2.destroyAllWindows()


    def learning_face(self,event):
        """使用多线程，子线程运行后台的程序，主线程更新前台的UI，这样不会互相影响"""
        import _thread
        # 创建子线程，按钮调用这个方法，
        _thread.start_new_thread(self._learning_face, (event,))


    def close_face(self,event):
        """关闭摄像头，显示封面页"""
        self.cap.release()
        self.bmp.SetBitmap(wx.Bitmap(self.image_cover))
        self.grid_bag_sizer.Fit(self)


class main_app(wx.App):
    # OnInit 方法在主事件循环开始前被wxPython系统调用，是wxpython独有的
    def OnInit(self):
        self.frame = face_emotion(parent=None,title="Face")
        self.frame.Show(True)
        return True

if __name__ == "__main__":
    app = main_app()
    app.MainLoop()

