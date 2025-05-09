import argparse
from prompts import Translator, User_prompt

def parse_arguments() -> tuple:
  """
  解析命令行参数
  :return: 解析后的参数和提示词类型
  """
  parser = argparse.ArgumentParser(
    description = "DeepSeek API 多模式工具", 
    formatter_class = argparse.RawTextHelpFormatter
  )

  parser.add_argument("text", nargs = "+", help = "输入需要处理的文本, 如果不传入参数则默认问答\n可以不使用引号来输入有间隔的英文单词, 但是问号需要转义字符\\")
  # parser.add_argument("text", nargs = argparse.REMAINDER, help = "输入需要处理的文本(不需要加引号, 所有后续内容都会被捕获)")
  
  parser.add_argument(
    "-f", "--stream-false",
    action = "store_true",
    help = "不采用流式传输，完整返回结果后再输出，适用于短文本"
  )
  parser.add_argument(
    "-t", "--stream-true",
    action = "store_true",
    help = "采用流式传输，适用于长文本"
  )
  
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
    "-s", "--sentence",
    action = "store_true",
    help = "解释句子, 输出其中难以理解的词汇和用法, 并给出翻译"
  )
  group.add_argument(
    "-e", "--en-synonyms",
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
  
  return args, prompt_type