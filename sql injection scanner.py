import requests
from bs4 import BeautifulSoup


s = requests.Session()
s.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


# function to get all forms
def get_forms(url):
    soup = BeautifulSoup(s.get(url).content, "html.parser")
    return soup.find_all("form")


# function to get detail of each form
def form_details(form):
    detailsOfForm = {}
    action = form.attrs.get("action")
    method = form.attrs.get("method", "get")    # default for "method" is "get".

    inputs = []

    for input_tag in form.find_all('input'):     # finds every input tag in form.
        input_type = input_tag.attrs.get('type', 'text')
        input_name = input_tag.attrs.get('name')
        input_value = input_tag.attrs.get('value', '')

        # appending all the data into inputs list.
        inputs.append({
            "type" : input_type,
            "name" : input_name,
            "value" : input_value
        })

        detailsOfForm['action'] = action
        detailsOfForm['method'] = method
        detailsOfForm['inputs'] = inputs
        return detailsOfForm


# function that returns whether the response says its vulnerable.
def vulnerable(response):
    # Oracle and SQL Server Errors:
    errors = {"quoted string not properly terminated",
              "unclosed quotation mark after the character string",
              "you have an error in your SQL syntax"}

    for error in errors:
        if error in response.content.decode().lower():
            return True

    return False


# function that scan the target site
def sql_injection_scan(url):
    forms = get_forms(url)
    print(f"[+] Detected {len(forms)} forms on {url}.")

    for form in forms:
        details = form_details(form)

        # we iterate over the ' sign that might be malicious.
        for i in "\"'":
            data = {}
            for input_tag in details["inputs"]:
                if input_tag["type"] == "hidden" or input_tag["value"]:
                    data[input_tag["name"]] = input_tag["value"] + i
                elif input_tag["type"] != "submit":
                    data[input_tag["name"]] = f"test{i}"

            print(url)
            form_details(form)

            # checking if the method is post or get.
            if details['method'] == 'post':
                res = s.post(url, data=data)
            elif details['method'] == 'get':
                res = s.get(url, params=data)

            if vulnerable(res):
                print("SQL injection attack vulnerability in link: ", url)
            else:
                print("No SQL injection attack vulnerability detected")
                break


if __name__ == "__main__":
    urlToCheck = "https://facebook.com"
    sql_injection_scan(urlToCheck)
