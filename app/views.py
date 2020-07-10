import json
import time

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

import app.audio_api as audio_api
import app.face_api as face_api
import app.file_api as file_api
from app.models import Result, UserProfile, Like


# 主页
def index(request):
    # 判断用户是否登录
    if request.user.is_authenticated:
        # 获取登录用户
        user = request.user
        userprofile = get_object_or_404(UserProfile, user=user)
        context = dict()
        context['nickname'] = userprofile.nickname
        return render(request, 'index.html', context)
    else:
        return render(request, "index.html")


# 注册页
def register(request):
    return render(request, 'register.html')


# 登录
def myLogin(request):
    if request.POST:
        # 接收参数
        username = request.POST.get('phoneNumber', None)
        password = request.POST.get('passwordNumber', None)

        user = authenticate(username=username, password=password)

        if user is not None:
            # 存在该用户, 则进行登录
            # 这里的login函数, 主要是hi为了把登录的对象存入到django_session表
            login(request, user)
            # 响应到客户端
            # 设置session
            request.session['username'] = username

            # 用户登录成功返回到主页面
            return redirect('/app/index/')
        else:
            # 用户登录失败回到注册页
            return render(request, 'login.html', {'msg': '登陆验证失败...'})
    else:
        if request.user.is_authenticated:
            return redirect('/app/index/')
        return render(request, 'login.html')


# 安全退出
def myLogout(request):
    # 清除session
    del request.session['username']
    # 登出
    logout(request)
    return render(request, 'index.html')


# 修改用户信息
@login_required
def modify(request):
    if request.POST:
        user = request.user
        userprofile = get_object_or_404(UserProfile, user=user)

        # 初始化字典, 记录用户信息
        context = dict()
        context['username'] = request.user.username
        context['nickname'] = userprofile.nickname
        context['city'] = userprofile.city
        context['gender'] = userprofile.gender

        # 接收数据
        gender = request.POST.get('gender', None)
        city = request.POST.get('city', None)
        nickname = request.POST.get('nickname')
        pwd0 = request.POST.get('pwd0', None)
        pwd1 = request.POST.get('pwd1', None)
        pwd2 = request.POST.get('pwd2', None)

        # 数据处理
        if gender is not None:
            if gender == '男' or gender == '女':
                userprofile.gender = gender
            else:
                context['msg'] = '必须输入男或女'
                return render(request, 'pinformation.html', context)
        if city is not None:
            userprofile.city = city
        if nickname is not None:
            userprofile.nickname = nickname

        # 用户修改
        if pwd0 is not None:
            user = authenticate(username=user.username, password=pwd0)
            if user is not None:
                if pwd1 == pwd2:
                    user.set_password(pwd1)
                    userprofile.save()
                    user.save()
                    context['gender'] = userprofile.gender
                    context['city'] = userprofile.city
                    context['nickname'] = userprofile.nickname
                    context['msg'] = '信息修改成功'
                    # 修改成功并保存
                    return redirect("/app/login/")
                else:
                    # 两次输入的密码不一致
                    context['msg'] = '两次输入密码不一致，请重新输入'
                    return render(request, 'pinformation.html', context)
            else:
                # 原密码不匹配
                context['msg'] = '原密码不正确'
                return render(request, 'pinformation.html', context)
        else:
            # 未修改密码，保存并返回
            userprofile.save()
            context['gender'] = userprofile.gender
            context['city'] = userprofile.city
            context['nickname'] = userprofile.nickname
            context['msg'] = '信息修改成功'
            return render(request, 'pinformation.html', context)
    else:
        # 网页初始化
        user = request.user
        userprofile = get_object_or_404(UserProfile, user=user)
        context = dict()
        context['username'] = request.user.username
        context['nickname'] = userprofile.nickname
        context['city'] = userprofile.city
        context['gender'] = userprofile.gender
        return render(request, 'pinformation.html', context)


