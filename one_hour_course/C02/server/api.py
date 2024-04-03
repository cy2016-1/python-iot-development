from flask.app import Flask
from flask.globals import request
import time

#初始化app
app = Flask(__name__, instance_relative_config=True)

@app.route('/time', methods=['GET', 'POST'])
def get_time():
    #返回格式化后的当前日期和时间
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

@app.route('/', methods=['GET', 'POST'])
def hello():
    return '<h1 style="color:blue">Iot server is running!</h1>'

if __name__ == "__main__":
    app.run(host='0.0.0.0')