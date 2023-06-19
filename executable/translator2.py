from selenium import webdriver 
from selenium.webdriver.common.keys import Keys 
from selenium.common.exceptions import NoSuchElementException 
from selenium.common.exceptions import JavascriptException 

# local variables 
from selenium.webdriver.chrome.options import Options as ChromeOptions 
chrome_op = ChromeOptions() 
chrome_op.add_argument('--headless')
browser = webdriver.Chrome(executable_path ='./chromedriver', options = chrome_op)



def takeInput(): 
	languages = {"English": 'en', "French": 'fr', 
				"Spanish": 'es', "German": 'de', "Italian": 'it'} 

	print("Select a source and target language (enter codes)") 
	print("Language", " ", "Code") 

	for x in languages: 
		print(x, " ", languages[x]) 

	print("\n\nSource: ", end ="") 
	src = input() 
	sflag = 0

	for x in languages: 
		if(languages[x] == src and not sflag): 
			sflag = 1
			break
	if(not sflag): 
		print("Source code not from the list, Exiting....") 
		exit() 

	print("Target: ", end ="") 
	trg = input() 
	tflag = 0

	for x in languages: 
		if(languages[x] == trg and not tflag): 
			tflag = 1
			break

	if(not tflag): 
		print("Target code not from the list, Exiting....") 
		exit() 

	if(src == trg): 
		print("Source and Target cannot be same, Exiting...") 
		exit() 

	print("Enter the phrase: ", end ="") 
	phrase = input() 

	return src, trg, phrase

def makeCall(url, script, default): 
	response = default 
	try: 
		browser.get(url) 
		while(response == default): 
			response = browser.execute_script(script) 

	except JavascriptException: 
		print(JavascriptException.args) 

	except NoSuchElementException: 
		print(NoSuchElementException.args) 

	if(response != default): 
		return response 
	else: 
		return 'Not Available'


def googleTranslate(src, trg, phrase): 
	url = 'https://translate.google.co.in/# view = home&op = translate&sl =' + src + '&tl =' + trg+'&text ='+phrase
	script = 'return document.getElementsByClassName("tlid-translation")[0].textContent'
	return makeCall(url, script, None)





if __name__ == "__main__": 
    src, trg, phrase = takeInput() 
    print("\nResult: ", googleTranslate(src, trg, phrase))




