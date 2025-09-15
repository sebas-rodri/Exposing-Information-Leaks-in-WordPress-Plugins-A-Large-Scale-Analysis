import requests
import string
import time
import random
import traceback
import json
from bs4 import BeautifulSoup

BASEURL = "https://wpscan.com/plugins"

categories = ["0-9"] + list(string.ascii_uppercase) + list(string.ascii_lowercase)

class CloudflareException(Exception): pass
class NoResultsException(Exception): pass

vulns = []
for category in categories:
	page_id = 1
	page_error = False
	s = requests.Session()
	s.headers.update({
		'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36'
	})

	while not page_error:
		print(f"Category: {category} @ Page {page_id}: {len(vulns)} vulns")
		try:
			try:
				r = s.get(BASEURL, params={'page': page_id, 'get': category})
				print(r.url)
				# open("page.txt","w").write(r.content.decode())
				if 'wp-block-navigation__container' not in r.text:
					# Block by cloudflare
					raise CloudflareException("Damn Cloudflare:")
			except (CloudflareException, Exception) as e:
				print(e)
				print(f"Cloudflare blocked us? waiting 2-3mins before retry: {page_id} @ {category}")
				time.sleep(random.randint(120, 180))

			if 'No results found.' in r.text or 'Page Not Found' in r.text:
				raise NoResultsException("No results")
			bsoup = BeautifulSoup(r.text, "html.parser")
			for row in bsoup.select("div[class^='vulnerabilities__table--row']"):
				# divs = row.select("div[class^='table_tableCell']")
				# #print(divs)
				# title = divs[0].select_one("p").select_one("a").text
				# date = divs[2].select_one("p").text
				# vuln = divs[4].select_one("p").select_one("a").text
				# href = divs[4].select_one("p").select_one("a")['href']
				a_slug =  row.select_one("a[class^='vulnerabilities__table--slug-link']")
				p_link = a_slug['href']
				p_slug = a_slug.text.strip()
				date = row.select_one("div[class^='vulnerabilities__table--date']").text.replace("Published","").strip()
				a_title = row.select_one("div[class^='vulnerabilities__table--title']").select_one("a")
				title = a_title.text.strip()
				v_link = a_title['href']

				vulnobj = {
					'title': title,
					'date': date,
					'p_slug': p_slug,
					'p_href': p_link,
					'v_link': v_link
					}
				# print(vulnobj)
				vulns.append(vulnobj)
			with open("./01-vulns.json", "w") as f:
				f.write(json.dumps(vulns))
			page_id += 1
			print("waiting before request to next page")
			time.sleep(random.randint(5,10))
		except NoResultsException as e:
			page_error = True
		except Exception as e:
			print("Error occurred")
			traceback.print_exc()
			time.sleep(random.randint(60,120))


		with open("./01-vulns.json", "w") as f:
			f.write(json.dumps(vulns))

	print("Sleeping...")
	time.sleep(random.randint(3,10))

with open("./01-vulns.json", "w") as f:
	f.write(json.dumps(vulns))