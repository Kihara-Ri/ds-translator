#!/usr/bin/env python3

# 保存问答日志, 管理回答记录
# 对于查询的单词等, 使用另一个文件进行存储

import os
from datetime import datetime
from zoneinfo import ZoneInfo
from tzlocal import get_localzone

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

def main():
  print("log主程序已运行!")
  print(get_current_time(SERVER_TIMEZONE))
  print(get_current_time())
  
if __name__ == "__main__":
  main()