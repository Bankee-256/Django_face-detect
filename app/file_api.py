import uuid
import os
import base64


# 保存base64解码后的数据到文件
def savaUserFile(username, b64data):
    absPath = os.path.join(os.getcwd(), 'app/static/user/' + username)
    if not os.path.exists(absPath):
        os.makedirs(absPath)
    uuidstr = str(uuid.uuid1()).replace("-", "")
    filePath = absPath + "/" + uuidstr + '.jpg'
    picPath = 'user' + "/" + username + "/" + uuidstr + '.jpg'
    try:
        img = base64.b64decode(b64data)
        with open(filePath, 'wb') as f:
            f.write(img)
            f.close()
            print('image saved')
    except:
        print('save image failed')
    return picPath


# 删除用户上传的文件
def delUserFile(pic_path):
    absPath = os.path.join(os.getcwd(), 'app/static/' + pic_path)
    try:
        if (os.path.exists(absPath)):
            os.remove(absPath)
            print('image deleted')
        else:
            print('image has deleted')
    except:
        print('del image failed')


# if __name__ == '__main__':
#     picPath = savaUserFile("test", base64.b64encode(b"1234"))
#     delUserFile(picPath)
