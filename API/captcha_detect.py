import io
import os
import ddddocr
import logging
from PIL import Image
from flask_cors import CORS
from datetime import datetime
from flask import Flask, request, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)

# 使用 CORS 來限制特定網域才能訪問
CORS(app, resources={r"/captcha_ocr": {"origins": "輸入網域名稱或是IP"}})

# 使用 ProxyFix 中間件處理代理伺服器
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# 配置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 初始化 ddddocrS
ocr = ddddocr.DdddOcr(show_ad=False)

# 設置允許的文件類型
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def log_api_usage(request, result):
    client_ip = request.remote_addr
    user_agent = request.user_agent.string
    timestamp = datetime.now().isoformat()
    logger.info(f"API Usage - IP: {client_ip}, User-Agent: {user_agent}, Timestamp: {timestamp}, Result: {result}")

@app.route('/captcha_ocr', methods=['POST'])
def captcha_ocr():
    try:
        logger.info('Received POST request')
        
        # 檢查是否有文件
        if 'image' not in request.files:
            logger.warning('No file part in the request')
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['image']
        
        # 檢查文件名是否為空
        if file.filename == '':
            logger.warning('No selected file')
            return jsonify({'error': 'No selected file'}), 400
        
        # 檢查文件類型
        if not allowed_file(file.filename):
            logger.warning('Invalid file type')
            return jsonify({'error': 'Invalid file type'}), 400
        
        # 讀取圖片
        image_bytes = file.read()
        image = Image.open(io.BytesIO(image_bytes))
        
        # 進行 OCR
        result = ocr.classification(image)
        logger.info(f'OCR result: {result}')
        
        # 記錄 API 使用情況
        log_api_usage(request, result)
        
        return jsonify({'result': result})
    
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error processing image: {error_message}")
        log_api_usage(request, f"Error: {error_message}")
        return jsonify({'error': error_message}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)