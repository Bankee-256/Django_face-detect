import json
import requests
from urllib import parse


# 返回文本转语音对应的二进制流
def getAudio(TEXT, voice):
    # 设置 access_token
    token = '24.4740ca74e72c2c83ed4f52050c499e94.2592000.1596482868.282335-21125309'

    tex = parse.quote_plus(TEXT)  # 两次urlencode
    # 设置文本以及其他参数
    params = {'tok': token,  # 开放平台获取到的开发者access_token
              'tex': TEXT,  # 合成的文本，使用UTF-8编码。小于2048个中文字或者英文数字
              'per': voice,  # 发音人选择, 基础音库：0为度小美，1为度小宇，3为度逍遥，4为度丫丫，
              #            精品音库: 度博文=106，度小童=110，度小萌=111，度米朵=103，度小娇=5
              'spd': 4,  # 语速，取值0-15，默认为5中语速
              'pit': 5,  # 音调，取值0-15，默认为5中语调
              'vol': 5,  # 音量，取值0-15，默认为5中音量
              'aue': 6,  # 下载的文件格式, 3为mp3格式(默认); 4为pcm-16k; 5为pcm-8k; 6为wav（内容同pcm-16k）
              'cuid': "7749py",  # 用户唯一标识
              'lan': 'zh',  # 固定值zh。语言选择,目前只有中英文混合模式，填写固定值zh
              'ctp': 1}  # 客户端类型选择，web端填写固定值1
    req = requests.post("http://tsn.baidu.com/text2audio", params)
    result_str = req.content
    # print(result_str)

    # 如果返回的header里有”Content-Type: audio/wav“信息，则合成成功
    if "audio/wav" in req.headers['content-type']:
        print("getAudio Success")
        return result_str
    elif "application/json" in req.headers['content-type']:
        # 合成失败, 打印错误信息, 进行debug
        # 后期可以改成写入到日志文件
        print('getAudio Failed')
        print(result_str)

#
# if __name__ == '__main__':
#     TEXT = "['年龄: 40岁', '性别: 男', '表情: 不笑', '脸型: 正方形', '眼镜: 未佩戴', '颜值分: 63.1']"
#     TEXT += "恭喜您, 您的颜值超过了全国55%的人"
#     getAudio(TEXT, 111)
