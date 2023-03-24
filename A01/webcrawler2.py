import argparse
import json
from utils import *

PAGE_SIZE = 2000

def get_paginated_url(url: str):
    """
    Description:
        Checks if the given URL has pagination.

    Parameters:
        url (str): The URL to check.

    Returns:
        str: The URL with pagination.
    """
    soup = get_content(url)
    pagination = soup.find("button", id="gsc_bpf_more")
    if (pagination):
        paginated_url = url + f"&cstart=20&pagesize={PAGE_SIZE}"
        return paginated_url

    return


def get_paginated_content(paginated_url: str):
    """
    Description:
        Returns the parsed content of the page at the given URL.

    Parameters:
        paginated_url (str): The URL of the page to retrieve.

    Returns:
        list: A list of dictionaries containing the paper title, authors, journal, citedby, and year.
    """
    soup = get_content(paginated_url)
    paginated_researcher_paper_dict = []
    for paper in soup.find_all("tr", class_="gsc_a_tr"):
        paginated_researcher_paper_dict.append({
            "paper_title": paper.find("a", class_="gsc_a_at").get_text(),
            "paper_authors": paper.find_all("div", {"class": "gs_gray"})[0].get_text(),
            "paper_journal": paper.find_all("div", {"class": "gs_gray"})[1].get_text().split(",")[0].strip(""),
            "paper_citedby": paper.find("a", class_="gsc_a_ac gs_ibl").get_text(),
            "paper_year": paper.find("span", class_="gsc_a_h gsc_a_hc gs_ibl").get_text()
        })

    return paginated_researcher_paper_dict


def get_parsed_content(url: str):
    """
    Description:
        Returns the parsed content of the page at the given URL.

    Parameters:
        url (str): The URL of the page to retrieve.

    Returns:
        dict: A dictionary containing the researcher name, caption,
        institution, keywords, image URL, citations, h-index, i10-index, coauthors, and papers.
    """
    soup = get_content(url)
    researcher_name = soup.find("div", id="gsc_prf_in").contents[0]
    researcher_caption = soup.find("div", class_="gsc_prf_il").contents[0].strip(", ")
    researcher_institution = soup.find("a", class_="gsc_prf_ila").contents[0]
    researcher_keywords = [keywords.get_text() for keywords in soup.find_all("a", class_="gsc_prf_inta gs_ibl")]
    researcher_imgURL = soup.find("img", id="gsc_prf_pup-img")["src"]
    researcher_citations = [citations.get_text() for citations in soup.find_all("td", class_="gsc_rsb_std")[0:2]]
    researcher_hindex = [hindex.get_text() for hindex in soup.find_all("td", class_="gsc_rsb_std")[2:4]]
    researcher_i10index = [i10index.get_text() for i10index in soup.find_all("td", class_="gsc_rsb_std")[4:6]]
    researcher_coauthor_content = soup.find_all("span", class_="gsc_rsb_a_desc")

    researcher_coauthor_dict = []
    for coauthor in researcher_coauthor_content:
        researcher_coauthor_dict.append({
            "coauthor_name": coauthor.find("a").get_text(),
            "coauthor_title": coauthor.find("span", class_="gsc_rsb_a_ext").get_text(),
            "coauthor_link": coauthor.find("a", href=True)["href"]
        })

    researcher_paper_dict = []
    for paper in soup.find_all("tr", class_="gsc_a_tr"):
        researcher_paper_dict.append({
            "paper_title": paper.find("a", class_="gsc_a_at").get_text(),
            "paper_authors": paper.find_all("div", {"class": "gs_gray"})[0].get_text(),
            "paper_journal": paper.find_all("div", {"class": "gs_gray"})[1].get_text().split(",")[0].strip(""),
            "paper_citedby": paper.find("a", class_="gsc_a_ac gs_ibl").get_text(),
            "paper_year": paper.find("span", class_="gsc_a_h gsc_a_hc gs_ibl").get_text()
        })

    return researcher_name, researcher_caption, researcher_institution, \
        researcher_keywords, researcher_imgURL, researcher_citations, \
        researcher_hindex, researcher_i10index, researcher_coauthor_dict, researcher_paper_dict


def combine_paper_lists(researcher_paper_dict: list, paginated_researcher_paper_dict: list):
    """
    Description:
        Combines the two lists of papers.

    Parameters:
        researcher_paper_dict (list): The list of papers.
        paginated_researcher_paper_dict (list): The list of papers.

    Returns:
        list: A list of dictionaries containing the paper title, authors, journal, citedby, and year.
    """
    for paper in paginated_researcher_paper_dict:
        researcher_paper_dict.append(paper)

    return researcher_paper_dict


def write_json_data(content: str, url: str):
    """
    Description:
        Writes the content to a file with hashed name.

    Parameters:
        content (str): The content to write to the file.
        url (str): The URL of the page to retrieve.
    """
    parsed_content = get_parsed_content(url)
    paginated_researcher_paper_dict = get_paginated_content(get_paginated_url(url))
    research_papers = combine_paper_lists(parsed_content[9], paginated_researcher_paper_dict)
    content_dict = {
        "researcher_name": parsed_content[0],
        "researcher_caption": parsed_content[1],
        "researcher_institution": parsed_content[2],
        "researcher_keywords": parsed_content[3],
        "researcher_imgURL": parsed_content[4],
        "researcher_citations": {"all": parsed_content[5][0], "since2018": parsed_content[5][1]},
        "researcher_hindex": {"all": parsed_content[6][0], "since2018": parsed_content[6][1]},
        "researcher_i10index": {"all": parsed_content[7][0], "since2018": parsed_content[7][1]},
        "researcher_coauthors": parsed_content[8],
        "researcher_papers": research_papers
    }

    filename = "data/" + hash_url(url) + ".json"
    with open(filename, "w") as f:
        f.write(json.dumps(content_dict, indent=4))

    return


def main():
    """
    Description:
         Main function.

    Usage:
         python3 webcrawler2.py <url>
    """
    parser = argparse.ArgumentParser(prog="Web Crawler #2", description="Google Scholar Profile Crawler.")
    parser.add_argument("url", help="The URL of the page to retrieve.")
    args = parser.parse_args()

    if (not args.url):
        print("Error. No URL argument provided.")
        return

    session_handler()
    print_giraffe()
    print_loading()

    url = args.url
    content = get_content(url).prettify()

    if (content):
        write_raw_data(content, url)
        write_json_data(content, url)
    else:
        print("Error. Unable to retrieve this flaming heap of garbage.")

    return


if (__name__ == "__main__"):
    main()
