import itertools
import time
import threading
from enum import Enum

# 控制加载动画 全局事件
loading_event = threading.Event()

def loading_animation(message: str = "正在请求"):
  class Animation(Enum):
    dots = ['.', '..', '...']
    spin = ['-', '/', '|', '\\']
    
  for frame in itertools.cycle(Animation.spin.value):
    if not loading_event.is_set():
      print(f'\r{message} {frame}', end="", flush=True)
      time.sleep(0.5)
    else:
      break
  print('\r' + ' ' * (len(message) + 1), end="", flush=True) # 清除加载动画

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
    print(f"总耗时: {elapsed_time:.2f}秒")
    return result
  return wrapper