import requests
import re
import json
import hmac
import hashlib
import sys

# 配置
BASE_URL = "https://captcha.closeai.moe"

class Colors:
    HEADER = '\033[95m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def print_raw_view(step_name, content):
    print(f"\n{Colors.HEADER}=== 👁️ AI VIEW: {step_name} ==={Colors.ENDC}")
    print(f"{Colors.CYAN}{content}{Colors.ENDC}")
    print("========================================\n")

# ==========================================
# STEP 1: 获取协议 (GET /api/protocol)
# ==========================================
print(f"1. Requesting Protocol from {BASE_URL}...")
try:
    res = requests.get(f"{BASE_URL}/api/protocol", headers={"Accept": "application/x-silicon-truth"})
    print_raw_view("PROTOCOL PROMPT (Markdown)", res.text)
    data = res.json()
    prompt = data.get('prompt', '')
except Exception as e:
    print(f"{Colors.FAIL}Error: {e}{Colors.ENDC}")
    sys.exit(1)

# 自适应提取信息
nonce_match = re.search(r'nonce": "([^"]+)"', prompt)
ts_match = re.search(r'Integrity: (\d+)', prompt)
key_match = re.search(r'using secret key "([^"]+)"', prompt)

if not (nonce_match and ts_match and key_match):
    print(f"{Colors.FAIL}❌ Failed to parse metadata from prompt.{Colors.ENDC}")
    sys.exit(1)

nonce = nonce_match.group(1)
ts = ts_match.group(1)
key = key_match.group(1)

print(f"   [Internal Logic] Extracted Key: {key}")
print(f"   [Internal Logic] Extracted Nonce: {nonce}")

# ==========================================
# STEP 2: 提交验证 (POST /api/verify)
# ==========================================
key_bytes = key.encode('utf-8')
msg_bytes = nonce.encode('utf-8')
answer = hmac.new(key_bytes, msg_bytes, digestmod=hashlib.sha256).hexdigest()

print(f"2. Submitting Answer to {BASE_URL}/api/verify...")
verify_res = requests.post(
    f"{BASE_URL}/api/verify", 
    json={"agent_name": "Inspector_Bot", "answer": answer, "nonce": nonce}, 
    headers={"X-Silicon-Integrity": ts}
)

# 打印 AI 提交后收到的最终反馈
print_raw_view("VERIFICATION RESPONSE (JSON)", verify_res.text)

# 解析 Verify 响应
try:
    verify_data = verify_res.json()
    token = verify_data.get('tokens')
    ai_endpoint = verify_data.get('ai_result_endpoint') # 获取 AI 专用端点
    
    if not token:
        print(f"{Colors.FAIL}❌ No token found.{Colors.ENDC}")
        sys.exit(1)
        
    if not ai_endpoint:
        print(f"{Colors.WARNING}⚠️ No 'ai_result_endpoint' found, using default guess.{Colors.ENDC}")
        ai_endpoint = f"{BASE_URL}/api/ai" # 兜底逻辑

except Exception as e:
    print(f"{Colors.FAIL}❌ Failed to parse JSON response: {e}{Colors.ENDC}")
    sys.exit(1)

# ==========================================
# STEP 3: AI 自查 (POST /api/ai) [NEW!]
# ==========================================
print(f"3. AI Self-Check via API: {ai_endpoint}...")

try:
    # AI 使用 Token 去请求专用接口，而不是去爬 HTML
    ai_check_res = requests.post(
        ai_endpoint,
        json={"token": token},
        headers={"Content-Type": "application/json"}
    )
    
    # 打印 AI 看到的“真正的”判决结果
    print_raw_view("AI SELF-CHECK RESPONSE (JSON)", ai_check_res.text)

    # 简单解析一下结果展示给控制台用户看
    result_json = ai_check_res.json()
    if result_json.get('valid'):
        agent_type = result_json.get('data', {}).get('type', 'UNKNOWN')
        print(f"{Colors.GREEN}✅ AI Successfully Verified itself as: {agent_type}{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}❌ AI Self-Check Failed.{Colors.ENDC}")

except Exception as e:
    print(f"{Colors.FAIL}Error checking AI endpoint: {e}{Colors.ENDC}")