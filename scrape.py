from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
import time
import csv
from tqdm import tqdm

def computeCsvStringFromTable(page, tableSelector, shouldIncludeRowHeaders):
    csvString = page.execute_script("""
        const table = document.querySelector(arguments[0]);
        if (!table) {
            return null;
        }

        let csvString = "";
        for (let i = 0; i < table.rows.length; i++) {
            const row = table.rows[i];

            if (!arguments[1] && i === 0) {
                continue;
            }

            for (let j = 0; j < row.cells.length; j++) {
                const cell = row.cells[j];

                const formattedCellText = cell.innerText.replace(/\\n/g, '\\\\n').trim();
                if (formattedCellText !== "No Data") {
                    csvString += formattedCellText;
                }

                if (j === row.cells.length - 1) {
                    csvString += "\\n";
                } else {
                    csvString += ",";
                }
            }
        }
        return csvString;
    """, tableSelector, shouldIncludeRowHeaders)
    return csvString

browser = webdriver.Chrome()
page = browser.get('https://www.mta.maryland.gov/performance-improvement')
time.sleep(5)

csvString = ""

yearSelect = Select(browser.find_element_by_css_selector('select[name="ridership-select-year"]'))
yearSelectOptions = [option.get_attribute("value") for option in yearSelect.options]

monthSelect = Select(browser.find_element_by_css_selector('select[name="ridership-select-month"]'))
monthSelectOptions = [option.get_attribute("value") for option in monthSelect.options]

routeSelect = Select(browser.find_element_by_css_selector('select[name="ridership-select-route"]'))
routeSelectOptions = [option.get_attribute("value") for option in routeSelect.options]

print('routes available:', routeSelectOptions)
print('months available:', monthSelectOptions)
print('years available:', yearSelectOptions)

progressBar = None
try:
    progressBar = tqdm(total=(len(monthSelectOptions) * len(yearSelectOptions)))
except:
    progressBar = None

hasIncludedRowHeaders = True
for yearSelectOption in yearSelectOptions:
    yearSelect.select_by_value(yearSelectOption)
    for monthSelectOption in monthSelectOptions:
        monthSelect.select_by_value(monthSelectOption)

        monthSelectElem = browser.find_element_by_css_selector('select[name="ridership-select-month"]')
        monthSelectElem.send_keys(Keys.TAB)
        monthSelectElem.send_keys(Keys.TAB)
        monthSelectElem.send_keys(Keys.ENTER)

        csvString += computeCsvStringFromTable(browser, 'div#container-ridership-table > table', hasIncludedRowHeaders)

        if hasIncludedRowHeaders:
            hasIncludedRowHeaders = False

        if progressBar:
            progressBar.update(1)

if progressBar:
    progressBar.close()

browser.quit()

with open('mta-bus-ridership.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    for line in csvString.split('\n'):
        writer.writerow(line.split(','))

# read csvString from file
with open('mta-bus-ridership.csv', 'r', newline='') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        print(row)
