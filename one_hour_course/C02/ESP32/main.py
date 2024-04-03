import network
import urequests
import os
import machine
import time
from microdot import Microdot, Response, send_file
from machine import Pin #导入Pin模块

def read_ap_info():
    #读取热点配置信息return (ssid, pwd)
    print('读取wifi配置文件')
    if 'wifi_info.txt' in os.listdir():
        print('发现wifi配置文件')
        with open('wifi_info.txt', 'r') as f:
            ssid = f.readline().strip()
            pwd = f.readline().strip()
            print('读取wifi配置文件成功',ssid, pwd)
            return ssid,pwd
        
    print('wifi配置文件不存在')
    return None, None

def write_ap_info(ssid, pwd):
    #保存热点信息
    with open('wifi_info.txt', 'w') as f:
        f.write(ssid + '\n')
        f.write(pwd + '\n')
    print('写入wifi配置文件成功...')
    
def connect_wifi(ssid, pwd):
    #连接到WiFi
    try:
        print('尝试连接到WiFi'+ssid)
        wlan = network.WLAN(network.STA_IF) # 创建站点接口
        wlan.active(False)
        wlan.active(True)                   # 激活接口
        if not wlan.isconnected():          # 检查是否连接 
            wlan.connect(ssid, pwd)    # 连接到热点
            i = 0
            while not wlan.isconnected():   # 检查状态直到连接到热点或失败
                time.sleep(1) #等待1秒
                print('正在连接',ssid,i)
                i = i+1
                if i>=5: #大于5秒超时，返回
                    return False
        print('已经连接到WiFi%s', ssid)        
        print('网络信息:', wlan.ifconfig()) #打印网络信息
        return True
    except:
        return False
    

def scan_wifi():
    #扫描附近的热点，返回热点列表
    print('扫描附近的WiFi热点...')
    import network #有时候外面的import不起作用
    
    sta_if = network.WLAN(network.STA_IF) #创建个WLAN的实例
    sta_if.active(False)#先关闭，再打开
    if not sta_if.isconnected():
        sta_if.active(True)  #激活网络接口
    networks = sta_if.scan() #扫描可用的无线网络。networks是扫描结果的元组数组
    ssids = []
    for network in networks: #循环，打印热点信息
        ssid = network[0].decode('utf-8')
        is_open = network[4]==0 #是否是开放热点，不需要密码
        if len(ssid)>0:
            ssids.append({"ssid":ssid, "is_open":is_open}) #每个热点一个元组，ssid，是否需要密码
    sta_if.active(False)
    print('扫描WiFi热点完成，发现',len(ssids),'个热点')
    return ssids

def restart_device():
    print('现在重启....')
    machine.reset()

def restart(sec=3):
    # 设置定时器，3秒后执行restart_device函数
    print(sec,'秒后重启')
    timer = machine.Timer(-1)
    timer.init(period=sec*1000, mode=machine.Timer.ONE_SHOT, callback=lambda t:restart_device())
 

def start_config_server():
    
    wifi_list = scan_wifi() #获取热点列表
    #启动WiFi热点
    print('正在启动wifi热点：ESP32-WiFi')
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid='ESP32-WiFi')
    print('wifi热点：ESP32-WiFi 已启动...')
    #启动配置服务，提供一个页面进行
    print('启动服务，连接到热点后，用浏览器打开地址：http://192.168.4.1/ 进行配置')
    app = Microdot()# 创建Web服务

    @app.route('/')  #绑定配置页面路由
    def index_page(request):
        print('/ 配置页面请求，返回index.html')
        return send_file('index.html')
    
    @app.route('/list')  #绑定配置页面路由
    def get_ap_list(request):
        print('/list 请求，返回', wifi_list)
        return Response(body=wifi_list)

    @app.route('/save', methods=['POST']) #绑定提交页面路由
    def save_method(request):
        data = request.json
        print('/save请求，数据：',data)
        ssid = data.get("ssid")
        pwd = data.get("pwd")
        if ssid==None or ssid=='':
            return Response(body={"ret":False, "msg":"ssid不能为空！"})
        else:
            write_ap_info(ssid, pwd)
            restart()
            return Response(body={"ret":True, "msg":"保存成功，三秒后重启！"})
    
    # 启动Web服务器
    print("服务已经启动，等待连接....")
    app.run(host='0.0.0.0', port=80)

def get_server_time(): #获取服务器时间并打印
    print('请求服务器时间')
    response = urequests.get("https://api.suniot.top/learn/time")  #使用urequest从服务器获取时间信息
    current_time = response.text       #获取返回的内容
    print("服务器时间：", current_time) #打印时间
    response.close()  #关闭response

def blink(t=0.5):
    #持续闪烁
    led = Pin(22, Pin.OUT) # 把22管脚设置为输出
    while(True):  #循环10次
        led.value(0)     #打开LED，这个LED是低电位点亮
        time.sleep(t)  #休眠0.5秒
        led.value(1)     #关闭LED
        time.sleep(t)  #再休眠0.5秒

def light():
    #持续亮灯
    led = Pin(22, Pin.OUT) # 把22管脚设置为输出
    led.value(0)     #打开LED，这个LED是低电位点亮

def main():
    #读取热点配置信息
    ssid,pwd = read_ap_info()
    if ssid and len(ssid)>0:
        if connect_wifi(ssid, pwd):
            try:
                get_server_time()
                blink(1) #完成任务，led 1秒间隔持续闪烁
            except:
                print('请求服务器时间失败！')
                blink(0.25) #完成任务，led 0.25秒间隔快速持续闪烁
    
    #进入网络配置
    light()#led长亮，进入网络配置状态
    start_config_server()

main()