# 创建用户
def createUser(request):
    if request.POST:
        # 获取参数
        username = request.POST.get('phoneNumber', None)
        pwd1 = request.POST.get('pwd1', None)
        pwd2 = request.POST.get('pwd2', None)
        nickname = request.POST.get('nickname', None)
        city = request.POST.get('city', None)
        gender = request.POST.get('gender', None)
        if (gender is None) or (nickname is None) or (city is None) or (pwd1 is None) or (pwd2 is None) or (
                username is None):
            return render(request, 'register.html', {'msg': '信息不能为空'})
        else:
            if pwd1 == pwd2:
                # 判断用户是否存在
                user = User.objects.filter(username=username)

                if len(user) > 0:
                    return render(request, 'register.html', {'msg': '用户名已经被使用'})

                # 这是用户名可以使用的时候
                # 向django_user数据表种添加数据
                user = User.objects.create_user(username=username, password=pwd1)
                # 向userProfile表中添加数据
                profile = UserProfile()
                # 这是建立外键的一对一关系
                profile.user_id = user.id
                profile.gender = gender
                # 这是为phone属性赋值
                profile.nickname = nickname
                profile.city = city
                profile.save()

                # 给用户添加权限
                contentType = ContentType.objects.get_for_model(Result)
                permissions = Permission.objects.filter(content_type=contentType)
                # 添加 点赞 和 查看排行榜 的电脑
                user.user_permissions.add(permissions[0], permissions[3])
                user.save()
                print(user.get_all_permissions())
                return redirect('/app/login/')
            else:
                return render(request, 'register.html', {'msg': '注册失败，请检查密码格式'})
    else:
        return render(request, 'register.html')


# 文本转语音api
def text2audio(request):
    if request.POST:
        text = request.POST.get('data', "未找到识别结果")
        voice = int(request.POST.get('voice', 0))
        blob = audio_api.getAudio(text, voice)
        return HttpResponse(blob)
    else:
        return redirect("/app/Camera/")


# 识别页面
def CMR(request):
    if request.user.is_authenticated:
        user = request.user
        print(user.username)
        userprofile = get_object_or_404(UserProfile, user=user)
        nickname = userprofile.nickname
        isPremier = User.objects.get(username=user.username).has_perm('app.high_quality_voice')
        print(isPremier)
        return render(request, 'Camera.html', {'nickname': nickname})
    else:
        return render(request, "Camera.html")


# 调用api将图片识别结果返回
def CMR2server(request):
    if request.method == 'POST':
        body = request.body
        strbody = body.decode()
        try:
            index = strbody.index("base64")
            b64data = strbody[index + 7:]
        except:
            b64data = strbody

        ret = face_api.getAnalysisByBase64(b64data)

        username = request.session.get('username', None)
        if username and User.objects.get(username=username) and ret['error_code'] == 0:
            # 写入文件
            picPath = file_api.savaUserFile(username, b64data)
            # 将 结果 和 相对路径 存入数据库
            user = User.objects.get(username=username)
            userProfile = UserProfile.objects.get(user_id=user.id)
            result = ret['results']

            # [age, gender, expression, face_shape, glasses, beauty]
            Result.objects.create(userProfile=userProfile, age=result[0], gender=result[1], expression=result[2],
                                  face_shape=result[3], glasses=result[4], value=result[5], pic_path=picPath)
        return HttpResponse(json.dumps(ret))
    else:
        return redirect('../Camera')


# 获取用户是否点赞
def getIsLike(user_id, pic_id):
    # 默认用户未点赞
    is_like = False
    try:
        like = Like.objects.get(pic_id=pic_id, user_id=user_id)
        if like.is_like:
            return True
        else:
            return False
    except:
        return False


# 获取颜值排行榜
def rank(request):
    context = dict()
    context['result_firstRow'] = []
    context['result_secondRow'] = []
    # 获得颜值从高到低的排名
    top = Result.objects.filter(authorization=True).order_by('-value')

    # 前端显示分成两行，一行4位用户,
    # 首先判断允许公开的记录总数
    # 返回记录的id，用户的昵称，图片路径，颜值，是否点赞，和点赞数给前端
    # 是否点赞是针对浏览网页的用户而不是允许分享该记录的用户
    # 对于已经点赞的用户显示点赞后的效果
    m = len(top)
    # 只有<=4位用户允许公开
    if m <= 4:
        for i in range(m):
            r = top[i]
            context['result_firstRow'].append(
                (r.pic_id, i + 1, r.userProfile.nickname, r.pic_path, r.value, getIsLike(request.user.id, r.pic_id),
                 r.thumbsUpTime))
    # 有>4位用户允许公开，分开传给前端，分成两行显示
    else:
        for i in range(4):
            r1 = top[i]
            context['result_firstRow'].append(
                (r1.pic_id, i + 1, r1.userProfile.nickname, r1.pic_path, r1.value,
                 getIsLike(request.user.id, r1.pic_id),
                 r1.thumbsUpTime))
            if i + 4 < m:
                r2 = top[i + 4]
                context['result_secondRow'].append(
                    (r2.pic_id, i + 5, r2.userProfile.nickname, r2.pic_path, r2.value,
                     getIsLike(request.user.id, r2.pic_id), r2.thumbsUpTime))

    user = request.user
    if request.user.is_authenticated:
        userprofile = get_object_or_404(UserProfile, user=user)
        context['nickname'] = userprofile.nickname
    return render(request, 'rank.html', context)


