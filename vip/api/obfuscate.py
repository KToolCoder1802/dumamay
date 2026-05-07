import sys
import os
import base64
import zlib
import json

# Thêm thư mục gốc vào path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import PYMEO
try:
    from pymeo import obfuscate
    PYMEO_READY = True
    print("[OK] PYMEO loaded", flush=True)
except ImportError as e:
    PYMEO_READY = False
    print(f"[WARN] PYMEO not loaded: {e}", flush=True)
    # Fallback obfuscate function
    def obfuscate(code, mode=2, more_obf=False, antidebug=True, anticrack=True, username="API_USER"):
        compressed = zlib.compress(code.encode())
        encoded = base64.b64encode(compressed).decode()
        return f"import base64,zlib\nexec(zlib.decompress(base64.b64decode('{encoded}')))"

def handler(request):
    """Vercel serverless function handler"""
    
    # Xử lý CORS preflight
    if request.method == 'OPTIONS':
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            },
            "body": ""
        }
    
    # Xử lý GET request
    if request.method == 'GET':
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "status": "ok",
                "message": "PYMEO Obfuscator API",
                "pymeo_loaded": PYMEO_READY
            })
        }
    
    # Xử lý POST request
    if request.method == 'POST':
        try:
            # Lấy dữ liệu từ request
            content_type = request.headers.get('content-type', '')
            raw_body = request.get_data()
            
            # Lấy tham số từ form
            mode = 2
            more_obf = True
            antidebug = True
            anticrack = True
            username = "API_USER"
            file_content = None
            filename = "obfuscated.py"
            
            # Parse multipart form data
            if 'multipart/form-data' in content_type:
                boundary = content_type.split('boundary=')[1].encode()
                parts = raw_body.split(boundary)
                
                for part in parts:
                    # Lấy nội dung file
                    if b'filename=' in part:
                        # Lấy tên file
                        for line in part.split(b'\r\n'):
                            if b'filename=' in line:
                                filename = line.decode().split('filename="')[1].split('"')[0]
                                break
                        
                        # Lấy nội dung
                        start = part.find(b'\r\n\r\n')
                        if start != -1:
                            file_content = part[start + 4:].rstrip(b'\r\n--')
                    
                    # Lấy tham số mode
                    if b'name="mode"' in part:
                        start = part.find(b'\r\n\r\n')
                        if start != -1:
                            try:
                                mode = int(part[start + 4:].strip())
                            except:
                                pass
                    
                    # Lấy username
                    if b'name="username"' in part:
                        start = part.find(b'\r\n\r\n')
                        if start != -1:
                            username = part[start + 4:].strip().decode()
            
            if not file_content:
                return {
                    "statusCode": 400,
                    "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                    "body": json.dumps({"error": "No file uploaded"})
                }
            
            # Đọc code
            code = file_content.decode('utf-8', errors='ignore')
            
            # Obfuscate bằng PYMEO
            result = obfuscate(
                code=code,
                mode=mode,
                more_obf=more_obf,
                antidebug=antidebug,
                anticrack=anticrack,
                username=username
            )
            
            # Trả về file
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "text/x-python",
                    "Content-Disposition": f"attachment; filename=obfuscated_{filename}",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": result,
                "isBase64Encoded": False
            }
            
        except Exception as e:
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": str(e)})
            }
    
    return {
        "statusCode": 405,
        "headers": {"Access-Control-Allow-Origin": "*"},
        "body": "Method not allowed"
    }