import os
import json

class History_Record:
  def __init__ (self, file_path: str):
    self.file_path = file_path
    if not os.path.exists(file_path):
      with open(self.file_path, "w", encoding = "utf-8") as file:
        json.dump({}, file)
  
  def _read_file(self) -> dict:
    """读取 JSON 文件内容并返回为字典"""
    with open(self.file_path, "r", encoding = "utf-8") as file:
      return json.load(file)
  
  def _write_file(self, data: dict) -> None:
    """将字典写入 JSON 文件"""
    with open(self.file_path, "w", encoding = "utf-8") as file:
      json.dump(data, file, intent = 4)
  
  def add_record(self, key: str, value: dict) -> None:
    """
    添加一条记录
    """
    data = self._read_file()
    if key in data:
      raise KeyError(f"记录 {key} 已存在")
    data[key] = value
    self._write_file(data)
  
  def update_record(self, key: str, value: dict) -> None:
    """更新一条记录"""
    data = self._read_file()
    if key not in data:
      raise KeyError(f"记录 {key} 不存在")
    data[key] = value
    self._write_file(data)
  
  def delete_record(self, key: str) -> None:
    """删除一条记录"""
    data = self._read_file()
    if key not in data:
      raise KeyError(f"记录 {key} 不存在")
    del data[key]
    self._write_file(data)
  
  def get_record(self, key: str) -> dict:
    """获取一条记录"""
    data = self._read_file()
    if key not in data:
      raise KeyError(f"记录 {key} 不存在")
    return data[key]
  
  def list_records(self) -> dict:
    """列出所有记录"""
    return self._read_file()