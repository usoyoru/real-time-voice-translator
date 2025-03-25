# 中文语音识别和翻译应用

一个简单的应用程序，可以实时将麦克风输入的中文语音转换为文字，并可以将识别的中文翻译成英文。

## 重要提示
**在使用前，必须先设置有效的Azure语音服务和翻译服务API密钥与区域**。未正确配置会导致应用程序无法连接到Azure服务。

## 功能
- 实时中文语音识别
- 中文到英文的实时翻译
- 提供命令行和图形用户界面两种使用方式
- 基于Azure语音服务和翻译服务，准确率高

## 安装步骤

1. 确保已安装Python 3.6或更高版本

2. 安装依赖库
   ```bash
   pip install -r requirements.txt
   ```

3. 获取Azure语音服务API密钥
   - 访问 [Azure门户](https://portal.azure.com/) 并登录
   - 创建语音服务资源（如果没有）：
     1. 点击"创建资源"
     2. 搜索"语音服务"
     3. 选择语音服务并点击"创建"
     4. 填写所需信息（订阅、资源组、区域等）
     5. 创建完成后，转到资源页面
   - 获取API密钥和区域信息：
     1. 在资源页面，点击左侧菜单的"密钥和终结点"
     2. 复制"密钥1"（或"密钥2"）和"区域"信息

4. 获取Azure翻译服务API密钥（可以尝试使用与语音服务相同的密钥）
   - 访问 [Azure门户](https://portal.azure.com/) 并登录
   - 创建翻译服务资源（如果没有）：
     1. 点击"创建资源"
     2. 搜索"Translator"
     3. 选择翻译服务并点击"创建"
     4. 填写所需信息
     5. 创建完成后，转到资源页面
   - 获取API密钥和区域信息：
     1. 在资源页面，点击左侧菜单的"密钥和终结点"
     2. 复制"密钥1"（或"密钥2"）和"终结点"信息

5. 配置API密钥
   - 在项目根目录下编辑`.env`文件
   - 将您的Azure语音服务和翻译服务密钥和区域填入相应位置：
     ```
     AZURE_SPEECH_KEY=your_azure_speech_key_here
     AZURE_SPEECH_REGION=your_azure_region_here
     AZURE_TRANSLATOR_KEY=your_azure_translator_key_here
     AZURE_TRANSLATOR_ENDPOINT=https://api.cognitive.microsofttranslator.com/
     ```
   - 注意：一定要用实际的密钥替换示例值

## 使用方法

### 语音识别（仅识别）

#### 命令行版本
```bash
python voice_recognition_mic_free.py
```
- 对着麦克风说话，识别结果将在控制台显示
- 每次说话后都会进行一次识别
- 按Ctrl+C退出程序

#### 图形界面版本
```bash
python voice_recognition_gui_mic_free.py
```
- 点击"开始识别"按钮开始语音识别
- 对着麦克风说话，识别结果将在文本区域显示
- 点击"停止识别"按钮停止识别
- 点击"清空文本"按钮清除已识别的文本

### 语音识别并翻译

#### 命令行版本
```bash
python voice_translate.py
```
- 对着麦克风说中文，程序将识别并翻译成英文
- 识别和翻译结果都会在控制台显示
- 按Ctrl+C退出程序

#### 图形界面版本
```bash
python voice_translate_gui.py
```
- 点击"开始识别"按钮开始语音识别和翻译
- 对着麦克风说中文，识别结果将在左侧文本区域显示，英文翻译将在右侧文本区域显示
- 点击"停止识别"按钮停止识别和翻译
- 点击"清空文本"按钮清除已识别和翻译的文本

## 解决PyAudio安装问题

如果你想使用原始版本（voice_recognition.py 和 voice_recognition_gui.py），你需要安装PyAudio。在Windows上安装PyAudio可能会遇到问题，可以尝试以下方法：

### 方法1：使用预编译的wheel文件
```bash
# 对于Python 3.11 64位
pip install https://download.lfd.uci.edu/pythonlibs/archived/PyAudio-0.2.11-cp311-cp311-win_amd64.whl

# 对于其他Python版本，请查找对应的wheel文件
```

### 方法2：安装必需的C++构建工具
1. 安装Visual C++ Build Tools
2. 然后再尝试安装PyAudio
```bash
pip install pyaudio
```

## 常见问题

### Connection failed (无法连接到远程主机)
- 错误信息: `Connection failed (no connection to the remote host)`
- 解决方法:
  1. 检查`.env`文件中的API密钥和区域是否正确填写，不要保留默认值
  2. 确保网络连接正常
  3. 检查Azure账户是否有效，服务是否可用

### 无法识别语音
- 确保麦克风正常工作并且已经正确连接
- 确保已授予应用使用麦克风的权限（在Windows设置中检查）
- 使用Windows声音设置测试麦克风

### 翻译错误
- 检查翻译服务的密钥和端点是否正确
- 确保网络连接正常
- 检查Azure翻译服务配额是否用尽

## 环境要求
- Python 3.6+
- Windows/macOS/Linux
- 麦克风设备
- 网络连接（用于连接Azure服务）
- 有效的Azure账户和服务订阅

## 注意事项
- 该应用使用的是付费的Azure服务，请注意服务使用量和费用
- 默认设置为中文识别和中译英，如需其他语言，请修改代码中的相应参数
- 免费层Azure服务有使用限制，查看Azure门户了解详情 