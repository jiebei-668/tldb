#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
铁路隐患审批自动化脚本
功能：自动登录、导航、批量审批日报
基于 Element UI 框架优化
"""

import time
import os
import configparser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class RailwayApprovalBot:
    def __init__(self, username="aaa", password="bbb", headless=False):
        """
        初始化机器人
        :param username: 用户名
        :param password: 密码
        :param headless: 是否无头模式
        """
        self.username = username
        self.password = password
        self.base_url = "http://sxstlhllfzhpt.cn/"

        # 配置Edge选项
        edge_options = Options()
        if headless:
            edge_options.add_argument('--headless')
        edge_options.add_argument('--no-sandbox')
        edge_options.add_argument('--disable-dev-shm-usage')
        edge_options.add_argument('--disable-blink-features=AutomationControlled')
        edge_options.add_argument('--window-size=1920,1080')

        # 初始化浏览器
        self.driver = webdriver.Edge(options=edge_options)
        self.wait = WebDriverWait(self.driver, 20)
        self.short_wait = WebDriverWait(self.driver, 5)

    def log(self, message):
        """打印日志"""
        print(f"[{time.strftime('%H:%M:%S')}] {message}")

    def switch_to_main_page(self):
        """切换回主页面（退出 frame）"""
        try:
            self.driver.switch_to.default_content()
            self.log("已切换回主页面")
        except Exception as e:
            self.log(f"切换回主页面时出错: {e}")

    def open_site(self):
        """打开网站"""
        self.log("正在打开网站...")
        self.driver.get(self.base_url)
        time.sleep(3)

        # 检查是否有 frame 并切换
        try:
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            frames = self.driver.find_elements(By.TAG_NAME, "frame")
            total_frames = len(iframes) + len(frames)

            if total_frames > 0:
                # 先尝试普通 frame
                for frame in frames:
                    try:
                        self.driver.switch_to.frame(frame)
                        time.sleep(2)
                        return
                    except:
                        continue

                # 如果普通 frame 失败，尝试 iframe
                for iframe in iframes:
                    try:
                        self.driver.switch_to.frame(iframe)
                        time.sleep(2)
                        return
                    except:
                        continue
        except Exception as e:
            self.log(f"处理 frame 时出错: {e}")

    def login(self):
        """登录 - Element UI"""
        self.log("开始登录流程...")
        time.sleep(2)

        # 查找用户名输入框
        username_input = None
        username_selectors = [
            (By.XPATH, "//input[@type='text' and contains(@class,'el-input__inner')]"),
            (By.XPATH, "(//input[@type='text'])[1]"),
            (By.XPATH, "//input[contains(@placeholder,'用户') or contains(@placeholder,'账号') or contains(@placeholder,'username')]"),
            (By.NAME, "username"),
            (By.NAME, "user"),
            (By.TAG_NAME, "input"),
        ]

        for selector_type, selector_value in username_selectors:
            try:
                username_input = self.short_wait.until(
                    EC.presence_of_element_located((selector_type, selector_value))
                )
                break
            except TimeoutException:
                continue

        if not username_input:
            raise Exception("无法找到用户名输入框")

        # 输入用户名
        username_input.clear()
        username_input.send_keys(self.username)

        # 查找密码输入框
        password_input = None
        password_selectors = [
            (By.XPATH, "//input[@type='password' and contains(@class,'el-input__inner')]"),
            (By.XPATH, "//input[@type='password']"),
            (By.NAME, "password"),
            (By.NAME, "pass"),
        ]

        for selector_type, selector_value in password_selectors:
            try:
                password_input = self.short_wait.until(
                    EC.presence_of_element_located((selector_type, selector_value))
                )
                break
            except TimeoutException:
                continue

        if not password_input:
            raise Exception("无法找到密码输入框")

        password_input.clear()
        password_input.send_keys(self.password)

        # 等待用户手动输入验证码
        self.log("=" * 50)
        self.log("请手动输入验证码，输入完成后按回车键继续...")
        self.show_verification_alert()
        input("按回车键继续...")
        self.hide_verification_alert()

        # 点击登录按钮
        login_button = None
        login_selectors = [
            (By.XPATH, "//button[contains(text(),'登 录')]"),
            (By.XPATH, "//button[normalize-space(text())='登录']"),
            (By.XPATH, "//button[contains(@class,'btn-block')]"),
            (By.CLASS_NAME, "btn-block"),
            (By.XPATH, "//button[contains(text(),'登')]"),
        ]

        for selector_type, selector_value in login_selectors:
            try:
                login_button = self.short_wait.until(
                    EC.element_to_be_clickable((selector_type, selector_value))
                )
                break
            except TimeoutException:
                continue

        if not login_button:
            raise Exception("无法找到登录按钮")

        login_button.click()
        self.log("登录请求已发送...")
        time.sleep(5)

    def show_verification_alert(self):
        """在页面显示验证码输入提示"""
        js_code = """
        var alertBox = document.createElement('div');
        alertBox.id = 'verification-alert';
        alertBox.style.cssText = 'position: fixed; top: 10px; left: 10px; z-index: 9999; background: #ff4444; color: white; padding: 40px; border-radius: 15px; font-size: 30px; font-weight: bold; box-shadow: 0 8px 24px rgba(0,0,0,0.3); max-width: 500px; font-family: Arial, sans-serif; line-height: 1.6;';
        alertBox.innerHTML = '⚠️ 重要提示<br><br>1. 手动输入验证码<br>2. 输入完成后回到黑框按回车<br>3. 不要点击登录按钮！';
        document.body.appendChild(alertBox);
        """
        self.driver.execute_script(js_code)

    def hide_verification_alert(self):
        """移除验证码输入提示"""
        self.driver.execute_script("var el = document.getElementById('verification-alert'); if (el) el.remove();")

    def click_menu(self, menu_name):
        """
        点击 Element UI 菜单项
        :param menu_name: 菜单名称
        """
        self.log(f"正在点击菜单: {menu_name}")

        # Element UI 菜单结构：可能是 span 或直接文本
        selectors = [
            # 尝试直接匹配文本的 span
            (By.XPATH, f"//span[contains(text(),'{menu_name}')]"),
            # 尝试包含文本的 li
            (By.XPATH, f"//li[contains(@class,'el-menu-item') and contains(text(),'{menu_name}')]"),
            # 尝试包含文本的 a 标签
            (By.XPATH, f"//a[contains(text(),'{menu_name}')]"),
            # 尝试子菜单标题
            (By.XPATH, f"//div[contains(@class,'el-submenu__title') and contains(text(),'{menu_name}')]"),
        ]

        for selector_type, selector_value in selectors:
            try:
                element = self.short_wait.until(
                    EC.element_to_be_clickable((selector_type, selector_value))
                )
                # 滚动到元素可见
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                time.sleep(0.5)
                element.click()
                time.sleep(1)
                self.log(f"成功点击: {menu_name}")
                return True
            except (TimeoutException, NoSuchElementException):
                continue

        self.log(f"警告：未找到菜单 '{menu_name}'")
        return False

    def click_submenu_item(self, item_name):
        """
        点击子菜单项（菜单展开后的选项）
        :param item_name: 菜单项名称
        """
        self.log(f"正在点击子菜单项: {item_name}")

        selectors = [
            # Element UI 子菜单项
            (By.XPATH, f"//li[contains(@class,'el-menu-item') and .//span[contains(text(),'{item_name}')]]"),
            (By.XPATH, f"//li[contains(@class,'el-menu-item') and contains(text(),'{item_name}')]"),
            (By.XPATH, f"//ul[contains(@class,'el-menu')]//span[contains(text(),'{item_name}')]"),
        ]

        for selector_type, selector_value in selectors:
            try:
                element = self.short_wait.until(
                    EC.element_to_be_clickable((selector_type, selector_value))
                )
                time.sleep(0.5)
                element.click()
                time.sleep(1)
                self.log(f"成功点击子菜单: {item_name}")
                return True
            except (TimeoutException, NoSuchElementException):
                continue

        self.log(f"警告：未找到子菜单项 '{item_name}'")
        return False

    def navigate_to_approval(self):
        """导航到审批页面"""
        self.log("开始导航到审批页面...")
        time.sleep(3)

        # 点击"全省铁路隐患库"卡片
        try:
            card = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//*[contains(text(),'全省铁路隐患库')]"))
            )
            card.click()
        except:
            try:
                card = self.driver.find_element(By.XPATH, "//*[@onclick and contains(.,'全省铁路隐患库')]")
                card.click()
            except Exception as e:
                self.log(f"点击卡片失败: {e}")
                self.driver.get("http://sxstlhllfzhpt.cn/hlbzxsys/mp/main.shtml?menui=3")

        time.sleep(5)

        # 点击菜单
        self.click_menu("日报告管理")
        time.sleep(2)
        self.click_menu("日报审批")

        self.log("等待审批页面加载...")
        time.sleep(40)

    def process_approval_page(self):
        """处理当前页面的所有待审批项目"""
        try:
            processed_count = 0

            while True:
                table = self.wait.until(
                    EC.presence_of_element_located((By.ID, "check_item_list"))
                )
                rows = table.find_elements(By.TAG_NAME, "tr")
                found_pending = False

                for row_index in range(len(rows)):
                    try:
                        row = rows[row_index]
                        cells = row.find_elements(By.TAG_NAME, "td")

                        if len(cells) < 8:
                            continue

                        status = cells[7].text.strip()

                        if "待审批" in status:
                            operate_cell = cells[-1]
                            approve_buttons = operate_cell.find_elements(By.XPATH, ".//i[contains(text(),'审批')]")
                            if not approve_buttons:
                                approve_buttons = operate_cell.find_elements(By.XPATH, ".//i[contains(@onclick,'spFun')]")

                            if not approve_buttons:
                                continue

                            approve_button = approve_buttons[0]
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", approve_button)
                            time.sleep(0.5)
                            approve_button.click()

                            self.approve_item()
                            processed_count += 1
                            time.sleep(2)
                            found_pending = True
                            break

                    except Exception as e:
                        continue

                if not found_pending:
                    break

            if processed_count > 0:
                self.log(f"已审批 {processed_count} 个项目")
            return processed_count > 0

        except Exception as e:
            self.log(f"处理页面时出错: {e}")
            return False

    def approve_item(self):
        """处理单个审批项 - Bootstrap 模态框"""
        try:
            textarea = self.wait.until(
                EC.visibility_of_element_located((By.XPATH, "//div[@id='addModal']//textarea"))
            )
            textarea.clear()
            textarea.send_keys("情况属实，同意上报")

            # 查找保存按钮
            save_button = None
            save_selectors = [
                (By.XPATH, "//button[@onclick='sp()']"),
                (By.XPATH, "//div[@id='addModal']//button[@onclick='sp()']"),
                (By.XPATH, "//button[normalize-space(text())='保存']"),
                (By.XPATH, "//div[@id='addModal']//button[normalize-space(text())='保存']"),
            ]

            for selector_type, selector_value in save_selectors:
                try:
                    save_button = self.short_wait.until(
                        EC.presence_of_element_located((selector_type, selector_value))
                    )
                    onclick_value = save_button.get_attribute("onclick")
                    if onclick_value and "sp()" in onclick_value:
                        break
                except TimeoutException:
                    continue

            if save_button:
                self.driver.execute_script("arguments[0].click();", save_button)
                time.sleep(1)

        except Exception as e:
            self.log(f"填写审批时出错: {e}")
            try:
                from selenium.webdriver.common.keys import Keys
                webdriver.ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            except:
                pass

    def go_to_next_page(self):
        """翻到下一页 - Bootstrap 分页"""
        try:
            self.short_wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "pagination"))
            )

            try:
                next_link = self.driver.find_element(By.XPATH, "//ul[contains(@class,'pagination')]//a[contains(text(),'»')]")
                parent_li = next_link.find_element(By.XPATH, "..")
                parent_class = parent_li.get_attribute("class") or ""

                if "disabled" in parent_class:
                    return False

                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_link)
                time.sleep(0.5)
                next_link.click()
                self.log("等待下一页数据加载...")
                time.sleep(40)
                return True

            except NoSuchElementException:
                pass

        except TimeoutException:
            pass

        return False

    def run(self):
        """运行自动化流程"""
        try:
            self.log("=" * 50)
            self.log("铁路隐患审批自动化脚本启动")
            self.log("=" * 50)

            self.open_site()
            self.login()
            self.navigate_to_approval()

            page_num = 1

            while True:
                self.log(f"正在处理第 {page_num} 页...")

                has_items = self.process_approval_page()

                if not has_items:
                    self.log("当前页面没有待审批项目")

                if not self.go_to_next_page():
                    break

                page_num += 1

            self.log("=" * 50)
            self.log(f"所有页面处理完成！共处理 {page_num} 页")
            self.log("=" * 50)

            self.log("按回车键关闭浏览器...")
            input()

        except Exception as e:
            self.log(f"运行出错: {e}")
            self.log("按回车键关闭浏览器...")
            input()

        finally:
            self.driver.quit()

    def test_login_only(self):
        """仅测试登录功能"""
        try:
            self.open_site()
            self.login()
            self.log("登录成功！浏览器将保持打开状态...")
            self.log("按回车键关闭...")
            input()
        except Exception as e:
            self.log(f"登录测试出错: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.driver.quit()


def load_config():
    """
    从配置文件加载账号密码
    :return: (username, password)
    """
    # 获取配置文件路径（兼容 PyInstaller 打包后的环境）
    if getattr(sys, 'frozen', False):
        # 打包后的环境：配置文件在 exe 同级目录
        base_path = os.path.dirname(sys.executable)
    else:
        # 开发环境：配置文件在脚本同级目录
        base_path = os.path.dirname(os.path.abspath(__file__))

    config_file = os.path.join(base_path, 'config.ini')

    # 如果配置文件存在，读取配置
    if os.path.exists(config_file):
        config = configparser.ConfigParser()
        config.read(config_file, encoding='utf-8')

        if 'credentials' in config:
            username = config['credentials'].get('username', 'aaa')
            password = config['credentials'].get('password', 'bbb')
            return username, password

    # 配置文件不存在或没有配置节，返回默认值
    return 'aaa', 'bbb'


if __name__ == "__main__":
    import sys

    # 优先使用配置文件，如果没有则使用命令行参数
    username, password = load_config()

    # 命令行参数会覆盖配置文件（可选）
    if len(sys.argv) > 1:
        username = sys.argv[1]
    if len(sys.argv) > 2:
        password = sys.argv[2]

    # 创建机器人实例（显示浏览器窗口）
    bot = RailwayApprovalBot(username=username, password=password, headless=False)

    # 运行完整流程
    bot.run()

    # 如果只想测试登录，使用：
    # bot.test_login_only()