# 查询历史记录
@login_required
def history(request):
    if request.user.is_authenticated:
        user = request.user
        if user:
            context = dict()
            context['history'] = []
            userprofile = get_object_or_404(UserProfile, user=user)
            context['nickname'] = userprofile.nickname
            try:
                page = 1
                if request.POST:
                    # 获取需要跳转到的历史记录页面数
                    # print(request.POST.get('page', 1))
                    page = int(request.POST.get('page', 1))
                his = Result.objects.filter(userProfile=UserProfile.objects.get(user=user)).order_by('pic_id')
                print(page)
                totalPage = int(len(his) / 5) + 1
                # 返回总页数给前端
                context['totalPage'] = totalPage
                # 分页器，每页显示5条数据
                paginator = Paginator(his, 5)
                # 前端显示的页
                currentPage = paginator.page(page)
                for i in range(len(currentPage)):
                    p = currentPage[i]
                    context['history'].append(
                        (user.username, p.pic_id, p.date, p.authorization, p.pic_path, p.value, p.thumbsUpTime))
            except:
                print('get user\'s history with exception')

            return render(request, 'history.html', context)
        else:
            # 返回至上一页面 或 主页面 或 其他页面
            return render(request, 'history.html', {'msg': 'access error'})
    else:
        return render(request, 'pinformation.html')


# 更新历史记录
@login_required
def update_history(request):
    if request.POST:
        if request.user.is_authenticated:
            user = request.user
            try:
                # 获取用户对是否公开人脸识别记录的更改
                # auth = False：不公开；auth = True：公开
                auth = request.POST.get('is_auth', False)
                if auth == '1':
                    auth = True
                pic_id = request.POST.get('pic_id', None)
                Result.objects.filter(pic_id=pic_id, userProfile=UserProfile.objects.get(user=user)).update(
                    authorization=auth)
            except:
                print('update_history failed')
    return redirect('/app/history/')


# 删除历史记录
@login_required
def delete_history(request):
    if request.POST:
        if request.user.is_authenticated:
            username = request.user.username
            user = User.objects.get(username=username)
            try:
                # 获取需要删除的历史记录的id值
                pic_id = request.POST.get('pic_id', None)
                # 查找该记录
                obj = Result.objects.filter(pic_id=pic_id, userProfile=UserProfile.objects.get(user=user))
                if obj[0]:
                    pic_path = obj[0].pic_path
                    file_api.delUserFile(pic_path)
                    obj.delete()
            except:
                print('delete_history failed')
    return redirect('/app/history/')


# 点赞
@login_required
def thumbs_up(request):
    if request.POST:
        # print(request.user.has_perm('app.thumbs_up'))
        if request.user.is_authenticated:
            pic_id = request.POST.get('pic_id', None)
            user = request.user
            # like = Like.objects.get(pic_id=pic_id, user_id=user.id)出现异常表示用户首次点击点赞按钮
            try:
                # 用户更改点赞状态
                like = Like.objects.get(pic_id=pic_id, user_id=user.id)
                r = Result.objects.get(pic_id=pic_id)
                # 更新点赞数量
                if like.is_like:
                    new_thumbs = r.thumbsUpTime - 1
                else:
                    new_thumbs = r.thumbsUpTime + 1
                like.is_like = not like.is_like  # 取反
                like.save()
                r.thumbsUpTime = new_thumbs
                r.save()
            except:
                # 用户首次点赞，添加该点赞记录
                Like.objects.create(pic_id=pic_id, user_id=user.id, is_like=True)
                r = Result.objects.get(pic_id=pic_id)
                thumbs = r.thumbsUpTime + 1
                r.thumbsUpTime = thumbs
                r.save()
    return redirect('/app/rank/')
