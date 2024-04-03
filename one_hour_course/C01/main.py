import time # 导入time模块
from machine import Pin #导入Pin模块

led = Pin(22, Pin.OUT) # 把22管脚设置为输出
for i in range(10):  #循环10次
    led.value(0)     #打开LED，这个LED是低电位点亮
    time.sleep(0.5)  #休眠0.5秒
    led.value(1)     #关闭LED
    time.sleep(0.5)  #再休眠0.5秒