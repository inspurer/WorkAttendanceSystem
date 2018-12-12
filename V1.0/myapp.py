import wx
import os
from importlib import reload
import webbrowser
import face_img_register
import face_recognize_punchcard
import sys
main ="icon/main.png"
file_path = os.getcwd()+r'\data\logcat.csv'
class   Mainui(wx.Frame):
    def __init__(self,superion):
        wx.Frame.__init__(self,parent=superion,title="员工考勤系统",size=(800,590))
        self.SetBackgroundColour('white')
        self.Center()

        self.frame = ''
        self.RegisterButton = wx.Button(parent=self, pos=(50, 120), size=(80, 50), label='人脸录入')

        self.PunchcardButton = wx.Button(parent=self, pos=(50, 220), size=(80, 50), label='刷脸签到')

        self.LogcatButton = wx.Button(parent=self, pos=(50, 320), size=(80, 50), label='日志查看')

        self.InstructButton =  wx.Button(parent=self,pos=(210,460),size=(80,50),label='操作说明')

        self.ForkButton =  wx.Button(parent=self,pos=(385,460),size=(80,50),label='Frok me')

        self.AboutButton =  wx.Button(parent=self,pos=(560,460),size=(80,50),label='小组成员')

        self.Bind(wx.EVT_BUTTON,self.OnRegisterButtonClicked,self.RegisterButton)
        self.Bind(wx.EVT_BUTTON,self.OnPunchCardButtonClicked,self.PunchcardButton)
        self.Bind(wx.EVT_BUTTON,self.OnLogcatButtonClicked,self.LogcatButton)
        self.Bind(wx.EVT_BUTTON,self.OnInstructButtonClicked,self.InstructButton)
        self.Bind(wx.EVT_BUTTON,self.OnForkButtonClicked,self.ForkButton)
        self.Bind(wx.EVT_BUTTON,self.OnAboutButtonClicked,self.AboutButton)

        # 封面图片
        self.image_cover = wx.Image(main, wx.BITMAP_TYPE_ANY).Scale(520, 360)
        # 显示图片
        self.bmp = wx.StaticBitmap(parent=self, pos=(180,80), bitmap=wx.Bitmap(self.image_cover))

    def OnRegisterButtonClicked(self,event):
        reload(face_img_register)
        #del sys.modules['face_img_register']
        #import face_img_register
        #runpy.run_path("face_img_register.py")
        #frame = face_img_register.RegisterUi(None)
        app.frame = face_img_register.RegisterUi(None)
        app.frame.Show()

    def OnPunchCardButtonClicked(self,event):
        #del sys.modules['face_recognize_punchcard']
        reload(face_recognize_punchcard)
        #import face_recognize_punchcard
        app.frame = face_recognize_punchcard.PunchcardUi(None)
        app.frame.Show()

    def OnLogcatButtonClicked(self,event):
        if os.path.exists(file_path):
            #调用系统默认程序打开文件
            os.startfile(file_path)
        else:
            wx.MessageBox(message="要先运行过一次刷脸签到系统，才有日志", caption="警告")
        pass
    def OnForkButtonClicked(self,event):
        webbrowser.open("https://github.com/inspurer//WorkAttendanceSystem",new=1,autoraise=True)

    def OnInstructButtonClicked(self,event):
        wx.MessageBox(message="先占个位",caption="操作说明")
        pass

    def OnAboutButtonClicked(self,event):
        wx.MessageBox(message="技术支持:肖涛,刘佳璇      专业班级:通信1602班"+
                              "\n联系qq:2391527690       所在单位:中南大学", caption="关于我们")

class MainApp(wx.App):
    def OnInit(self):
        self.frame = Mainui(None)
        self.frame.Show()
        return True

app = MainApp()
app.MainLoop()