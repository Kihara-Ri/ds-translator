#!/usr/bin/env python3

import argparse
import os
import threading
import json
import sys
from openai import OpenAI

from prompts import Translator, User_prompt
from log import log_message
from utils import loading_animation, loading_event, measure_time

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

client = OpenAI(api_key = os.getenv('DEEPSEEK_API_KEY'), base_url = "https://api.deepseek.com")

# HEADERS = {
#   "Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}",
#   "Content-Type": "application/json"
# } 

# input_text 只是从命令行中输入的一小段核心问题
# prompt 则是根据预设的提示词加上 input_text 生成的完整提示词

@measure_time
def send_messages(input_text: str, prompt: str, prompt_type) -> None:
  # 启动加载动画线程
  animation_thread = threading.Thread(target = loading_animation)
  animation_thread.start()
  
  # 发送请求
  try:
    response = client.chat.completions.create(
      model = "deepseek-chat",
      messages = [
        {"role": "user", "content": prompt}
      ],
      # response_format = "text",
      stream = False,
      temperature = 0.3,
      max_tokens = 1024
    )
    answer = response.choices[0].message.content
    tokens_used = response.usage.total_tokens
    print(f"\n{answer}")
    print(f"\n使用的token数: {tokens_used}")
    # 记录日志
    log_message(question = input_text, answer = answer, prompt_type = prompt_type)
  finally:
    # 停止加载动画
    loading_event.set()
    animation_thread.join()

def translate(input_text, prompt_type):
  # 获取对应的prompt
  prompt = prompt_type.value.format(text = input_text)

  # 如果提示词类型属于[单词解释], 则触发 json 输出
  if prompt_type == Translator.explain_word:
    send_messages(input_text, prompt, prompt_type)
  else:
    send_messages(input_text, prompt, prompt_type)

def main():
  parser = argparse.ArgumentParser(
    description = "DeepSeek API 多模式工具", 
    formatter_class = argparse.RawTextHelpFormatter
  )
  parser.add_argument("text", nargs = "+", help = "输入需要处理的文本, 如果不传入参数则默认问答\n可以不使用引号来输入有间隔的英文单词, 但是问号需要转义字符\\")
  # parser.add_argument("text", nargs = argparse.REMAINDER, help = "输入需要处理的文本(不需要加引号, 所有后续内容都会被捕获)")
  
  # 三个互斥的选项: translate, word, default(不传入参数时)
  group = parser.add_mutually_exclusive_group()
  group.add_argument(
    "-tr", "--translate",
    action = "store_true",
    help = "将中文翻译成英文和日文"
  )
  group.add_argument(
    "-w", "--word",
    action = "store_true",
    help = "解释单词/词组/短语, 输出含义和语境及其应用场景, 并且给出例句"
  )
  group.add_argument(
    "-tj", "--translate-jp",
    action = "store_true",
    help = "将中文翻译成日文, 更加精细化"
  )
  # 如果都不传，就默认走问答模式
  args = parser.parse_args()
  if args.translate:
    prompt_type = Translator.fast_translate
  elif args.word:
    prompt_type = Translator.explain_word
  elif args.translate_jp:
    prompt_type = Translator.translate_jp
  else:
    # 默认走问答模式
    prompt_type = User_prompt.default_answer

  input_text = ' '.join(args.text)
  
  if not os.getenv('DEEPSEEK_API_KEY'):
    print("请设置环境变量 DEEPSEEK_API_KEY")
    sys.exit(1)
    
  translate(input_text, prompt_type)
  
if __name__ == "__main__":
  main()