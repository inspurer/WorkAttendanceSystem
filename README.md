# WorkAttendanceSystem    
一个基于opencv人脸识别的员工考勤系统    

##工程简介  
写于2018/09/，python课设期间；

##项目结构    
mainui.py是主界面，调用face_img_register.py和face_recognize_punchcard.py   
其中face_img_register.py是录入人脸信息，face_recognize_punchcard.py是刷脸考勤
face_feature_storage.py属于鸡肋文件，没什么用，舍不得删，毕竟有点参考价值。   
face_recognize_punchcard_lib.py和face_recognize_punchcard.py本质上差不多，
但是前者是给face_img_register.py专有的依赖。防止录入两个同样的人脸建不同数据库的风险。


##运行效果   
1.主界面
![](https://i.imgur.com/fNw0Mgj.png)![](https://i.imgur.com/Gg3hmBs.png)![](https://i.imgur.com/ymz7nYV.png)

   


2.人脸录入   
![](https://i.imgur.com/Gg3hmBs.png)    


3.刷脸考勤  
![](https://i.imgur.com/ymz7nYV.png)


其余的就不多做展示了，有什么问题欢迎2391527690@qq.com联系
