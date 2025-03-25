import os
import time
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv
import sys

def main():
    # 打印当前工作目录
    print(f"当前工作目录: {os.getcwd()}")
    
    # 查看.env文件是否存在
    env_path = os.path.join(os.getcwd(), '.env')
    print(f".env文件路径: {env_path}")
    print(f".env文件存在: {os.path.exists(env_path)}")
    
    # 加载环境变量
    load_dotenv(dotenv_path=env_path, override=True)
    
    # 获取Azure语音服务密钥和区域
    speech_key = os.environ.get('AZURE_SPEECH_KEY')
    speech_region = os.environ.get('AZURE_SPEECH_REGION')
    
    # 打印环境变量值（隐藏密钥的一部分）
    if speech_key:
        masked_key = speech_key[:4] + '*' * (len(speech_key) - 8) + speech_key[-4:]
        print(f"Azure语音服务密钥: {masked_key}")
    else:
        print("Azure语音服务密钥未设置")
    
    print(f"Azure语音服务区域: {speech_region}")
    
    if not speech_key or not speech_region:
        print("错误：请在.env文件中设置AZURE_SPEECH_KEY和AZURE_SPEECH_REGION")
        return
    
    if speech_region == "your_azure_region_here":
        print("错误：请将.env文件中的AZURE_SPEECH_REGION替换为实际的区域名称")
        return
    
    # 创建语音配置
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
    speech_config.speech_recognition_language = "zh-CN"  # 设置中文识别
    
    # 打印完整的配置信息
    print(f"语音识别语言: {speech_config.speech_recognition_language}")
    print(f"使用的区域: {speech_region}")
    
    # 使用默认麦克风 (这种方式不需要PyAudio)
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    
    # 创建语音识别器
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    
    print("开始语音识别（中文）")
    print("请对着麦克风说话...")
    print("按Ctrl+C退出程序")
    
    # 使用单次识别，而不是连续识别模式
    try:
        while True:
            print("\n正在听取语音...")
            result = speech_recognizer.recognize_once()
            
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                print(f"识别结果: {result.text}")
            elif result.reason == speechsdk.ResultReason.NoMatch:
                print("没有识别到语音")
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation = speechsdk.CancellationDetails(result)
                print(f"识别被取消: {cancellation.reason}")
                if cancellation.reason == speechsdk.CancellationReason.Error:
                    print(f"错误详情: {cancellation.error_details}")
                    # 打印更多错误信息
                    print(f"完整错误信息: {cancellation.error_details}")
            
            # 短暂暂停，避免CPU使用率过高
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n停止语音识别...")
    except Exception as e:
        print(f"发生未预期的错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 