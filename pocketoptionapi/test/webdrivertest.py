from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver

class WebdriverTest:
    def __init__(self) -> None:
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.url = "https://pocketoption.com"
    def connect(self):
        sevice = webdriver.ChromeService(executable_path=ChromeDriverManager().install())
        driver = webdriver.Chrome(service=sevice)
        driver.get(url=self.url)

# Example usage
wt = WebdriverTest()
wt.connect()