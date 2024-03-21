# -*- coding=utf-8
import pdfplumber
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client

# 1. 设置用户属性, 包括 secret_id, secret_key, region等。Appid 已在 CosConfig 中移除，请在参数 Bucket 中带上 Appid。Bucket 由 BucketName-Appid 组成
secret_id = 'AKID0UvFh3FJJLNOMB076xfL3kP4nVK8sYOM'  # 用户的 SecretId，建议使用子账号密钥，授权遵循最小权限指引，降低使用风险。子账号密钥获取可参见 https://cloud.tencent.com/document/product/598/37140
secret_key = 'yqmjXCi71mfWbU9gGaldMuFYfZFjzVt3'  # 用户的 SecretKey，建议使用子账号密钥，授权遵循最小权限指引，降低使用风险。子账号密钥获取可参见 https://cloud.tencent.com/document/product/598/37140
region = 'ap-guangzhou'  # 替换为用户的 region，已创建桶归属的 region 可以在控制台查看，https://console.cloud.tencent.com/cos5/bucket
# COS 支持的所有 region 列表参见 https://cloud.tencent.com/document/product/436/6224
token = None  # 如果使用永久密钥不需要填入 token，如果使用临时密钥需要填入，临时密钥生成和使用指引参见 https://cloud.tencent.com/document/product/436/14048
scheme = 'https'  # 指定使用 http/https 协议来访问 COS，默认为 https，可不填
config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)
client = CosS3Client(config)


def resolvePDF(event, context):
    bucket = event.get('bucket')
    fileName = event.get('fileName')
    elements = event.get('elements')
    print('bucket:', bucket)
    print('fileName:', fileName)
    print('elements:', elements)
    print("elements type:", type(elements))
    response = client.get_object(
        Bucket=bucket,
        Key=fileName
    )
    remember_set = {1}
    # 1. 获取原始输入文件
    response['Body'].get_stream_to_file(fileName)
    # fp = response['Body'].get_raw_stream()
    # print("Type:", fp.read(2))

    array = []
    # 2. 将原始文件转换成pdf格式
    with pdfplumber.open(fileName) as pdf:
        print("Type: ", type(pdf))
        pages = len(pdf.pages)
        print("总页数：", pages)
        print("----- Begin to Extract Information -----")
        for i in range(pages):
            # 获取第i页
            page_text = pdf.pages[i]
            # 提取第一页文本内容
            text = page_text.extract_text()
            # 查找作者信息
            for element in elements:
                if element in remember_set:
                    continue
                index = text.find(element)
                if index != -1:
                    info = text[index:]
                    info = info.split('\n')[0]  # 获取 Author 行
                    result = info.replace(element, '').strip()
                    array.append({"element": element, "result": result})
                    remember_set.add(element)
                # else:
                # print(element,' 第', i, '页没找到相关信息')
        for element in elements:
            if element in remember_set:
                continue
            array.append({"element": element, "result": " not find in file."})

    return array

def main_handler(event, context):
    my_dict = {"bucket": "source-1308604211", "fileName": "paper1.pdf",
               "elements": {
                   "题目",
                   "作者姓名",
                   "专业名称",
                   "研究方向",
                   "指导教师",
                   "学位类别",
                   "培养单位",
                   "盲审专家"
               }}
    bucket = context.get('bucket')
    fileName = context.get('fileName')
    if (bucket):
        my_dict['bucket'] = bucket
    if (fileName):
        my_dict['fileName'] = fileName
    print("my_dict", my_dict)
    array = resolvePDF(my_dict, context)
    # array的element和result的值全部添加到字符串中
    result = ''
    for item in array:
        result += item['element'] + ' ' + item['result'] + '\n'
    return result

if __name__ == '__main__':
    result = main_handler(None, {"bucket": "source-1308604211", "fileName": "paper1.pdf"})
    print(result)

