import requests
import re
from progress.bar import IncrementalBar
import os
import argparse

URL = "https://survey.uowmkdu.edu.my"

def get_args(text,data):
	args = re.findall("<input type=\"hidden\" .*/>",text)
	for a in args:
		data[str(re.findall("id=\"([A-Za-z0-9_]+)\"",a)[0])] = str(re.findall("value=\"(.*)\"",a)[0])
	return data

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-u","--username",help="Enter your Student ID",required=True)
	parser.add_argument("-p","--password",help="Enter your Password (Last 4 Characters on back of your Student Card)",required=True)
	parser.add_argument("-all",choices=['1','2','3','4','5'],help="Enter your rating for all subjects")
	settings = parser.parse_args()
	os.system('clear')
	s = requests.Session()
	r = s.get(URL+"/Login.aspx")
	cookies = r.cookies
	data = {
		'ctl00$CPH_main$CB_AutoLogin': 'on',
		'ctl00$CPH_main$BTN_Submit': 'Proceed'
	}
	data = get_args(r.text,data)
	s.post(URL+"/Login.aspx",data=data,cookies=cookies)
	r = s.get(URL+"/Login2.aspx")
	data = {
		"ctl00$CPH_main$TB_UserName": settings.username,
		"ctl00$CPH_main$TB_Password": settings.password,
		"ctl00$CPH_main$BTN_Submit": "Proceed"
	}
	data = get_args(r.text,data)
	r = s.post(URL+"/Login2.aspx",data=data,cookies=cookies)
	if r.text.find("Invalid Username Or Password") != -1:
		print("Login failed")
		os.sys.exit(0)
	if settings.all:
		subject_input = 0
		rating_input = int(settings.all)
	while(1):
		r = s.get(URL+"/StudentSurveys.aspx",cookies=cookies)
		subjects = re.findall("name=\"(ctl00\$CPH_main\$GV_Surveys\$ctl[0-9]+\$btnProcess)",r.text)
		if not settings.all:
			subjects_name = re.findall("<span id=\"ctl00_CPH_main_GV_Surveys_ctl[0-9]+_lbl1\" ItemStyle-HorizontalAlign=\"Center\">(.*)</span>",r.text)
			options = zip(subjects,subjects_name)
			print("Subjects:\n")
			for i,o in enumerate(options):
				print(i,o[1])
			subject_input = int(input("Enter Subject ID: "))
			if subject_input >= len(subjects) or subject_input < 0:
				os.system('clear')
				print("Invalid Subject ID!")
				continue
			rating_input = int(input("Enter rating (1-5): "))
			if rating_input > 5 or rating_input < 0:
				os.system('clear')
				print("Invalid rating!")
				continue
		data = {}
		data = get_args(r.text,data)
		data["__EVENTTARGET"] = str(subjects[subject_input])
		s.post(URL+"/StudentSurveys.aspx",data=data,cookies=cookies)
		r = s.get(URL+"/survey.aspx",cookies=cookies)
		ratings = re.findall("__doPostBack\([A-Za-z0-9\$_,\'\\\\]+\)",r.text)
		questions = []
		for rate in ratings:
			questions.append(str(re.findall("ctl00\$CPH_main\$gvQuestion_Category\$ctl[0-9]+\$gvQuestion_SubCategory\$ctl[0-9]+\$gvQuestion\$ctl[0-9]+\$rbl5Answer",rate)[0]))
		questions = list(set(questions))
		bar = IncrementalBar('Processing', max=len(questions))
		data = {
			"__LASTFOCUS":'',
			"__ASYNCPOST": "true"
		}
		data = get_args(r.text,data)
		data['ctl00$CPH_main$token_id'] = int(data.pop('ctl00_CPH_main_token_id'))
		data['ctl00$CPH_main$attendance_id'] = int(data.pop('ctl00_CPH_main_attendance_id'))
		for q in questions:
			data['ctl00$CPH_main$ScriptManager1'] = "ctl00$CPH_main$ScriptManager1|" + q + "$" + str(rating_input-1)
			data[q] = rating_input
			data['__EVENTTARGET'] = q + "$" + str(rating_input-1)
			headers = {
				'Origin': 'http://survey.kdu.edu.my',
				'Accept-Encoding': 'gzip, deflate',
				'Accept-Language':'en-US,en;q=0.9',
				'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
				'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
				'Accept': '*/*',
				'Cache-Control': 'no-cache',
				'Referer': 'http://survey.kdu.edu.my/survey.aspx',
				'Connection': 'keep-alive',
				'X-MicrosoftAjax': 'Delta=true' 
			}
			s.post(URL+"/survey.aspx",headers=headers,data=data,cookies=cookies)
			bar.next()
		bar.finish()
		data = {}
		data = get_args(r.text,data)
		data["__EVENTTARGET"] = str(subjects[subject_input])
		s.post(URL+"/StudentSurveys.aspx",data=data,cookies=cookies)
		r = s.get(URL+"/survey.aspx",cookies=cookies)

		data = {
			"ctl00$CPH_main$btnSubmit": "Complete"		
		}
		data = get_args(r.text,data)
		data['ctl00$CPH_main$token_id'] = int(data.pop('ctl00_CPH_main_token_id'))
		data['ctl00$CPH_main$attendance_id'] = int(data.pop('ctl00_CPH_main_attendance_id'))
		s.post(URL+"/survey.aspx",headers=headers,data=data,cookies=cookies)

		if not settings.all:
			os.system('clear')
		if settings.all:
			if subject_input < len(subjects)-1:
				subject_input += 1
			else:
				print("Done!")
				break
