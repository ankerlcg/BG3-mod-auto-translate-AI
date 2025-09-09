import json
import os
from openai import OpenAI
import xml.etree.ElementTree as ET
import concurrent.futures
import logging
import sys
from tqdm import tqdm
import colorama
import pendulum
from pyefun import *
import sys
import clr
from tkinter import Tk, filedialog
# Initialize colorama to make ANSI color codes work on Windows
colorama.init(autoreset=True)

def select_pak_file():
    """Opens a file dialog to select a .pak file."""
    root = Tk()
    root.withdraw()  # Hide the main window
    root.attributes('-topmost', True)  # Make the dialog always on top
    file_path = filedialog.askopenfilename(
        title="请选择一个您要进行汉化的mod的pak文件",
        filetypes=[("博德之门Mod文件", "*.pak")]
    )
    root.destroy()
    return file_path


# --- Logger Setup ---
class ColoredFormatter(logging.Formatter):
    """A custom log formatter that adds colors to log messages."""
    COLORS = {
        'WARNING': colorama.Fore.YELLOW,
        'INFO': colorama.Fore.GREEN,
        'DEBUG': colorama.Fore.BLUE,
        'CRITICAL': colorama.Fore.RED,
        'ERROR': colorama.Fore.RED,
    }

    def format(self, record):
        color = self.COLORS.get(record.levelname, '')
        log_message = super().format(record)
        return f"{color}{log_message}"


# Configure logger
logger = logging.getLogger('XML_Translator')
logger.setLevel(logging.INFO)
logger.propagate = False

if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    formatter = ColoredFormatter('%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)



# AI翻译函数
def translate(msg):
    if not client:
        logger.critical("API client is not initialized. Cannot translate.")
        return msg
    if not msg or not msg.strip():
        return msg
    try:
        # noinspection PyTypeChecker
        response = client.chat.completions.create(
            model=config['model'],
            messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": msg},
                    ],
                }
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"调用AI翻译错误 '{msg}': {e}")
        return msg

