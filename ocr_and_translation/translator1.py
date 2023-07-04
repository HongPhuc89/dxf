import time
import selenium
from selenium import webdriver 
from selenium.webdriver.chrome.options import Options as ChromeOptions 




# Give Language code in which you want to translate the text:=>
#lang_code = 'sq'
def Translator(original):
	CHROMEDRIVER_PATH = './chromedriver'
	input1 = original
	chrome_op = ChromeOptions() 
	chrome_op.add_argument('--headless')
	chrome_op.add_argument('--no-sandbox')
	# Provide text that you want to translate:=>
	print(input1)
	# launch browser with selenium:=>
	browser = webdriver.Chrome() #browser = webdriver.Chrome('path of chromedriver.exe file') if the chromedriver.exe is in different folder
	# copy google Translator link here:=>
	browser.get("https://translate.google.com")
	#view=home&op=translate&sl=en&tl="+lang_code)
	# Use Javascript command to give input text:=>
	command = "document.getElementById('source').value = '" + input1 + "'"
	# Excute above command:=>
	browser.execute_script(command)
	# just wait for some time for translating input text:=>
	time.sleep(6)
	# Given below x path contains the translated output that we are storing in output variable:=>
	output1 = browser.find_element_by_xpath( '/html/body/div[2]/div[2]/div[1]/div[2]/div[1]/div[1]/div[2]/div[3]/div[1]/div[2]/div/span[1]').text
	translated = output1
	# Display the output:=>
	print("Translated Paragraph:=> " + translated)
	time.sleep(6)
	browser.quit()
