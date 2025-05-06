import itertools
import time
import threading
import os
import json
import shutil
import tempfile
from enum import Enum

ORANGE_DOT = "\033[38;2;245;148;37m●\033[0m"
GREEN_DOT =  "\033[38;2;37;245;58m●\033[0m"
RED_DOT = "\033[38;2;242;12;12m●\033[0m"
# ANSI 清行 \x1b[2K
CLEAN_SEQ = "\r\x1b[2K"

class Animation(Enum):
  dots = ([' ', '.', '..', '...'], 0.5) # 目前还有问题，一直是三个点，之前的动画帧没有被清除
  spin = (['-', '/', '|', '\\'], 0.15)
  
class RequestStatus(Enum):
  start = f"{ORANGE_DOT} 发起请求"
  in_progress = f"{ORANGE_DOT} 正在请求"
  completed = f"{GREEN_DOT} 请求完毕"
  failed = f"{RED_DOT} 请求失败"

animation_event = threading.Event()
request_done = threading.Event()
"""
对于动画线程有新的问题:
1. 发起请求时显示 "正在请求" 的加载动画
2. 当请求完成时，即主线程的 answer (非流式传输)变量被赋值时，加载动画线程应该停止
并且立即显示 "请求完毕" 的提示 
但是在主进程中，加载动画线程的状态是无法被直接访问的
【这是否意味着需要想办法先阻塞主进程代码的运行】
3. 对于流式传输，answer 变量一旦有了值，动画应该改变为 "正在流式传输" 的状态
"""
def loading_animation(animation_type: Enum = Animation.spin, isStream: bool = False):
  """
  动态加载动画，支持状态切换
  """
  frames, frame_rate = animation_type.value
  for frame in itertools.cycle(frames):
    if request_done.is_set():
      print(f"{CLEAN_SEQ}{RequestStatus.completed.value}", end = '', flush = True)
      break
    status = RequestStatus.in_progress.value if animation_event.is_set() else RequestStatus.start.value
    print(f"{CLEAN_SEQ}\r{status} {frame}", end = '', flush = True)
    time.sleep(frame_rate)

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

