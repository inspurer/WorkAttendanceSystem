import numpy as np  # 数据处理的库 Numpy
import cv2          # 图像处理的库 OpenCv
import os
import shutil
import _thread
import wx
import csv
from importlib import reload
from skimage import io as iio
import face_recognize_punchcard
import sys
# 创建 cv2 摄像头对象
#    C++: VideoCapture::VideoCapture(int device);

#API:http://www.opencv.org.cn/opencvdoc/2.3.2/html/modules/highgui/doc/reading_and_writing_images_and_video.html#videocapture

# 保存
path_make_dir = "data/face_img_database/"

path_feature_all = "data/feature_all.csv"

info = 'icon/info.png'



#register ui
class   RegisterUi(wx.Frame):
    def __init__(self,superion):
        wx.Frame.__init__(self,parent=superion,title="人脸录入",size=(800,590),style=wx.DEFAULT_FRAME_STYLE|wx.STAY_ON_TOP)
        self.SetBackgroundColour('white')
        self.Center()

        self.NewButton =  wx.Button(parent=self,pos=(50,120),size=(80,50),label='新建录入')

        self.ShortCutButton = wx.Button(parent=self,pos=(50,220),size=(80,50),label='截图保存')

        self.SaveButton =  wx.Button(parent=self,pos=(50,320),size=(80,50),label='完成录入')

        # 封面图片
        self.image_info = wx.Image(info, wx.BITMAP_TYPE_ANY).Scale(600, 480)
        # 显示图片
        self.bmp = wx.StaticBitmap(parent=self, pos=(180,20), bitmap=wx.Bitmap(self.image_info))

        self.Bind(wx.EVT_BUTTON,self.OnShortCutButtonClicked,self.ShortCutButton)
        self.Bind(wx.EVT_BUTTON,self.OnNewButtonClicked,self.NewButton)
        self.ShortCutButton.Enable(enable=False)
        self.SaveButton.Enable(False)

        self.Bind(wx.EVT_BUTTON,self.OnSaveButtonClicked,self.SaveButton)

        self.sc_number = 0
        self.register_flag = 0
        self.name = ""

    def OnNewButtonClicked(self, event):
        while self.name == '':
            self.name = wx.GetTextFromUser(message="请先输入录入者的姓名,用于创建姓名文件夹", caption="温馨提示",
                                      default_value="", parent=None)

            # 监测是否重名
            for exsit_name in (os.listdir(path_make_dir)):
                if self.name == exsit_name:
                    wx.MessageBox(message="姓名已存在，请重新输入", caption="警告")
                    self.name = ''
                    break
        os.makedirs(path_make_dir+self.name)
        print("新建的人脸文件夹: ", path_make_dir+self.name)
        self.NewButton.Enable(enable=False)
        self.ShortCutButton.Enable(enable=True)
        """使用多线程，子线程运行后台的程序，主线程更新前台的UI，这样不会互相影响"""
        # 创建子线程，按钮调用这个方法，
        _thread.start_new_thread(self._open_cap, (event,))

    def OnShortCutButtonClicked(self,event):
        self.SaveButton.Enable(True)
        if len(self.rects) !=0:
            # 计算矩形框大小,保证同步
            height = self.rects[0].bottom() - self.rects[0].top()
            width = self.rects[0].right() - self.rects[0].left()
            self.sc_number += 1
            im_blank = np.zeros((height, width, 3), np.uint8)
            for ii in range(height):
                for jj in range(width):
                    im_blank[ii][jj] = self.im_rd[self.rects[0].top() + ii][self.rects[0].left() + jj]
            # cv2.imwrite(path_make_dir+self.name + "/img_face_" + str(self.sc_number) + ".jpg", im_blank)
            # cap = cv2.VideoCapture("***.mp4")
            # cap.set(cv2.CAP_PROP_POS_FRAMES, 2)
            # ret, frame = cap.read()
            # cv2.imwrite("我//h.jpg", frame)  # 该方法不成功

            #解决python3下使用cv2.imwrite存储带有中文路径图片
            cv2.imencode('.jpg', im_blank)[1].tofile(path_make_dir+self.name + "/img_face_" + str(self.sc_number) + ".jpg") #正确方法
            print("写入本地：", str(path_make_dir+self.name) + "/img_face_" + str(self.sc_number) + ".jpg")

        else:
            print("未检测到人脸，识别无效，未写入本地")

    def OnSaveButtonClicked(self,event):


        self.bmp.SetBitmap(wx.Bitmap(self.image_info))
        self.NewButton.Enable(True)
        self.SaveButton.Enable(False)
        self.ShortCutButton.Enable(False)


        # 释放摄像头
        self.cap.release()
        # 删除建立的窗口
        #cv2.destroyAllWindows()

        if self.register_flag == 1:
            if os.path.exists(path_make_dir+self.name):
                shutil.rmtree(path_make_dir+self.name)
                print("重复录入，已删除姓名文件夹", path_make_dir+self.name)

        if self.sc_number == 0 and len(self.name)>0:
            if os.path.exists(path_make_dir+self.name):
                shutil.rmtree(path_make_dir+self.name)
                print("您未保存截图，已删除姓名文件夹", path_make_dir+self.name)
        if self.register_flag==0 and self.sc_number!=0:
            pics = os.listdir(path_make_dir+self.name)
            feature_list = []
            feature_average = []
            for i in range(len(pics)):
                pic_path = path_make_dir+self.name + "/" + pics[i]
                print("正在读的人脸图像：", pic_path)
                img = iio.imread(pic_path)
                img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                dets = face_recognize_punchcard.detector(img_gray, 1)
                if len(dets) != 0:
                    shape = face_recognize_punchcard.predictor(img_gray, dets[0])
                    face_descriptor = face_recognize_punchcard.facerec.compute_face_descriptor(img_gray, shape)
                    feature_list.append(face_descriptor)
                else:
                    face_descriptor = 0
                    print("未在照片中识别到人脸")
            if len(feature_list)>0:
                for j in range(128):
                    feature_average.append(0)
                    for i in range(len(feature_list)):
                        feature_average[j] += feature_list[i][j]
                    feature_average[j] = (feature_average[j])/len(feature_list)
                feature_average.append(self.name)

                with open(path_feature_all, "a+", newline="") as csvfile:
                    writer = csv.writer(csvfile)
                    print('写入一条特征人脸入库',feature_average)
                    writer.writerow(feature_average)

        self.name = ""
        self.register_flag = 0
        self.sc_number = 0;




    def _open_cap(self,event):
        # reload(facerec)
        reload(face_recognize_punchcard)
        # reload(predictor)
        # reload(detector)
        # reload(return_euclidean_distance())

        self.cap = cv2.VideoCapture(0)



        # cap.set(propId, value)
        # 设置视频参数，propId 设置的视频参数，value 设置的参数值
        self.cap.set(3, 480)
        #self.cap.set(cv2.CAP_PROP_FPS,5)
        while self.cap.isOpened():
            # cap.read()
            # 返回两个值：
            #    一个布尔值 true/false，用来判断读取视频是否成功/是否到视频末尾
            #    图像对象，图像的三维矩阵q
            flag, self.im_rd = self.cap.read()
            # 人脸数 rects
            self.rects = face_recognize_punchcard.detector(self.im_rd, 1)

            cv2.waitKey(1)  # 必不可少
            # 待会要写的字体
            font = cv2.FONT_HERSHEY_SIMPLEX

            if len(self.rects) != 0:
                # 检测到人脸
                # 矩形框#d是人脸

                # 查重
                features_cap = face_recognize_punchcard.facerec.compute_face_descriptor(self.im_rd, face_recognize_punchcard.predictor(self.im_rd, self.rects[0]))
                for i in range(len(face_recognize_punchcard.features_known_arr)):
                    # 将某张人脸与存储的所有人脸数据进行比对
                    compare = face_recognize_punchcard.return_euclidean_distance(features_cap, face_recognize_punchcard.features_known_arr[i][0:-1])
                    if compare == "same":  # 找到了相似脸
                        face_name = face_recognize_punchcard.features_known_arr[i][-1]
                        print(face_name)
                        wx.MessageBox(message=face_name + "，您已录过人脸，请检查是否签过到", caption="警告")
                        self.NewButton.Enable(False)
                        self.ShortCutButton.Enable(False)
                        self.SaveButton.Enable(True)
                        self.register_flag = 1

                for k, d in enumerate(self.rects):
                    # 根据人脸大小生成空的图像
                    # 最后一个参数是线宽
                    cv2.rectangle(self.im_rd, tuple([d.left(), d.top()]), tuple([d.right(), d.bottom()]), (255, 0, 0), 2)

                # 显示人脸数
            cv2.putText(self.im_rd, "Faces: " + str(len(self.rects)), (50, 80), font, 0.8, (255, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(self.im_rd, "Warning: please shortcut having rectangle", (50, 140), font, 0.8, (0, 0, 255), 1,
                        cv2.LINE_AA)

            # print(im_rd.shape)
            height, width = self.im_rd.shape[:2]
            image1 = cv2.cvtColor(self.im_rd, cv2.COLOR_BGR2RGB)
            pic = wx.Bitmap.FromBuffer(width, height, image1)
            # 显示图片在panel上
            self.bmp.SetBitmap(pic)

            #直接在sbclicked里设置self.bmp.SetBitmap(wx.Bitmap(self.image_cover))，子线程还在运行
            if self.NewButton.IsEnabled()==True and self.ShortCutButton.IsEnabled()==False and self.SaveButton.IsEnabled()==False:
                self.bmp.SetBitmap(wx.Bitmap(self.image_info))
                _thread.exit()



# app = wx.App()
#
# frame = RegisterUi(None)
# frame.Show()
# app.MainLoop()

#cap.isOpened（） 返回 true/false 检查初始化是否成功
