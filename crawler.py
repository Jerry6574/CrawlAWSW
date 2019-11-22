import os
import requests
import bs4
import numpy as np
import pandas as pd
import utils
import timeit


def get_product_attrib(pn):
    """
    get_product_attrib acquires product attribute from http://www.assmann-wsw.com/.
    :param pn: a tuple or list with signature [country_code, part_number]
    :return: product_attrib, a numpy array.
    """

    # Initialize product attributes.
    product_link = '#NA'
    img_link = '#NA'
    datasheet_link = "#NA"

    wsw_home_page = "http://www.assmann-wsw.com/"
    url_p2 = "&artnr-search=find+now#searchresults"

    print('Processing PN:', pn)

    # US version WSW website
    url_p1_us = "http://www.assmann-wsw.com/us/en/artikelfinder/?artnr="

    # Germany version WSW website
    url_p1_de = "http://www.assmann-wsw.com/wo/en/artikelfinder/?artnr="

    # If part number is a numeric type, convert to string.
    try:
        search_url_us = url_p1_us + pn + url_p2
        search_url_de = url_p1_de + pn + url_p2
    except TypeError:
        search_url_us = url_p1_us + str(pn) + url_p2
        search_url_de = url_p1_de + str(pn) + url_p2

    target_artnr = None

    all_artnr = parse_product_search_page(search_url_us)
    if not all_artnr:
        all_artnr = parse_product_search_page(search_url_de)
        if not all_artnr:
            pass

    # Part number exists and is not a substring of other part numbers.
    if len(all_artnr) == 1:
        target_artnr = all_artnr[0]

    # Part number exists and is a substring of other part numbers.
    # Iterate through every returned part number to find exact match.
    else:
        for artnr in all_artnr:
            # Replace "Non-breaking Hyphen"('\u2011') with '-' to have correct string comparison.
            if artnr.text.replace('\u2011', '-') == pn.replace('\u2011', '-'):
                target_artnr = artnr

    try:
        product_link = wsw_home_page + target_artnr.find('a')['href']
        img_link = wsw_home_page + target_artnr.previous_element['src']
        datasheet_link = wsw_home_page + target_artnr.find_next('a', {'title': 'PDF download'})['href']
        # print(datasheet_link)

    except (TypeError, UnboundLocalError, AttributeError):
        pass

    product_attrib = np.array([pn, product_link, img_link, datasheet_link])
    return product_attrib


def parse_product_search_page(search_url):
    """
    parse_product_search_page acquires a list of bs4 td tags of 'class': 'artnr'.
    :param search_url: url of a part number search
    :return: all_artnr: a list of bs4 td tags of 'class': 'artnr'.
    """
    src = requests.get(search_url).content
    soup = bs4.BeautifulSoup(src, 'lxml')
    all_artnr = soup.find_all('td', attrs={'class': 'artnr'})

    return all_artnr


def get_prod_links(pn_path, prodlink_path):
    """
    get_n_product_attrib performs the get_product_attrib function on multiple inputs.
    :param pn_path: path to Excel file contains part_number column.
    :param prodlink_path: Path to export an Excel file containing a table of product attributes.
    """
    pn_list = pd.read_excel(pn_path)["WSW_PN"].tolist()
    n_product_attrib = utils.mp_func(get_product_attrib, pn_list, has_return=True)
    n_prod_attrib_df = pd.DataFrame(n_product_attrib, columns=['PN', 'Product Link', 'Image Link', "Datasheet"])
    n_prod_attrib_df.to_excel(prodlink_path)


def main():
    start = timeit.default_timer()

    pn_path = "pn.xlsx"
    prodlink_path = "prod_link.xlsx"
    get_prod_links(pn_path, prodlink_path)

    stop = timeit.default_timer()

    print('Time: ', stop - start, " seconds")


if __name__ == '__main__':
    main()
