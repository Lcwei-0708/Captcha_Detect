# 使用官方 Python 運行時作為父鏡像
FROM python:3.9-slim

# 設置工作目錄
WORKDIR /app

# 複製並安裝 Python 依賴
COPY requirements.txt .

# 安裝 pip 和必要的庫
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 複製當前目錄下的所有文件到容器的 /app 目錄
COPY . /app

# 暴露 8080 端口
EXPOSE 8080

# 運行 app.py
CMD ["python", "OCR.py"]