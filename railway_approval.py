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

        # 等待页面加载
        self.log("等待页面加载完成...")
        time.sleep(3)

        # 检查是否有 frame 并切换
        try:
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            frames = self.driver.find_elements(By.TAG_NAME, "frame")
            total_frames = len(iframes) + len(frames)

            if total_frames > 0:
                self.log(f"发现 {total_frames} 个 frame，正在切换...")

                # 切换到第一个可用的 frame
                switched = False

                # 先尝试普通 frame
                for i, frame in enumerate(frames):
                    try:
                        self.driver.switch_to.frame(frame)
                        self.log(f"成功切换到 frame #{i+1}")
                        switched = True
                        break
                    except Exception as e:
                        self.log(f"切换到 frame #{i+1} 失败: {e}")
                        continue

                # 如果普通 frame 失败，尝试 iframe
                if not switched:
                    for i, iframe in enumerate(iframes):
                        try:
                            self.driver.switch_to.frame(iframe)
                            self.log(f"成功切换到 iframe #{i+1}")
                            switched = True
                            break
                        except Exception as e:
                            self.log(f"切换到 iframe #{i+1} 失败: {e}")
                            continue

                if not switched:
                    self.log("警告：无法切换到任何 frame")

                # 切换后等待 frame 内容加载
                time.sleep(2)

            else:
                self.log("页面中没有 frame")

        except Exception as e:
            self.log(f"处理 frame 时出错: {e}")

        self.log(f"当前 URL: {self.driver.current_url}")

    def login(self):
        """登录 - Element UI"""
        self.log("开始登录流程...")

        # 等待页面加载
        time.sleep(2)

        # 尝试多种方式定位用户名输入框
        self.log("正在查找用户名输入框...")

        username_input = None
        username_selectors = [
            # 方法1: 通过 type 和 class (Element UI)
            (By.XPATH, "//input[@type='text' and contains(@class,'el-input__inner')]"),
            # 方法2: 第一个文本输入框
            (By.XPATH, "(//input[@type='text'])[1]"),
            # 方法3: 通过 placeholder（如果有）
            (By.XPATH, "//input[contains(@placeholder,'用户') or contains(@placeholder,'账号') or contains(@placeholder,'username')]"),
            # 方法4: 通过 name 属性
            (By.NAME, "username"),
            (By.NAME, "user"),
            # 方法5: 第一个 input
            (By.TAG_NAME, "input"),
        ]

        for selector_type, selector_value in username_selectors:
            try:
                self.log(f"尝试选择器: {selector_type} = {selector_value}")
                username_input = self.short_wait.until(
                    EC.presence_of_element_located((selector_type, selector_value))
                )
                self.log(f"成功找到用户名输入框！")
                break
            except TimeoutException:
                self.log(f"该选择器未找到元素，尝试下一个...")
                continue

        if not username_input:
            # 打印页面源码用于调试
            self.log("错误：无法找到用户名输入框！")
            self.log("页面标题: " + self.driver.title)
            self.log("页面URL: " + self.driver.current_url)

            # 保存页面截图
            screenshot_path = "/tmp/login_page_debug.png"
            self.driver.save_screenshot(screenshot_path)
            self.log(f"已保存页面截图到: {screenshot_path}")

            # 打印页面上所有 input 元素的信息
            try:
                inputs = self.driver.find_elements(By.TAG_NAME, "input")
                self.log(f"页面上共有 {len(inputs)} 个 input 元素:")
                for i, inp in enumerate(inputs):
                    inp_type = inp.get_attribute("type") or "未知"
                    inp_name = inp.get_attribute("name") or "无"
                    inp_class = inp.get_attribute("class") or "无"
                    inp_placeholder = inp.get_attribute("placeholder") or "无"
                    self.log(f"  Input #{i+1}: type={inp_type}, name={inp_name}, class={inp_class}, placeholder={inp_placeholder}")
            except:
                pass

            raise Exception("无法找到用户名输入框，请检查页面结构")

        # 输入用户名
        self.log("输入用户名...")
        username_input.clear()
        username_input.send_keys(self.username)
        self.log("用户名已输入")

        # 查找密码输入框
        self.log("正在查找密码输入框...")
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
                self.log(f"成功找到密码输入框！")
                break
            except TimeoutException:
                continue

        if not password_input:
            raise Exception("无法找到密码输入框")

        self.log("输入密码...")
        password_input.clear()
        password_input.send_keys(self.password)
        self.log("密码已输入")

        # 等待用户手动输入验证码
        self.log("=" * 50)
        self.log("请手动输入验证码，输入完成后按回车键继续...")

        # 显示浏览器提示框
        self.show_verification_alert()

        # 等待用户按回车
        input("按回车键继续...")

        # 移除浏览器提示框
        self.hide_verification_alert()

        # 点击登录按钮 - 尝试多种方式
        self.log("正在查找登录按钮...")

        login_button = None
        login_selectors = [
            # 注意：实际文本是"登 录"（中间有空格）
            (By.XPATH, "//button[contains(text(),'登 录')]"),
            (By.XPATH, "//button[normalize-space(text())='登录']"),
            (By.XPATH, "//button[contains(@class,'btn-block')]"),
            (By.CLASS_NAME, "btn-block"),
            # 通过文本包含
            (By.XPATH, "//button[contains(text(),'登')]"),
        ]

        for selector_type, selector_value in login_selectors:
            try:
                self.log(f"尝试选择器: {selector_type} = {selector_value}")
                login_button = self.short_wait.until(
                    EC.element_to_be_clickable((selector_type, selector_value))
                )
                self.log(f"成功找到登录按钮！")
                break
            except TimeoutException:
                self.log(f"该选择器未找到元素，尝试下一个...")
                continue

        if not login_button:
            # 调试：打印页面上所有按钮
            try:
                buttons = self.driver.find_elements(By.TAG_NAME, "button")
                self.log(f"页面上共有 {len(buttons)} 个按钮:")
                for i, btn in enumerate(buttons):
                    btn_text = btn.text.strip()
                    btn_class = btn.get_attribute("class") or "无"
                    btn_type = btn.get_attribute("type") or "无"
                    self.log(f"  Button #{i+1}: text='{btn_text}', class={btn_class}, type={btn_type}")
            except:
                pass

            raise Exception("无法找到登录按钮")

        self.log("点击登录按钮...")
        login_button.click()
        self.log("登录请求已发送...")

        # 等待登录成功 - 等待主页加载
        self.log("等待登录成功...")
        time.sleep(5)

        # 登录后，frame 内容会更新为主页
        self.log("检查登录后的状态...")
        self.log(f"当前 URL: {self.driver.current_url}")

        # 保存登录后的页面信息
        try:
            links = self.driver.find_elements(By.TAG_NAME, "a")
            self.log(f"当前页面有 {len(links)} 个链接")

            # 如果链接很少，说明可能还在登录页或者需要等待
            if len(links) < 5:
                self.log("页面链接较少，等待更长时间...")
                time.sleep(3)
                links = self.driver.find_elements(By.TAG_NAME, "a")
                self.log(f"等待后页面有 {len(links)} 个链接")
        except Exception as e:
            self.log(f"检查链接时出错: {e}")

    def show_verification_alert(self):
        """在页面显示验证码输入提示"""
        js_code = """
        var alertBox = document.createElement('div');
        alertBox.id = 'verification-alert';
        alertBox.style.cssText = 'position: fixed; top: 10px; left: 10px; z-index: 9999; background: #ff4444; color: white; padding: 40px; border-radius: 15px; font-size: 70px; font-weight: bold; box-shadow: 0 8px 24px rgba(0,0,0,0.3); max-width: 1200px; font-family: Arial, sans-serif; line-height: 1.6;';
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

        # 等待轮播图页面加载
        self.log("等待主页完全加载...")
        time.sleep(3)

        self.log("当前 URL: " + self.driver.current_url)

        # 登录后是轮播图页面，需要点击"全省铁路隐患库"卡片
        self.log("正在点击'全省铁路隐患库'卡片...")

        # 查找包含"全省铁路隐患库"文本的元素
        # 这是一个 div.swiper-slide 元素，点击后会跳转
        try:
            # 方法1: 直接查找包含文本的元素
            card = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//*[contains(text(),'全省铁路隐患库')]"))
            )
            self.log("找到'全省铁路隐患库'卡片")
            card.click()
            self.log("已点击卡片")
        except:
            # 方法2: 通过 onclick 属性查找
            try:
                card = self.driver.find_element(By.XPATH, "//*[@onclick and contains(.,'全省铁路隐患库')]")
                card.click()
                self.log("已点击卡片（通过onclick）")
            except Exception as e:
                self.log(f"点击卡片失败: {e}")
                # 方法3: 直接访问 URL
                self.log("尝试直接访问URL...")
                self.driver.get("http://sxstlhllfzhpt.cn/hlbzxsys/mp/main.shtml?menui=3")

        # 等待跳转后的页面加载
        self.log("等待系统主页面加载...")
        time.sleep(5)

        self.log("当前 URL: " + self.driver.current_url)

        # 现在应该进入了系统主页面，需要查找"日报告管理"和"日报审批"
        # 保存页面源码用于调试
        with open("/tmp/main_page.html", "w", encoding="utf-8") as f:
            f.write(self.driver.page_source)
        self.log("已保存主页面源码到: /tmp/main_page.html")

        # 查找所有链接和菜单项
        try:
            all_links = self.driver.find_elements(By.TAG_NAME, "a")
            self.log(f"主页面有 {len(all_links)} 个链接")

            # 显示所有包含文本的链接
            count = 0
            for i, link in enumerate(all_links):
                text = link.text.strip()
                if text and count < 30:  # 显示前30个
                    self.log(f"  链接#{i+1}: {text}")
                    count += 1
        except Exception as e:
            self.log(f"查找链接时出错: {e}")

        # 尝试点击"日报告管理"
        self.log("正在查找'日报告管理'...")
        success = self.click_menu("日报告管理")
        time.sleep(2)

        # 尝试点击"日报审批"
        self.log("正在查找'日报审批'...")
        success = self.click_menu("日报审批")

        self.log("等待审批页面加载...")
        self.log("重要：表格渲染需要约40秒，请耐心等待...")
        time.sleep(40)  # 等待表格渲染
        self.log("等待完成，开始处理...")

    def process_approval_page(self):
        """
        处理当前页面的所有待审批项目
        :return: 是否处理了项目
        """
        self.log("正在处理当前页面的待审批项目...")

        try:
            processed_count = 0

            while True:
                # 每次循环都重新获取表格，避免元素过期
                table = self.wait.until(
                    EC.presence_of_element_located((By.ID, "check_item_list"))
                )
                rows = table.find_elements(By.TAG_NAME, "tr")

                # 从头查找第一个"待审批"的项目
                found_pending = False

                for row_index in range(len(rows)):
                    try:
                        row = rows[row_index]
                        cells = row.find_elements(By.TAG_NAME, "td")

                        if len(cells) < 8:
                            continue

                        # 获取状态（第8列，索引7）
                        status = cells[7].text.strip()

                        # 找到第一个"待审批"的项目
                        if "待审批" in status:
                            self.log(f"找到待审批项目（第 {row_index} 行），开始处理...")

                            # 获取操作列（最后一列）
                            operate_cell = cells[-1]

                            # 查找"审批"按钮
                            approve_buttons = operate_cell.find_elements(By.XPATH, ".//i[contains(text(),'审批')]")
                            if not approve_buttons:
                                approve_buttons = operate_cell.find_elements(By.XPATH, ".//i[contains(@onclick,'spFun')]")

                            if not approve_buttons:
                                self.log(f"未找到审批按钮，跳过")
                                continue

                            approve_button = approve_buttons[0]

                            # 滚动到按钮可见
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", approve_button)
                            time.sleep(0.5)

                            # 点击审批按钮
                            approve_button.click()
                            self.log("审批按钮已点击")

                            # 等待模态框加载并填写审批
                            self.approve_item()
                            processed_count += 1

                            # 等待页面更新
                            time.sleep(2)

                            # 标记找到并跳出当前for循环，重新开始while循环
                            found_pending = True
                            break

                    except Exception as e:
                        self.log(f"处理第 {row_index} 行时出错: {e}")
                        continue

                # 如果没找到待审批项目，退出while循环
                if not found_pending:
                    self.log("当前页面没有更多待审批项目")
                    break

            self.log(f"当前页面处理完成，共审批 {processed_count} 个项目")
            return processed_count > 0

        except Exception as e:
            self.log(f"处理页面时出错: {e}")
            import traceback
            traceback.print_exc()
            return False

    def approve_item(self):
        """处理单个审批项 - Bootstrap 模态框"""
        self.log("正在填写审批意见...")

        try:
            # 直接等待模态框内的 textarea 元素可见（确保内容已加载）
            self.log("等待审批弹窗打开...")
            textarea = self.wait.until(
                EC.visibility_of_element_located((By.XPATH, "//div[@id='addModal']//textarea"))
            )
            self.log("审批弹窗已打开，找到输入框")

            textarea.clear()
            textarea.send_keys("情况属实，同意上报")
            self.log("已填写审批意见")

            # 点击保存按钮 - Bootstrap 按钮
            self.log("点击保存按钮...")
            save_button = None
            save_selectors = [
                # 通过 onclick 属性查找（最精确）
                (By.XPATH, "//button[@onclick='sp()']"),
                # 在模态框内通过 onclick 属性查找
                (By.XPATH, "//div[@id='addModal']//button[@onclick='sp()']"),
                # 使用 normalize-space 处理 HTML 实体和空格
                (By.XPATH, "//button[normalize-space(text())='保存']"),
                # 在模态框内使用 normalize-space
                (By.XPATH, "//div[@id='addModal']//button[normalize-space(text())='保存']"),
            ]

            for selector_type, selector_value in save_selectors:
                try:
                    # 先查找元素，不要求可点击
                    save_button = self.short_wait.until(
                        EC.presence_of_element_located((selector_type, selector_value))
                    )
                    self.log(f"找到保存按钮: {selector_type}={selector_value}")

                    # 验证 onclick 属性
                    onclick_value = save_button.get_attribute("onclick")
                    if onclick_value and "sp()" in onclick_value:
                        self.log("验证通过：onclick 包含 sp()")
                        break
                    else:
                        self.log(f"onclick 值是: {onclick_value}，继续查找...")
                        continue
                except TimeoutException:
                    continue

            if save_button:
                # 使用 JavaScript 点击来避免遮挡问题
                self.driver.execute_script("arguments[0].click();", save_button)
                self.log("保存成功")

                # 等待模态框关闭
                time.sleep(1)
            else:
                self.log("警告：未找到保存按钮")

        except Exception as e:
            self.log(f"填写审批时出错: {e}")
            import traceback
            traceback.print_exc()

            # 尝试按 ESC 关闭弹窗
            try:
                from selenium.webdriver.common.keys import Keys
                webdriver.ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            except:
                pass

    def go_to_next_page(self):
        """翻到下一页 - Bootstrap 分页"""
        self.log("尝试翻到下一页...")

        try:
            # 等待分页组件加载
            self.short_wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "pagination"))
            )

            # 获取当前页码
            try:
                active_page = self.driver.find_element(By.XPATH, "//ul[contains(@class,'pagination')]//li[contains(@class,'active')]/a")
                current_page_text = active_page.text.strip()
                self.log(f"当前页码: {current_page_text}")
            except:
                current_page_text = "1"
                self.log("无法获取当前页码，假设是第1页")

            # Bootstrap 分页结构：<ul class="pagination"><li><a>»</a></li></ul>
            # 查找包含 "»" 的链接
            try:
                next_link = self.driver.find_element(By.XPATH, "//ul[contains(@class,'pagination')]//a[contains(text(),'»')]")
                parent_li = next_link.find_element(By.XPATH, "..")

                # 检查父级 li 是否有 disabled 类
                parent_class = parent_li.get_attribute("class") or ""

                if "disabled" in parent_class:
                    self.log("下一页按钮已禁用，没有更多页了")
                    return False
                else:
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_link)
                    time.sleep(0.5)
                    next_link.click()
                    self.log("已点击下一页链接")

                    # 等待页面更新 - 固定等待40秒让数据加载
                    self.log("等待页面数据更新（约40秒）...")
                    time.sleep(40)  # 等待表格数据加载
                    self.log("数据加载完成")
                    return True

            except NoSuchElementException:
                self.log("未找到下一页链接（»）")

        except TimeoutException:
            self.log("等待分页组件超时")
            return False
        except Exception as e:
            self.log(f"翻页时出错: {e}")
            import traceback
            traceback.print_exc()

        self.log("没有更多页了")
        return False

    def run(self):
        """运行自动化流程"""
        try:
            self.log("=" * 50)
            self.log("铁路隐患审批自动化脚本启动")
            self.log("=" * 50)

            # 打开网站
            self.open_site()

            # 登录
            self.login()

            # 导航到审批页面
            self.navigate_to_approval()

            # 处理所有页面的待审批项目
            page_num = 1
            total_processed = 0

            while True:
                self.log(f"正在处理第 {page_num} 页...")
                self.log("-" * 30)

                has_items = self.process_approval_page()

                if not has_items:
                    self.log("当前页面没有待审批项目")

                # 翻到下一页
                if not self.go_to_next_page():
                    break

                page_num += 1

            self.log("=" * 50)
            self.log(f"所有页面处理完成！共处理 {page_num} 页")
            self.log("=" * 50)

            # 保持浏览器打开，方便查看结果
            self.log("按回车键关闭浏览器...")
            input()

        except Exception as e:
            self.log(f"运行出错: {e}")
            import traceback
            traceback.print_exc()
            self.log("按回车键关闭浏览器...")
            input()

        finally:
            self.driver.quit()
            self.log("浏览器已关闭")

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
    config_file = os.path.join(os.path.dirname(__file__), 'config.ini')

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
