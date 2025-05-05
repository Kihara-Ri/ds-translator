#!/usr/bin/env python3

# 保存问答日志, 管理回答记录
# 对于查询的单词等, 使用另一个文件进行存储

import os
import re
from datetime import datetime
from zoneinfo import ZoneInfo
from tzlocal import get_localzone
from utils import append_dict_to_json

# 保存时区
LOCAL_ZONE = get_localzone()
SERVER_TIMEZONE = ZoneInfo("Asia/Shanghai")

def get_current_time(timezone = LOCAL_ZONE) -> str:
  """
  获取当前时间
  :param timezone: 时区对象, 默认为本地时区
  :return: 当前时间字符串
  """
  if timezone == None:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  else:
    return datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S %Z")

def log_message(question: str, answer: str, prompt_type: str, log_file: str = None) -> None:
  """
  记录问答日志到log.txt文件
  :param question: 提问内容
  :param answer: 回答内容
  :param prompt_type: 使用的提问枚举类型
  :param log_file: 日志文件名, 默认路径为 ../data/log.txt
  """
  # 获取脚本所在目录
  base_dir = os.path.dirname(os.path.abspath(__file__))
  if log_file is None:
    log_file = os.path.join(base_dir, "../data/log.txt")
  log_dir = os.path.dirname(log_file)
  if not os.path.exists(log_dir):
    os.makedirs(log_dir)

  timestamp = get_current_time(LOCAL_ZONE)
  log_entry = f"[{timestamp} || Prompt Type: {prompt_type}\nQuestion: {question}\nAnswer: {answer}]\n\n"
  # 将日志写入文件
  with open(log_file, "a", encoding = "utf-8") as file:
    file.write(log_entry)
  print(f"日志已记录到 {log_file} 文件中")

def word_format(input_text: str, answer: str, request_time: str, data_file: str = None):
  """
  提取大模型输出的数据
  格式化输出为json数据
  """
  base_dir = os.path.dirname(os.path.abspath(__file__))
  if data_file is None:
    data_file = os.path.join(base_dir, "../data/word_data.json")
  data_dir = os.path.dirname(data_file)
  if not os.path.exists(data_dir):
    os.makedirs(data_dir)

  pattern = re.compile(
    r"最接近的中文解释:\s*(?P<ans1>.+?)\s*"
    r"作为俚语或日常用法:\s*(?P<ans2>.+?)\s*"
    r"常用语境:\s*(?P<ans3>.+?)\s*"
    r"造句:\s*(?P<ans4>.+?)(?:\n|$)",
    re.S
  )
  # 正则匹配回答中的关键信息
  match = pattern.search(answer)
  if match:
    ans1 = match.group("ans1")
    ans2 = match.group("ans2")
    ans3 = match.group("ans3")
    ans4 = match.group("ans4")
  else:
    print("未匹配到内容")
    return 1
  
  word_data = {
    "word": input_text,
    "closest_chinese": ans1,
    "slang_or_usage": ans2,
    "context": ans3,
    "example": ans4,
    "time": request_time
  }
  append_dict_to_json(data_file, word_data)


def main():
  print("log主程序已运行!")

if __name__ == "__main__":
  main()