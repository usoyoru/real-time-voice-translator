import os
import time
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv
import sys

class VoiceRecognitionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("中文语音识别")
        self.root.geometry("600x400")
        self.root.resizable(True, True)
        
        # 打印当前工作目录
        print(f"当前工作目录: {os.getcwd()}")
        
        # 查看.env文件是否存在
        env_path = os.path.join(os.getcwd(), '.env')
        print(f".env文件路径: {env_path}")
        print(f".env文件存在: {os.path.exists(env_path)}")
        
        # 加载环境变量
        load_dotenv(dotenv_path=env_path, override=True)
        
        # 获取Azure语音服务密钥和区域
        self.speech_key = os.environ.get('AZURE_SPEECH_KEY')
        self.speech_region = os.environ.get('AZURE_SPEECH_REGION')
        
        # 打印环境变量值（隐藏密钥的一部分）
        if self.speech_key:
            masked_key = self.speech_key[:4] + '*' * (len(self.speech_key) - 8) + self.speech_key[-4:]
            print(f"Azure语音服务密钥: {masked_key}")
        else:
            print("Azure语音服务密钥未设置")
        
        print(f"Azure语音服务区域: {self.speech_region}")
        
        # 检查环境变量是否正确设置
        if not self.speech_key or not self.speech_region:
            error_msg = "请在.env文件中设置AZURE_SPEECH_KEY和AZURE_SPEECH_REGION"
            print(f"错误：{error_msg}")
            messagebox.showerror("错误", error_msg)
            root.destroy()
            return
        
        if self.speech_region == "your_azure_region_here":
            error_msg = "请将.env文件中的AZURE_SPEECH_REGION替换为实际的区域名称"
            print(f"错误：{error_msg}")
            messagebox.showerror("错误", error_msg)
            root.destroy()
            return
        
        # 创建语音配置
        self.speech_config = speechsdk.SpeechConfig(subscription=self.speech_key, region=self.speech_region)
        self.speech_config.speech_recognition_language = "zh-CN"  # 设置中文识别
        
        # 打印配置信息
        print(f"语音识别语言: {self.speech_config.speech_recognition_language}")
        print(f"使用的区域: {self.speech_region}")
        
        # 创建从默认麦克风获取音频的配置
        self.audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        
        # 创建语音识别器
        try:
            self.speech_recognizer = speechsdk.SpeechRecognizer(
                speech_config=self.speech_config, 
                audio_config=self.audio_config
            )
            print("语音识别器创建成功")
        except Exception as e:
            error_msg = f"创建语音识别器失败: {e}"
            print(f"错误：{error_msg}")
            messagebox.showerror("错误", error_msg)
            root.destroy()
            return
        
        # 识别状态
        self.is_recognizing = False
        self.recognition_thread = None
        
        # 创建GUI元素
        self.create_widgets()
    
    def create_widgets(self):
        # 顶部状态标签
        self.status_label = tk.Label(self.root, text="准备就绪", font=("SimHei", 12))
        self.status_label.pack(pady=10)
        
        # 文本显示区域
        self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=60, height=15, font=("SimHei", 12))
        self.text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # 添加配置信息到文本区域
        self.text_area.insert(tk.END, f"Azure语音服务区域: {self.speech_region}\n")
        self.text_area.insert(tk.END, f"语音识别语言: {self.speech_config.speech_recognition_language}\n")
        self.text_area.insert(tk.END, "----------------------------\n")
        
        # 按钮区域
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        self.start_button = tk.Button(button_frame, text="开始识别", command=self.start_recognition, bg="#4CAF50", fg="white", font=("SimHei", 12), width=10)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = tk.Button(button_frame, text="停止识别", command=self.stop_recognition, bg="#F44336", fg="white", font=("SimHei", 12), width=10, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = tk.Button(button_frame, text="清空文本", command=self.clear_text, bg="#2196F3", fg="white", font=("SimHei", 12), width=10)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # 底部版权信息
        footer_label = tk.Label(self.root, text="基于Azure语音服务开发", font=("SimHei", 8))
        footer_label.pack(side=tk.BOTTOM, pady=5)
    
    def append_text(self, text):
        """向文本区域追加文本"""
        self.text_area.insert(tk.END, text + "\n")
        self.text_area.see(tk.END)  # 滚动到底部
    
    def recognition_loop(self):
        """识别循环，在独立线程中运行"""
        while self.is_recognizing:
            try:
                # 单次识别
                result = self.speech_recognizer.recognize_once()
                
                if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                    recognized_text = result.text
                    # 在主线程中更新UI
                    self.root.after(0, lambda text=recognized_text: self.append_text(text))
                elif result.reason == speechsdk.ResultReason.NoMatch:
                    self.root.after(0, lambda: self.status_label.config(text="没有识别到语音", fg="#FF9800"))
                elif result.reason == speechsdk.ResultReason.Canceled:
                    cancellation = speechsdk.CancellationDetails(result)
                    error_message = f"识别被取消: {cancellation.reason}"
                    if cancellation.reason == speechsdk.CancellationReason.Error:
                        error_message += f"\n错误详情: {cancellation.error_details}"
                    # 在主线程中更新UI
                    self.root.after(0, lambda msg=error_message: self.append_text(msg))
                    # 如果是错误，暂停一下再继续
                    if cancellation.reason == speechsdk.CancellationReason.Error:
                        time.sleep(2)
            except Exception as e:
                error_message = f"识别过程中发生错误: {e}"
                self.root.after(0, lambda msg=error_message: self.append_text(msg))
                time.sleep(2)
                
            # 短暂暂停，避免CPU使用率过高
            if self.is_recognizing:  # 再次检查，以便能够更快地退出线程
                time.sleep(0.1)
    
    def start_recognition(self):
        """开始语音识别"""
        if not self.is_recognizing:
            self.is_recognizing = True
            self.status_label.config(text="正在识别中...", fg="#4CAF50")
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            
            # 在新线程中启动识别循环
            self.recognition_thread = threading.Thread(target=self.recognition_loop, daemon=True)
            self.recognition_thread.start()
    
    def stop_recognition(self):
        """停止语音识别"""
        if self.is_recognizing:
            self.is_recognizing = False
            self.status_label.config(text="已停止", fg="#F44336")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            
            # 线程会自行停止，因为我们设置了is_recognizing = False
    
    def clear_text(self):
        """清空文本区域"""
        self.text_area.delete(1.0, tk.END)
        # 重新添加配置信息
        self.text_area.insert(tk.END, f"Azure语音服务区域: {self.speech_region}\n")
        self.text_area.insert(tk.END, f"语音识别语言: {self.speech_config.speech_recognition_language}\n")
        self.text_area.insert(tk.END, "----------------------------\n")
    
    def on_closing(self):
        """关闭窗口时的操作"""
        if self.is_recognizing:
            self.stop_recognition()
        self.root.destroy()

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = VoiceRecognitionApp(root)
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        root.mainloop()
    except Exception as e:
        print(f"应用程序发生未预期的错误: {e}")
        import traceback
        traceback.print_exc() 