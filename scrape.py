import asyncio
import csv
from pathlib import Path

# Import beautiful soup
from bs4 import BeautifulSoup

from tqdm import tqdm
from playwright.async_api import Playwright, async_playwright


async def compute_csv_string_from_table(
    page, table_selector, should_include_row_headers
):
    """
    It takes a table selector, a boolean indicating whether or not to include the row headers, and
    returns a CSV string of the table

    :param page: the page object that you're working with
    :param table_selector: The CSS selector for the table you want to scrape
    :param should_include_row_headers: Whether or not the first row of the table should be included in
    the CSV string
    :return: A string of the table in csv format
    """
    # Initialize an empty string to store the table in CSV format
    csv_string = ""
    # Query the table using the table selector
    table = await page.query_selector(table_selector)
    # If the table isn't found, return None
    if not table:
        return None

    # Query all the rows in the table
    rows = await table.query_selector_all("tr")
    # Iterate through the rows
    for i, row in enumerate(rows):
        # If the row headers shouldn't be included and this is the first row, skip it
        if not should_include_row_headers and i == 0:
            continue
        # Query all the cells in the row
        cells = await row.query_selector_all("th,td")
        # Iterate through the cells
        for j, cell in enumerate(cells):
            # Get the text content of the cell
            cell_text = await cell.inner_text()
            # Replace any newlines in the cell text with \n
            formatted_cell_text = cell_text.replace("\n", "\\n").strip()
            # If the cell text isn't "No Data", add it to the CSV string
            if formatted_cell_text != "No Data":
                csv_string += formatted_cell_text
            # If this is the last cell, add a newline to the CSV string
            if j == len(cells) - 1:
                csv_string += "\n"
            # Otherwise, add a comma to the CSV string
            else:
                csv_string += ","
    # Return the CSV string
    return csv_string


async def main(playwright: Playwright) -> None:
    browser = await playwright.chromium.launch()
    page = await browser.new_page()
    await page.set_viewport_size({"width": 1920, "height": 1080})
    await page.goto("https://www.mta.maryland.gov/performance-improvement")

    await page.click("h3#ui-id-5")

    csv_string = ""

    route_select_selector = 'select[name="ridership-select-route"]'
    route_select_options = await page.evaluate(
        f'() => Array.from(document.querySelectorAll("{route_select_selector} > option")).map(option => option.value)'
    )
    print("routes available:", route_select_options)

    month_select_selector = 'select[name="ridership-select-month"]'
    month_select_options = await page.evaluate(
        f'() => Array.from(document.querySelectorAll("{month_select_selector} > option")).map(option => option.value)'
    )
    print("months available:", month_select_options)

    year_select_selector = 'select[name="ridership-select-year"]'
    year_select_options = await page.evaluate(
        f'() => Array.from(document.querySelectorAll("{year_select_selector} > option")).map(option => option.value)'
    )
    print("years available:", year_select_options)

    pbar = tqdm(
        total=len(month_select_options) * len(year_select_options), ncols=50
    )
    has_included_row_headers = True
    for year_select_option in year_select_options:
        await page.focus(year_select_selector)
        await page.select_option(
            year_select_selector, value=year_select_option
        )

        for month_select_option in month_select_options:
            await page.focus(month_select_selector)
            await page.select_option(
                month_select_selector, value=month_select_option
            )

            await page.keyboard.press("Tab")
            await page.keyboard.press("Tab")

            await asyncio.gather(
                page.keyboard.press("Enter"),
                page.wait_for_selector(
                    "div#container-ridership-table > table tbody tr"
                ),
            )

            csv_string += await compute_csv_string_from_table(
                page,
                "div#container-ridership-table > table",
                has_included_row_headers,
            )

            if has_included_row_headers:
                has_included_row_headers = False

            pbar.update(1)
    pbar.close()

    await browser.close()

    with open("mta-bus-ridership.csv", "w", newline="") as f:
        writer = csv.writer(f)
        for line in csv_string.splitlines():
            writer.writerow(line.split(","))


async def scrape_data():
    async with async_playwright() as playwright:
        await main(playwright)


if __name__ == "__main__":
    asyncio.run(scrape_data())
