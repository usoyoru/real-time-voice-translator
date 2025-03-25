import os
import time
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import azure.cognitiveservices.speech as speechsdk
import requests
import uuid
import json
from dotenv import load_dotenv

class VoiceTranslateTTSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("中文语音识别、翻译与朗读")
        self.root.geometry("700x500")
        self.root.resizable(True, True)
        
        # 加载环境变量
        load_dotenv()
        
        # 获取Azure语音服务密钥和区域
        self.speech_key = os.environ.get('AZURE_SPEECH_KEY')
        self.speech_region = os.environ.get('AZURE_SPEECH_REGION')
        
        # 获取Azure翻译服务密钥和端点
        self.translator_key = os.environ.get('AZURE_TRANSLATOR_KEY')
        self.translator_endpoint = os.environ.get('AZURE_TRANSLATOR_ENDPOINT')
        
        # 检查环境变量是否正确设置
        if not self.speech_key or not self.speech_region:
            error_msg = "请在.env文件中设置AZURE_SPEECH_KEY和AZURE_SPEECH_REGION"
            messagebox.showerror("错误", error_msg)
            root.destroy()
            return
        
        if not self.translator_key or not self.translator_endpoint:
            error_msg = "请在.env文件中设置AZURE_TRANSLATOR_KEY和AZURE_TRANSLATOR_ENDPOINT"
            messagebox.showerror("错误", error_msg)
            root.destroy()
            return
        
        if self.speech_region == "your_azure_region_here":
            error_msg = "请将.env文件中的AZURE_SPEECH_REGION替换为实际的区域名称"
            messagebox.showerror("错误", error_msg)
            root.destroy()
            return
        
        # 创建语音配置
        self.speech_config = speechsdk.SpeechConfig(subscription=self.speech_key, region=self.speech_region)
        self.speech_config.speech_recognition_language = "zh-CN"  # 设置中文识别
        
        # 创建文本转语音配置
        self.tts_config = speechsdk.SpeechConfig(subscription=self.speech_key, region=self.speech_region)
        self.tts_config.speech_synthesis_language = "en-US"
        self.tts_config.speech_synthesis_voice_name = "en-US-JennyNeural"
        
        # 创建从默认麦克风获取音频的配置
        self.audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        
        # 创建语音识别器
        try:
            self.speech_recognizer = speechsdk.SpeechRecognizer(
                speech_config=self.speech_config, 
                audio_config=self.audio_config
            )
            
            # 创建语音合成器
            self.speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.tts_config)
            
        except Exception as e:
            error_msg = f"创建语音服务失败: {e}"
            messagebox.showerror("错误", error_msg)
            root.destroy()
            return
        
        # 识别状态
        self.is_recognizing = False
        self.recognition_thread = None
        self.is_speaking = False
        
        # 创建GUI元素
        self.create_widgets()
    
    def create_widgets(self):
        # 顶部状态标签
        self.status_label = tk.Label(self.root, text="准备就绪", font=("SimHei", 12))
        self.status_label.pack(pady=10)
        
        # 主框架
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 文本区域框架
        text_frame = tk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        # 中文文本区域
        chinese_frame = tk.LabelFrame(text_frame, text="中文识别结果", font=("SimHei", 10))
        chinese_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.chinese_text = scrolledtext.ScrolledText(chinese_frame, wrap=tk.WORD, width=30, height=15, font=("SimHei", 12))
        self.chinese_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 英文文本区域
        english_frame = tk.LabelFrame(text_frame, text="英文翻译结果", font=("SimHei", 10))
        english_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.english_text = scrolledtext.ScrolledText(english_frame, wrap=tk.WORD, width=30, height=15, font=("SimHei", 12))
        self.english_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 按钮区域
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        self.start_button = tk.Button(button_frame, text="开始识别", command=self.start_recognition, bg="#4CAF50", fg="white", font=("SimHei", 12), width=10)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = tk.Button(button_frame, text="停止识别", command=self.stop_recognition, bg="#F44336", fg="white", font=("SimHei", 12), width=10, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = tk.Button(button_frame, text="清空文本", command=self.clear_text, bg="#2196F3", fg="white", font=("SimHei", 12), width=10)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        self.speak_button = tk.Button(button_frame, text="朗读英文", command=self.speak_last_translation, bg="#FF9800", fg="white", font=("SimHei", 12), width=10)
        self.speak_button.pack(side=tk.LEFT, padx=5)
        
        # 选择语音下拉框
        voice_frame = tk.Frame(self.root)
        voice_frame.pack(pady=5)
        
        tk.Label(voice_frame, text="选择语音:", font=("SimHei", 10)).pack(side=tk.LEFT, padx=5)
        
        self.voice_var = tk.StringVar(value="en-US-JennyNeural")
        voice_options = [
            "en-US-JennyNeural",  # 女声
            "en-US-GuyNeural",    # 男声
            "en-US-AriaNeural",   # 女声
            "en-GB-SoniaNeural"   # 英式女声
        ]
        
        self.voice_dropdown = ttk.Combobox(voice_frame, textvariable=self.voice_var, values=voice_options, width=20)
        self.voice_dropdown.pack(side=tk.LEFT, padx=5)
        self.voice_dropdown.bind("<<ComboboxSelected>>", self.on_voice_change)
        
        # 底部状态栏
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.root, orient=tk.HORIZONTAL, length=300, mode='indeterminate', variable=self.progress_var)
        self.progress_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        
        # 底部版权信息
        footer_label = tk.Label(self.root, text="基于Azure语音服务和翻译服务开发", font=("SimHei", 8))
        footer_label.pack(side=tk.BOTTOM, pady=2)
    
    def on_voice_change(self, event):
        """更新选择的语音"""
        selected_voice = self.voice_var.get()
        self.tts_config.speech_synthesis_voice_name = selected_voice
        language_code = selected_voice.split("-")[0] + "-" + selected_voice.split("-")[1]
        self.tts_config.speech_synthesis_language = language_code
        self.update_status(f"已选择语音: {selected_voice}", "#000000")
    
    def append_chinese_text(self, text):
        """向中文文本区域追加文本"""
        self.chinese_text.insert(tk.END, text + "\n")
        self.chinese_text.see(tk.END)  # 滚动到底部
    
    def append_english_text(self, text):
        """向英文文本区域追加文本"""
        self.english_text.insert(tk.END, text + "\n")
        self.english_text.see(tk.END)  # 滚动到底部
        # 存储最新的翻译文本
        self.last_translation = text
    
    def translate_text(self, text, source_language="zh-Hans", target_language="en"):
        """使用Azure翻译服务将文本从源语言翻译为目标语言"""
        # 配置API请求
        path = '/translate'
        constructed_url = self.translator_endpoint + path
        
        params = {
            'api-version': '3.0',
            'from': source_language,
            'to': target_language
        }
        
        headers = {
            'Ocp-Apim-Subscription-Key': self.translator_key,
            'Ocp-Apim-Subscription-Region': self.speech_region,
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }
        
        # 准备要翻译的文本
        body = [{
            'text': text
        }]
        
        # 发送请求
        try:
            response = requests.post(constructed_url, params=params, headers=headers, json=body)
            response.raise_for_status()  # 如果请求失败，抛出异常
            
            # 解析响应
            result = response.json()
            
            if result and len(result) > 0 and 'translations' in result[0] and len(result[0]['translations']) > 0:
                translated_text = result[0]['translations'][0]['text']
                # 存储最新的翻译，用于朗读按钮
                self.last_translation = translated_text
                return translated_text
            else:
                self.update_status("翻译结果格式不正确", "red")
                return None
        
        except Exception as e:
            self.update_status(f"翻译错误: {e}", "red")
            return None
    
    def text_to_speech(self, text):
        """将文本转换为语音"""
        if not text:
            self.update_status("没有文本可以朗读", "#FF9800")
            return False
        
        try:
            self.is_speaking = True
            self.update_status("正在朗读...", "#4CAF50")
            
            # 执行文本转语音
            result = self.speech_synthesizer.speak_text_async(text).get()
            
            # 检查结果
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                self.update_status("朗读完成", "#4CAF50")
                return True
            else:
                self.update_status(f"朗读失败: {result.reason}", "red")
                if result.reason == speechsdk.ResultReason.Canceled:
                    cancellation = speechsdk.SpeechSynthesisCancellationDetails(result)
                    self.update_status(f"朗读取消: {cancellation.reason}", "red")
                return False
        
        except Exception as e:
            self.update_status(f"朗读错误: {e}", "red")
            return False
        finally:
            self.is_speaking = False
    
    def speak_last_translation(self):
        """朗读最后一次翻译的文本"""
        if hasattr(self, 'last_translation') and self.last_translation:
            # 在新线程中执行，避免阻塞UI
            threading.Thread(target=self.text_to_speech, args=(self.last_translation,), daemon=True).start()
        else:
            self.update_status("没有可朗读的翻译", "#FF9800")
    
    def recognition_loop(self):
        """识别循环，在独立线程中运行"""
        while self.is_recognizing:
            try:
                # 更新状态
                self.update_status("正在听取语音...", "#4CAF50")
                
                # 单次识别
                result = self.speech_recognizer.recognize_once()
                
                if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                    chinese_text = result.text
                    
                    # 更新中文文本
                    self.root.after(0, lambda text=chinese_text: self.append_chinese_text(text))
                    
                    # 更新状态
                    self.update_status("正在翻译...", "#FF9800")
                    self.root.after(0, lambda: self.progress_bar.start(10))
                    
                    # 翻译成英文
                    english_text = self.translate_text(chinese_text)
                    
                    # 停止进度条
                    self.root.after(0, lambda: self.progress_bar.stop())
                    
                    if english_text:
                        # 更新英文文本
                        self.root.after(0, lambda text=english_text: self.append_english_text(text))
                        self.update_status("翻译成功", "#4CAF50")
                        
                        # 自动朗读翻译结果
                        if not self.is_speaking:
                            threading.Thread(target=self.text_to_speech, args=(english_text,), daemon=True).start()
                    else:
                        self.update_status("翻译失败", "red")
                
                elif result.reason == speechsdk.ResultReason.NoMatch:
                    self.update_status("没有识别到语音", "#FF9800")
                
                elif result.reason == speechsdk.ResultReason.Canceled:
                    cancellation = speechsdk.CancellationDetails(result)
                    error_message = f"识别被取消: {cancellation.reason}"
                    if cancellation.reason == speechsdk.CancellationReason.Error:
                        error_message += f"\n错误详情: {cancellation.error_details}"
                    self.update_status(error_message, "red")
                    
                    # 暂停一下再继续
                    time.sleep(2)
            
            except Exception as e:
                self.update_status(f"识别过程中发生错误: {e}", "red")
                time.sleep(2)
            
            # 短暂暂停，避免CPU使用率过高
            if self.is_recognizing:  # 再次检查，以便能够更快地退出线程
                time.sleep(0.1)
    
    def update_status(self, message, color="#000000"):
        """更新状态标签"""
        self.root.after(0, lambda: self.status_label.config(text=message, fg=color))
    
    def start_recognition(self):
        """开始语音识别"""
        if not self.is_recognizing:
            self.is_recognizing = True
            self.update_status("正在识别中...", "#4CAF50")
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            
            # 在新线程中启动识别循环
            self.recognition_thread = threading.Thread(target=self.recognition_loop, daemon=True)
            self.recognition_thread.start()
    
    def stop_recognition(self):
        """停止语音识别"""
        if self.is_recognizing:
            self.is_recognizing = False
            self.update_status("已停止", "#F44336")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.progress_bar.stop()
            
            # 线程会自行停止，因为我们设置了is_recognizing = False
    
    def clear_text(self):
        """清空文本区域"""
        self.chinese_text.delete(1.0, tk.END)
        self.english_text.delete(1.0, tk.END)
        self.update_status("准备就绪", "#000000")
        # 清除最后的翻译
        if hasattr(self, 'last_translation'):
            self.last_translation = None
    
    def on_closing(self):
        """关闭窗口时的操作"""
        if self.is_recognizing:
            self.stop_recognition()
        self.root.destroy()

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = VoiceTranslateTTSApp(root)
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        root.mainloop()
    except Exception as e:
        print(f"应用程序发生未预期的错误: {e}")
        import traceback
        traceback.print_exc() 