def process_xml(input_file, output_file):
    """
    Parses an XML file, translates the content of 'content' tags using multiple threads,
    and writes the result to a new XML file, showing a progress bar.
    """
    try:
        tree = ET.parse(input_file)
        root = tree.getroot()
        content_elements = root.findall('.//content')

        future_to_element = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            for element in content_elements:
                if element.text and element.text.strip():


                    msg = config['prompt'].replace("{msg}", element.text)
                    future = executor.submit(translate,msg)
                    future_to_element[future] = element

            for future in tqdm(concurrent.futures.as_completed(future_to_element), total=len(future_to_element),
                               desc="Translating"):
                element = future_to_element[future]
                try:
                    translated_text = future.result()
                    if translated_text != element.text:
                        logger.info(f"UID{element.attrib.get('contentuid', 'N/A')},正在翻译")

                        logger.info(f" {element.text} ---->>>>> {translated_text}")
                        element.text = translated_text
                except Exception as exc:
                    logger.error(f"Element UID {element.attrib.get('contentuid', 'N/A')} generated an exception: {exc}")
                    logger.error(f"Original Text: {element.text}")
                    logger.error(f"Translated Text: 翻译错误！！！")
        tree.write(output_file, encoding='utf-8', xml_declaration=True)
        logger.info(f"已完成全部文本的翻译, 请选择Mod的保存位置:")
    except ET.ParseError as e:
        logger.error(f"Error parsing the XML file: {e}")
    except FileNotFoundError:
        logger.error(f"Error: Input file not found at {input_file}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
# --- Package Functions ---
def cratePackage(packageDataPath,outputPath):
    try:
        clr.AddReference(f'unBG3Pack')
    except Exception as e:
        logger.error(f"载入关键DLL失败, {e}")
        logger.error("请检查您是否成功安装了.Net 4.x 运行库之后重新运行本程序")
        logger.error("请按任意键退出本程序")
        sys.exit(1)
    try:
        from BG3Pack import PackageManage
        PackageManage.CreatePackage(packageDataPath, outputPath)
    except ImportError as e:
        logger.error(f"Failed to import from DLL. Check namespace and class names: {e}")
        logger.error("请按任意键退出本程序")
        sys.exit(1)

    except Exception as e:
        logger.error(f"Error initializing PackageManage: {e}")
        logger.error("请按任意键退出本程序")
        sys.exit(1)

def unpackMod(modPath,outputPath):
    # 解包Mod
    try:
        clr.AddReference(f'unBG3Pack')
    except Exception as e:
        logger.error(f"载入关键DLL失败, {e}")
        logger.error("请检查您是否成功安装了.Net 4.x 运行库之后重新运行本程序")
        logger.error("请按任意键退出本程序")
        sys.exit(1)
    try:
        from BG3Pack import PackageManage
        PackageManage.UnPackageFile(modPath, outputPath)
    except ImportError as e:
        logger.error(f"Failed to import from DLL. Check namespace and class names: {e}")
        logger.error("请按任意键退出本程序")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error initializing PackageManage: {e}")
        logger.error("请按任意键退出本程序")
        sys.exit(1)

def select_save_pak_file(default_name=""):
    """Opens a file dialog to select a save location for a .pak file."""
    root = Tk()
    root.withdraw()  # Hide the main window
    root.attributes('-topmost', True)  # Make the dialog always on top

    file_path = filedialog.asksaveasfilename(
        title="将汉化后的Mod保存为一个新的pak文件",
        initialfile=default_name,
        defaultextension=".pak",
        filetypes=[("PAK 文件", "*.pak")]
    )
    root.destroy()
    return file_path


#删除指定目录
def delete_directory(dir_path):
    """Deletes the specified directory and all its contents."""
    if os.path.exists(dir_path):
        try:
            shutil.rmtree(dir_path)
            logger.info(f"Successfully deleted directory: {dir_path}")
        except Exception as e:
            logger.error(f"Error deleting directory {dir_path}: {e}")
    else:
        logger.warning(f"Directory not found, skipping deletion: {dir_path}")


if __name__ == "__main__":
    # 初始化配置文件
    try:
        config = json.loads(读入文本(f"{取运行目录()}\\config.ini"))
    except Exception as e:
        logger.error(f"初始化配置失败,请检查配置文件config.ini是否存在且格式正确,错误信息:{e}")
        logger.error("请按任意键退出本程序")
        input()
        sys.exit(1)
    try:
        dll_folder_path = f"{取运行目录()}\\C#\\"
        sys.path.append(dll_folder_path)
    except Exception as e:
        logger.error(f"载入关键DLL失败, {e}")
        logger.error("请检查您是否成功安装了.Net 4.x 运行库之后重新运行本程序")
        logger.info("请按任意键退出本程序")
        sys.exit(1)
    try:
        logger.info('欢迎使用博德之门AI一键汉化Mod工具,本程序由 无阻 制作')
        logger.info(f'加载关键DLL,{取运行目录()}\\C#\\unBG3Pack.dll')
        clr.AddReference(f'unBG3Pack')
    except Exception as e:
        logger.error(f"载入关键DLL失败, {e}")
        logger.error("请检查您是否成功安装了.Net 4.x 运行库之后重新运行本程序")
        logger.error("请按任意键退出本程序")
        sys.exit(1)
    try:
        from BG3Pack import PackageManage
    except ImportError as e:
        logger.error(f"导入关键DLL失败, 错误信息: {e}")
        logger.error(f"Failed to import from DLL. Check namespace and class names: {e}")
        logger.error("请按任意键退出本程序")
        sys.exit(1)
    api_key = config['api_key']
    if api_key == "":
        logger.error("检测到你输入的ApiKey为空,请前往各大AI开发者中心申请ApiKey后重新运行本程序")
        logger.info("请按任意键退出本程序")
        input()
        sys.exit(1)
    logger.info("当前使用AI模型:" + config['model'])
    logger.info("正在初始化API client...")
    # 初始化AI
    client = OpenAI(
        # 此为默认路径，您可根据业务所在地域进行配置
        base_url=config['base_url'],
        # 从环境变量中获取您的 API Key。此为默认方式，您可根据需要进行修改
        api_key=api_key,
    )
    logger.info("API client initialized successfully.")
    logger.info("请选择需要汉化的Mod文件.")
    try:
        pak_file_path = select_pak_file()
        if pak_file_path:
            logger.info(f"已选择文件: {pak_file_path}")
        else:
            logger.info("未选择文件.")
            logger.error("请按任意键退出本程序")
            sys.exit(1)
        # 获取mod文件名
        modFileName = 文件_取文件名(pak_file_path,False)
        try:
            delete_directory(f"{取运行目录()}\\mod-unpackage")
            创建目录(f"{取运行目录()}\\mod-unpackage\\{modFileName}")
        except:
            pass
        # 解包指定mod
        unpackMod(modPath=pak_file_path,outputPath=f"{取运行目录()}\\mod-unpackage\\{modFileName}")
        logger.info(f"正在处理汉化mod:{modFileName}.")
        # 枚举解包出来的mod目录
        modList = 目录_枚举(f"{取运行目录()}\\mod-unpackage\\{modFileName}\\Mods",False)
        for mod in modList:
            logger.info(f"Found mod: {mod}")
            if 文件是否存在(f"{mod}/Localization/English/english.xml"):
                input_path = f"{mod}/Localization/English/english.xml"
                创建目录(f"{mod}/Localization/Chinese")
                output_path = f"{mod}/Localization/Chinese/chinese.xml"
                process_xml(input_path, output_path)
            else:
                logger.error(f"Error: {mod} 未找到需要翻译的 english.xml 文件，请将程序放在正确的目录下运行。")

        try:
            # 选择汉化后的Mod保存位置
            outputPath = select_save_pak_file(default_name=f"{modFileName}-CHS.pak")
            while not outputPath:
                logger.error("保存文件路径不能为空.")
                outputPath = select_save_pak_file(default_name=f"{modFileName}-CHS.pak")

            # 打包汉化后的mod
            cratePackage(f"{取运行目录()}\\mod-unpackage\\{modFileName}",outputPath)
        except Exception as e:
            logger.error(f"汉化文件打包时出错: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
    logger.info("所有操作完成，按任意键退出本程序...")
    input()
