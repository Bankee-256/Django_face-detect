# encoding:utf-8

import requests
import base64
import os
import json

'''
人脸检测与属性分析, 
现支持PNG、JPG、JPEG、BMP，不支持GIF图片
'''


# 图片路径
# image_path = 'C:\\Users\\Vayne Duan\\Desktop\\wcl.jpg' #绝对路径

# 返回一个包含结果的字典
def getAnalysisByBase64(image_base64):
    request_url = "https://aip.baidubce.com/rest/2.0/face/v3/detect"

    params = "{\"image\":\"" + image_base64 + "\",\"image_type\":\"BASE64\",\"face_field\":\"age,gender,beauty,expression,face_shape,glasses\"}"
    # 年龄 : age
    # 性别 : gender
    # 颜值 : beauty
    # 表情 : expression
    # 脸型 : face_shape
    # 眼睛 : glasses  
    access_token = '24.0b1db2ac0fb18e07dd84bff1f7c98e1d.2592000.1596472521.282335-21125309'
    request_url = request_url + "?access_token=" + access_token
    headers = {'content-type': 'application/json'}
    response = requests.post(request_url, data=params, headers=headers)

    data = response.json()
    # print(data)

    # 存储结果的字典
    retdict = {"error_code": data['error_code'],
               "error_msg": data['error_msg']
               }

    if data['error_code'] == 0:
        # 年龄
        age = data['result']['face_list'][0]['age']
        age = int(age)

        # 性别
        gender = data['result']['face_list'][0]['gender']['type']
        gender = ('男' if (gender == 'male') else '女')

        # 表情
        expression = data['result']['face_list'][0]['expression']['type']
        if expression == 'none':
            expression = '不笑'
        if expression == 'smile':
            expression = '微笑'
        if expression == 'laugh':
            expression = '大笑'

        # 脸型
        face_shape = data['result']['face_list'][0]['face_shape']['type']
        if face_shape == 'square':
            face_shape = '正方形'
        if face_shape == 'triangle':
            face_shape = '三角形'
        if face_shape == 'oval':
            face_shape = '椭圆'
        if face_shape == 'heart':
            face_shape = '心形'
        if face_shape == 'round':
            face_shape = '圆形'

            # 戴眼镜
        glasses = data['result']['face_list'][0]['glasses']['type']
        if glasses == 'none':
            glasses = '未佩戴'
        if glasses == 'common':
            glasses = '普通眼镜'
        if glasses == 'sun':
            glasses = '墨镜'

        # 颜值分数
        beauty = data['result']['face_list'][0]['beauty']
        beauty = float(beauty)

        # 存储结果的元组
        retarray = [age,
                    gender,
                    expression,
                    face_shape,
                    glasses,
                    beauty]

        # 存储返回结果的字典
        retdict = {"results": retarray,
                   "error_code": 0
                   }

    return retdict


def getAnalysisByPath(image_path):
    # image -> base64
    with open(image_path, 'rb') as f:
        image = f.read()
        image_base64 = str(base64.b64encode(image), encoding='utf-8')  # 图片的BASE64的字符串
    return getAnalysisByBase64(image_base64)

# if __name__ == '__main__':
#     retstr = getAnalysisByPath('static/images/test.jpg')
#     print(retstr)
