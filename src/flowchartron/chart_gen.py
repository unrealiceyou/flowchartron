import os, shutil, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from PyQt5.QtCore import pyqtSignal 

def cp(file_path: str, output_path: str):
    if os.name == "nt":
        cmd = f"copy \"{file_path}\" \"{output_path}\""
    else:
        cmd = f"cp \"{file_path}\" \"{output_path}\""
    os.system(cmd)

class DrawIOBrowser:
    def __init__(self):
        if not os.path.exists(".drawio_export"):
            os.makedirs(".drawio_export")
        if not os.path.isdir(".drawio_export"):
            raise IsADirectoryError
        self._WORKING_DIRECTORY = os.path.abspath(".drawio_export")

    def export_to_png(self, drawio_file: str, output_path: str, progress_signal: pyqtSignal):
        options = webdriver.FirefoxOptions()
        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.manager.showWhenStarting", 2)
        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.dir", self._WORKING_DIRECTORY)
        options.add_argument("-headless")

        progress_signal.emit(1)
        self._driver = webdriver.Firefox(options=options)
        self._driver.implicitly_wait(10)
        self._driver.get("https://app.diagrams.net/")

        save_to_device_btn = self._driver.find_element(
                By.XPATH,
                "/html/body/div[11]/div/div/div/a[3]"
                )
        save_to_device_btn.click()

        new_diagram_btn = self._driver.find_element(
                By.CSS_SELECTOR, 
                "button.geBigButton:nth-child(1)"
                )
        new_diagram_btn.click()

        filename_textbox = self._driver.find_element(
                By.CSS_SELECTOR, 
                ".geDialog > div:nth-child(1) > div:nth-child(1) > input:nth-child(2)"
                )
        filename_textbox.clear()
        filename_textbox.send_keys("output.png")

        create_btn = self._driver.find_element(
                By.CSS_SELECTOR, 
                "button.geBtn:nth-child(4)"
                )
        create_btn.click()

        if not os.path.exists(drawio_file):
            raise FileNotFoundError
        if os.path.isdir(output_path):
            output_path = os.path.join(output_path, "output.png")

        drawio_file = os.path.abspath(drawio_file)

        downloaded_path = os.path.join(self._WORKING_DIRECTORY, "output.png")
        if os.path.isfile(downloaded_path): os.remove(downloaded_path)

        progress_signal.emit(2)
        webdriver.ActionChains(self._driver)\
                .key_down(Keys.CONTROL)\
                .send_keys("a")\
                .key_up(Keys.CONTROL)\
                .key_up(Keys.DELETE)\
                .key_down(Keys.DELETE)\
                .perform()

        scratchpad_btn = self._driver.find_element(
                By.CSS_SELECTOR, 
                "img.geAdaptiveAsset:nth-child(3)"
                )
        scratchpad_btn.click()

        file_input = self._driver.find_element(
                By.CSS_SELECTOR, 
                "input[type=file]"
                )
        file_input.send_keys(drawio_file)

        save_btn = self._driver.find_element(
                By.CSS_SELECTOR, 
                "#btnSave"
                )
        save_btn.click()

        last_scratchpad_elem = self._driver.find_element(
                By.CSS_SELECTOR, 
                "div.geSidebarContainer:nth-child(5) > div:nth-child(1) > div:nth-child(4) > div:nth-child(1) > a:last-child"
                )
        last_scratchpad_elem.click()

        progress_signal.emit(3)
        webdriver.ActionChains(self._driver)\
                .key_down(Keys.CONTROL)\
                .send_keys("s")\
                .key_up(Keys.CONTROL)\
                .perform()

        while not os.path.isfile(downloaded_path):
            time.sleep(0.5)

        cp(downloaded_path, output_path)
        self._driver.quit()

    def __del__(self):
        if os.path.isdir(self._WORKING_DIRECTORY):
            shutil.rmtree(self._WORKING_DIRECTORY)
        self._driver.quit()
        return

