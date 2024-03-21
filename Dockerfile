# 使用官方 Python 运行时作为父镜像
FROM python:3.9-slim

# 将工作目录设置为 /app
WORKDIR /app

# 将当前目录中的内容复制到 /app 中
COPY . /app

# 安装依赖
RUN pip3 install --no-cache-dir -r requirements.txt

# 在容器内运行应用
CMD ["python", "app.py"]
