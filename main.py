from bs4 import BeautifulSoup
import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 \
    (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
}
user_url = "https://uts-logs.eng.vmware.com/vsan-fvt/nimbus-logs/Galileo_CI_Runs/home/worker/workspace/vsan-fvt-ci_ExecutionEngine1/Results/10/vsan-fvt-ci/ExecutionEngine1/"
user_url = "https://uts-logs.eng.vmware.com/vsan-fvt/01_VSANSPARSE_SNAPCREATEDELETE_P0/Results/"
testcase_result = "pass"
response = requests.get(url=user_url)
if response.status_code != 200:
    raise Exception("unexpected result. Status code %s", response.status_code)
soup = BeautifulSoup(response.content, 'html.parser')
# print(soup)

table = soup.find(lambda tag: tag.name == 'table')

new_list = []
for anchor in table.findAll('a'):
    href = anchor['href']
    new_list.append(href)

my_list = []
for file in new_list:
    new_file = file.removesuffix('/')
    my_list.append(new_file)

for file in my_list:
    print(file)
    print('\n')

url_list = []
for x in range(len(my_list)):
    new_url = user_url + my_list[x] + '/summary.html'
    url_list.append(new_url)

hyperlink = []
table_contents = []
table_contents2 = []
table_header = ['#', 'Testcase', 'Start', 'Result', 'Exceptions/Errors']
for link in url_list:
    html_response = requests.get(url=link, headers=headers)
    soup = BeautifulSoup(html_response.content, 'html.parser')
    table = soup.find(lambda tag: tag.name == 'table' and tag.has_attr('id') and tag['id'] == "testcaseTable")
    if table is None:
        continue

    rows = table.find_all("tr")
    for tr in rows:
        if (rows.index(tr) == 0 and link == url_list[0]):
            row_cells = header_cells = [th.getText().strip() for th in tr.find_all('th') if th.getText().strip() != '']
            table_header += [header_cells]

        else:
            row_cells = ([tr.find('th').getText()] if tr.find('th') else []) + [td.getText().strip() for td in
                                                                                tr.find_all('td') if
                                                                                td.getText().strip() != '']

        if len(row_cells) > 1:
            table_contents2 += [row_cells]
        # ---------------------------------FOR CREATING HYPERLINKS-------------------------------------------------------------#
        cols = tr.findAll(lambda tag: tag.name == 'td')
        for td in cols:
            if td.find('a'):
                href_link = td.find('a')['href']
                remove_link = link.removesuffix('summary.html')
                new_link = remove_link + href_link
                hyperlink += {new_link}

# -----------------------------------TO ADD HYPERLINKS TO THE LIST-----------------------------------------------------#
table_contents = table_contents2
for i in table_contents2:
    if i == ['#', 'Testcase', 'Start', 'Result', 'Exceptions/Errors']:
        table_contents.remove(i)

for x in range(len(table_contents)):
    table_contents[x].append(hyperlink[x])

# #--------------------------------FOR PRINTING OUT THE TABLE-----------------------------------------------------------#
#
# col_len={i:max(map(len,inner)) for i,inner in enumerate(zip(*table_contents))}
# for inner in table_contents:
#     for col,word in enumerate(inner):
#         print(f"{word:{col_len[col]}}",end=" | ")
#     print()


# -----------------------------FOR SPLITING THE TABLE IN PASS AND FAIL-------------------------------------------------#
mylist = table_contents
list_of_specific_list1 = ['PASS', 'PASS - PASS']
set_of_specific_element = set(list_of_specific_list1)
fail_output = [item for item in mylist if not set_of_specific_element.intersection(set(item))]
# print(fail_output)

mylist = table_contents
list_of_specific_list2 = ['FAIL', 'FAIL - FAIL', 'FAIL - SKIPRUN']
set_of_specific_element = set(list_of_specific_list2)
pass_output = [item for item in mylist if not set_of_specific_element.intersection(set(item))]
# print(pass_output)

# with open('passtest.txt', 'w') as f:
#     f.write(str(pass_output))

if testcase_result.lower() == 'fail':
    print("List of fail testcases:\n")
    col_len = {i: max(map(len, inner)) for i, inner in enumerate(zip(*fail_output))}
    for inner in fail_output:
        for col, word in enumerate(inner):
            print(f"{word:{col_len[col]}}", end=" | ")
        print()
else:
    print("List of pass testcases:\n")
    col_len = {i: max(map(len, inner)) for i, inner in enumerate(zip(*pass_output))}
    for inner in pass_output:
        for col, word in enumerate(inner):
            print(f"{word:{col_len[col]}}", end=" | ")
        print()
