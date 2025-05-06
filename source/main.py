#!/usr/bin/env python3

import argparse
import os
import threading
import requests
import sys
from openai import OpenAI

from prompts import Translator, User_prompt
from log import log_message, get_current_time, word_format
from utils import Animation, loading_animation, measure_time, animation_event, request_done, RED_DOT

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

client = OpenAI(api_key = os.getenv('DEEPSEEK_API_KEY'), base_url = "https://api.deepseek.com")

# HEADERS = {
#   "Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}",
#   "Content-Type": "application/json"
# } 

# input_text 只是从命令行中输入的一小段核心问题
# prompt 则是根据预设的提示词加上 input_text 生成的完整提示词

@measure_time
def send_messages(input_text: str, 
                  prompt: str, 
                  prompt_type, 
                  isStream: bool = False,
                  ) -> tuple:
  """
  发起请求到 DeepSeek API
  默认为非流式传输模式
  :param input_text: 输入的文本
  :param prompt: 生成的提示词
  :param prompt_type: 提示词类型
  :return: 返回内容: 大模型的回答内容, 使用的token数, 请求时间
  """
  # 启动加载动画线程
  animation_thread = threading.Thread(target = loading_animation, args = (Animation.spin, isStream)) # 只能这么写
  animation_event.clear()
  request_done.clear()
  animation_thread.start()
  
  # 发送请求
  try:
    request_time = get_current_time()
    response = client.chat.completions.create(
      model = "deepseek-chat",
      messages = [
        {"role": "user", "content": prompt}
      ],
      # response_format = "text",
      stream = isStream,
      temperature = 0.3,
      max_tokens = 1024
    )
    
    answer = ""
    tokens_used = 0
    # 获取返回的内容
    if isStream:
      animation_event.set() # 设置动画状态为正在请求
      for chunk in response:
        if chunk.choices[0].finish_reason == 'stop':
          request_done.set()
          tokens_used = chunk.usage.total_tokens
          break
        else:
          reply = chunk.choices[0].delta.content
          answer += reply
          print(reply, end = '', flush = True)
    else:
      request_done.set()
      answer = response.choices[0].message.content
      tokens_used = response.usage.total_tokens
    
  except requests.exceptions.RequestException as e:
    print(f"\n{RED_DOT} 请求失败: {e}")
    log_message(question = input_text, answer = "请求失败", prompt_type = prompt_type)
  except Exception as e:
    print(f"\n{RED_DOT} 未知错误: {e}")
    log_message(question = input_text, answer = "未知错误", prompt_type = prompt_type)
  finally:
    # 停止加载动画
    request_done.set()
    animation_thread.join() # 等待动画线程结束
    print(f"\n{answer}")
    print(f"\n使用的token数: {tokens_used}")
    log_message(question = input_text, answer = answer, prompt_type = prompt_type)
    return answer, tokens_used, request_time

def translate(input_text, prompt_type):
  """
  根据输入文本恶化提示词类型调用API并处理返回结果
  """
  # 获取对应的prompt
  prompt = prompt_type.value.format(text = input_text)

  try:
    # 如果提示词类型属于[单词解释], 则触发 json 输出
    if prompt_type == Translator.explain_word:
      answer, tokens_used, request_time = send_messages(input_text, prompt, prompt_type)
      if answer: # 确保返回值有效
        word_format(input_text, answer, request_time)
      else:
        print(f"\n{RED_DOT} 未能获取有效的回答")
    else:
      # 其他类型直接调用API
      send_messages(input_text, prompt, prompt_type)
  except KeyboardInterrupt:
    print(f"\n{RED_DOT} 请求已中断，程序已安全退出")
  except Exception as e:
    print(f"\n{RED_DOT} 程序发生错误: {e}")
    log_message(question = input_text, answer = "程序发生错误", prompt_type = prompt_type)

def main():
  parser = argparse.ArgumentParser(
    description = "DeepSeek API 多模式工具", 
    formatter_class = argparse.RawTextHelpFormatter
  )
  parser.add_argument("text", nargs = "+", help = "输入需要处理的文本, 如果不传入参数则默认问答\n可以不使用引号来输入有间隔的英文单词, 但是问号需要转义字符\\")
  # parser.add_argument("text", nargs = argparse.REMAINDER, help = "输入需要处理的文本(不需要加引号, 所有后续内容都会被捕获)")
  
  group = parser.add_mutually_exclusive_group()
  group.add_argument(
    "-tr", "--translate",
    action = "store_true",
    help = "中日英三语翻译, 识别语言并翻译成另外两种语言"
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
  group.add_argument(
    "-e", "--sentence",
    action = "store_true",
    help = "解释句子, 输出其中难以理解的词汇和用法, 并给出翻译"
  )
  group.add_argument(
    "-s", "--en-synonyms",
    action = "store_true",
    help = "查询英文同义词/近义词, 输出表格"
  )
  # 如果都不传，就默认走问答模式
  args = parser.parse_args()
  if args.translate:
    prompt_type = Translator.fast_translate
  elif args.word:
    prompt_type = Translator.explain_word
  elif args.translate_jp:
    prompt_type = Translator.translate_jp
  elif args.sentence:
    prompt_type = Translator.explain_sentence
  elif args.en_synonyms:
    prompt_type = Translator.en_synonyms
  else:
    # 默认走问答模式
    prompt_type = User_prompt.default_answer

  input_text = ' '.join(args.text)
  
  if not os.getenv('DEEPSEEK_API_KEY'):
    print("请设置环境变量 DEEPSEEK_API_KEY")
    sys.exit(1)

  try:
    translate(input_text, prompt_type)
  except KeyboardInterrupt:
    # 捕获 Ctrl+C 中断
    print(f"\n{RED_DOT} 请求已中断，程序已安全退出")
  except Exception as e:
    print(f"\n{RED_DOT} 程序发生错误: {e}")
    log_message(question = input_text, answer = "程序发生错误", prompt_type = prompt_type)
  
if __name__ == "__main__":
  main()