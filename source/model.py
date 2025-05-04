from log import get_current_time
import requests
import os

# 大模型服务器所在时区
# 错峰使用大模型可以获得价格优惠
# 具体参考: https://api-docs.deepseek.com/zh-cn/quick_start/pricing

HEADERS = {
  'Accept': 'application/json',
  'Authorization': f"Bearer {os.getenv('DEEPSEEK_API_KEY')}"
}

def list_models():
  """
  列出所有可用的模型
  :return: 模型列表 json 格式
  """
  url = "https://api.deepseek.com/models"
  payload={}
  
  response = requests.request("GET", url, headers=HEADERS, data=payload)
  print(response.text)

def check_balance():
  """
  查询余额
  :return: 余额信息 json 格式
  """
  url = "https://api.deepseek.com/user/balance"
  payload={}
  response = requests.request("GET", url, headers=HEADERS, data=payload)
  print(response.text)

def main():
  print("model主程序已运行!")
  list_models()
  check_balance()

if __name__ == "__main__":
  main()