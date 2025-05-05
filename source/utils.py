import itertools
import time
import threading
import os
import json
import shutil
import tempfile
from enum import Enum

YELLOW_DOT = "\033[38;2;245;148;37m●\033[0m"
GREEN_DOT =  "\033[38;2;37;245;58m●\033[0m"
RED_DOT = "\033[38;2;242;12;12m●\033[0m"

class Animation(Enum):
  dots = (['.', '..', '...'], 0.5) # 目前还有问题，一直是三个点，之前的动画帧没有被清除
  spin = (['-', '/', '|', '\\'], 0.15)

# 控制加载动画 全局事件
loading_event = threading.Event()

def loading_animation(message: str = f"{YELLOW_DOT} 正在请求", animation_type: Enum = Animation.spin):
  frames, frame_rate = animation_type.value
  max_frame_len = max(len(f) for f in frames) # 计算最长帧用于清行
  clear_line = '\r' + ' ' * (len(message) + 1 + max_frame_len)
  
  for frame in itertools.cycle(frames):
    if not loading_event.is_set():
      # 每次打印前都进行一次清空
      print(f'{clear_line}\r{message} {frame}', end = "", flush = True)
      time.sleep(frame_rate)
    else:
      break
  # 请求完成后，清空动画并打印“请求完毕”
  # 需要注意这里的 end 和 flush
  print(f'{clear_line}\r{GREEN_DOT} 请求完毕', end = "\n", flush = False) # 清除加载动画

def measure_time(func):
  """
  计时器装饰器
  :param func: 被装饰的函数
  """
  def wrapper(*args, **kwargs):
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"\r总耗时: {elapsed_time:.2f}秒")
    return result
  return wrapper

def append_dict_to_json(path: str, record: dict) -> None:
  """
  讲一个字典 record 追加到 path 制定的 JSON 文件中的数组里
  如果文件不存在，则创建文件并写入包含 record 的数组
  """
  # 检查文件是否存在
  if os.path.exists(path):
    # 文件存在: 读取现有数据
    with open(path, "r", encoding = 'utf-8') as file:
      try:
        data = json.load(file) # 反序列化为 Python 对象
        if not isinstance(data, list):
          raise ValueError(f"预期 JSON 文件内容是数组，但得到 {type(data)}")
      except (json.JSONDecodeError, ValueError):
        # 当文件为空、格式错误或类型不匹配时，备份原文件后当作空列表处理
        backup_path = path + ".bak"
        shutil.copy(path, backup_path)
        print(f"⚠️ 原文件内容非法，已备份到 {backup_path}，将以空数组继续操作")
        data = []
  else:
    # 文件不存在: 初始化空列表
    data = []
  # 将新的字典追加到列表
  data.append(record)
  # 原子写入: 先写入临时文件，再替换
  dir_name = os.path.dirname(path) or "."
  fd, tmp_path = tempfile.mkstemp(dir = dir_name, prefix = ".tmp_", suffix = ".json")
  try:
    with os.fdopen(fd, "w", encoding = "utf-8") as tmp_file:
      json.dump(data, tmp_file, ensure_ascii = False, indent = 4)
      tmp_file.flush()
      os.fsync(tmp_file.fileno()) # 确保写入磁盘
    # 用原子替换的方法将临时文件移动到目标路径
    os.replace(tmp_path, path)
  except Exception:
    # 若写入或替换发生异常，删除临时文件以免残留
    os.remove(tmp_path)
    raise
  else:
    print(f"✅ 已安全将记录追加并写入 {path}")

def main():
  print("utils.py程序已执行")

if __name__ == "__main__":
  main()

