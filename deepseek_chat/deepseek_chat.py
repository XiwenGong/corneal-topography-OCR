import tkinter as tk
from tkinter import scrolledtext, ttk
import requests
import json
import os
from dotenv import load_dotenv
import threading

class DeepSeekChat:
    """
    DeepSeek聊天应用的主类
    提供GUI界面和与DeepSeek API的交互功能
    """
    def __init__(self, root):
        """
        初始化聊天应用
        
        @param {tk.Tk} root - tkinter根窗口
        """
        self.root = root
        self.root.title("DeepSeek 聊天")
        self.root.geometry("800x600")
        
        # 加载环境变量
        load_dotenv()
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("请在.env文件中设置DEEPSEEK_API_KEY")
            
        self.setup_ui()
        
    def setup_ui(self):
        """
        设置用户界面组件
        """
        # 创建聊天显示区域
        self.chat_display = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=20)
        self.chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # 创建输入框和发送按钮的容器
        input_frame = ttk.Frame(self.root)
        input_frame.pack(padx=10, pady=5, fill=tk.X)
        
        # 创建输入框
        self.input_field = ttk.Entry(input_frame)
        self.input_field.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.input_field.bind("<Return>", self.send_message)
        
        # 创建发送按钮
        send_button = ttk.Button(input_frame, text="发送", command=self.send_message)
        send_button.pack(side=tk.RIGHT, padx=5)
        
        # 创建状态标签
        self.status_label = ttk.Label(self.root, text="就绪")
        self.status_label.pack(pady=5)
        
    def send_message(self, event=None):
        """
        发送消息到DeepSeek API并显示响应
        
        @param {Event} event - 触发事件（可选）
        """
        message = self.input_field.get().strip()
        if not message:
            return
            
        # 清空输入框
        self.input_field.delete(0, tk.END)
        
        # 显示用户消息
        self.chat_display.insert(tk.END, f"你: {message}\n")
        self.chat_display.see(tk.END)
        
        # 在新线程中发送请求
        threading.Thread(target=self.get_ai_response, args=(message,), daemon=True).start()
        
    def get_ai_response(self, message):
        """
        从DeepSeek API获取响应
        
        @param {str} message - 用户输入的消息
        """
        self.status_label.config(text="正在获取响应...")
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": message}]
            }
            
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                ai_response = response.json()["choices"][0]["message"]["content"]
                self.root.after(0, self.display_ai_response, ai_response)
            else:
                error_msg = f"错误: API返回状态码 {response.status_code}"
                self.root.after(0, self.display_ai_response, error_msg)
                
        except Exception as e:
            error_msg = f"错误: {str(e)}"
            self.root.after(0, self.display_ai_response, error_msg)
            
        finally:
            self.root.after(0, lambda: self.status_label.config(text="就绪"))
            
    def display_ai_response(self, response):
        """
        在聊天显示区域显示AI的响应
        
        @param {str} response - AI的响应文本
        """
        self.chat_display.insert(tk.END, f"DeepSeek: {response}\n\n")
        self.chat_display.see(tk.END)

def main():
    """
    主函数，创建并运行应用
    """
    root = tk.Tk()
    app = DeepSeekChat(root)
    root.mainloop()

if __name__ == "__main__":
    main() 