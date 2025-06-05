import pickle
import os
from datetime import datetime
from typing import Any, Dict, Optional

class DataManager:
    """
    数据管理器类，用于管理多个脚本的数据存储
    使用别名作为主要键，每个别名下可以存储来自不同脚本的数据
    """
    def __init__(self, pkl_file: str = "shared_data.pkl"):
        """
        初始化数据管理器
        Args:
            pkl_file: pkl文件路径，默认为shared_data.pkl
        """
        self.pkl_file = pkl_file
        self.data = self._load_data()

    def _load_data(self) -> Dict[str, Any]:
        """
        加载pkl文件中的数据
        Returns:
            Dict: 包含所有数据的字典
        """
        if os.path.exists(self.pkl_file):
            try:
                with open(self.pkl_file, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                print(f"加载数据时出错：{str(e)}")
                return {}
        return {}

    def has_alias(self, alias: str) -> bool:
        """
        检查别名是否已存在
        Args:
            alias: 要检查的别名
        Returns:
            bool: 别名是否存在
        """
        return alias in self.data

    def save_data(self, alias: str, script_name: str, data: dict) -> bool:
        """
        保存数据到pkl文件，内容为字典结构
        Args:
            alias: 数据别名，作为主要键
            script_name: 脚本名称，用于区分不同脚本的数据
            data: 要保存的数据（dict类型）
        Returns:
            bool: 是否保存成功
        """
        try:
            if alias not in self.data:
                self.data[alias] = {}
            save_dict = data.copy()
            save_dict['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.data[alias][script_name] = save_dict
            with open(self.pkl_file, 'wb') as f:
                pickle.dump(self.data, f)
            return True
        except Exception as e:
            print(f"保存数据时出错：{str(e)}")
            return False

    def get_data(self, alias: str, script_name: Optional[str] = None) -> Any:
        """
        获取指定别名的数据
        Args:
            alias: 数据别名
            script_name: 脚本名称，如果不提供则返回该别名下的所有数据
        Returns:
            Any: 请求的数据
        """
        if alias not in self.data:
            return None
        
        if script_name is None:
            return self.data[alias]
        
        return self.data[alias].get(script_name)

    def list_aliases(self) -> list:
        """
        列出所有已保存数据的别名
        Returns:
            list: 别名列表
        """
        return list(self.data.keys())

    def list_scripts(self, alias: str) -> list:
        """
        列出指定别名下的所有脚本名称
        Args:
            alias: 数据别名
        Returns:
            list: 脚本名称列表
        """
        if alias not in self.data:
            return []
        return list(self.data[alias].keys())

    def remove_data(self, alias: str, script_name: Optional[str] = None) -> bool:
        """
        删除指定别名的数据
        Args:
            alias: 数据别名
            script_name: 脚本名称，如果不提供则删除该别名的所有数据
        Returns:
            bool: 是否删除成功
        """
        try:
            if alias not in self.data:
                return False
            
            if script_name is None:
                del self.data[alias]
            else:
                if script_name in self.data[alias]:
                    del self.data[alias][script_name]
                else:
                    return False
            
            with open(self.pkl_file, 'wb') as f:
                pickle.dump(self.data, f)
            return True
        except Exception as e:
            print(f"删除数据时出错：{str(e)}")
            return False

    def set_global_data(self, key: str, value: any) -> bool:
        """
        设置全局（通用）数据
        Args:
            key: 全局数据的键
            value: 全局数据的值
        Returns:
            bool: 是否设置成功
        """
        try:
            if "__global__" not in self.data:
                self.data["__global__"] = {}
            self.data["__global__"][key] = value
            with open(self.pkl_file, 'wb') as f:
                pickle.dump(self.data, f)
            return True
        except Exception as e:
            print(f"设置全局数据时出错：{str(e)}")
            return False

    def get_global_data(self, key: str) -> any:
        """
        获取全局（通用）数据
        Args:
            key: 全局数据的键
        Returns:
            any: 全局数据的值
        """
        return self.data.get("__global__", {}).get(key) 