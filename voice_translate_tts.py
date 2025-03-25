import os
import time
import requests
import uuid
import json
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

def translate_text(text, source_language="zh-Hans", target_language="en"):
    """使用Azure翻译服务将文本从源语言翻译为目标语言"""
    # 加载环境变量
    load_dotenv()
    
    # 获取Azure翻译服务密钥和端点
    translator_key = os.environ.get('AZURE_TRANSLATOR_KEY')
    translator_endpoint = os.environ.get('AZURE_TRANSLATOR_ENDPOINT')
    
    if not translator_key or not translator_endpoint:
        print("错误：请在.env文件中设置AZURE_TRANSLATOR_KEY和AZURE_TRANSLATOR_ENDPOINT")
        return None
    
    # 配置API请求
    path = '/translate'
    constructed_url = translator_endpoint + path
    
    params = {
        'api-version': '3.0',
        'from': source_language,
        'to': target_language
    }
    
    headers = {
        'Ocp-Apim-Subscription-Key': translator_key,
        'Ocp-Apim-Subscription-Region': os.environ.get('AZURE_SPEECH_REGION', 'eastus'),
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
            return translated_text
        else:
            print("翻译结果格式不正确")
            return None
    
    except Exception as e:
        print(f"翻译过程中发生错误: {e}")
        return None

def text_to_speech(text, language="en-US", voice_name="en-US-JennyNeural"):
    """使用Azure语音服务将文本转换为语音"""
    # 加载环境变量
    load_dotenv()
    
    # 获取Azure语音服务密钥和区域
    speech_key = os.environ.get('AZURE_SPEECH_KEY')
    speech_region = os.environ.get('AZURE_SPEECH_REGION')
    
    if not speech_key or not speech_region:
        print("错误：请在.env文件中设置AZURE_SPEECH_KEY和AZURE_SPEECH_REGION")
        return False
    
    # 创建语音配置
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
    
    # 设置语音合成的语言和声音
    speech_config.speech_synthesis_language = language
    speech_config.speech_synthesis_voice_name = voice_name
    
    # 创建语音合成器，使用默认扬声器作为音频输出
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
    
    try:
        # 进行语音合成
        print(f"正在将文本转换为语音: {text}")
        result = speech_synthesizer.speak_text_async(text).get()
        
        # 检查结果
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("语音合成成功")
            return True
        else:
            print(f"语音合成失败: {result.reason}")
            if result.reason == speechsdk.ResultReason.Canceled:
                cancellation = speechsdk.SpeechSynthesisCancellationDetails(result)
                print(f"语音合成被取消: {cancellation.reason}")
                print(f"错误详情: {cancellation.error_details}")
            return False
    
    except Exception as e:
        print(f"语音合成过程中发生错误: {e}")
        return False

def main():
    # 加载环境变量
    load_dotenv()
    
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
    
    # 使用默认麦克风
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    
    # 创建语音识别器
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    
    print("====== 中文语音识别、翻译和文本转语音 ======")
    print("对着麦克风说中文，程序将识别、翻译成英文并朗读")
    print("按Ctrl+C退出程序")
    
    # 使用单次识别，而不是连续识别模式
    try:
        while True:
            print("\n正在听取语音...")
            result = speech_recognizer.recognize_once()
            
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                chinese_text = result.text
                print(f"识别结果 (中文): {chinese_text}")
                
                # 翻译成英文
                print("正在翻译...")
                english_text = translate_text(chinese_text)
                
                if english_text:
                    print(f"翻译结果 (英文): {english_text}")
                    
                    # 将英文文本转换为语音
                    print("正在朗读...")
                    text_to_speech(english_text)
                else:
                    print("翻译失败")
                
            elif result.reason == speechsdk.ResultReason.NoMatch:
                print("没有识别到语音")
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation = speechsdk.CancellationDetails(result)
                print(f"识别被取消: {cancellation.reason}")
                if cancellation.reason == speechsdk.CancellationReason.Error:
                    print(f"错误详情: {cancellation.error_details}")
            
            # 短暂暂停，避免CPU使用率过高
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n停止程序...")
    except Exception as e:
        print(f"发生未预期的错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 