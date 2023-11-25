from bs4 import BeautifulSoup
from pymongo import MongoClient

# MongoDB setup
client = MongoClient("mongodb://<username>:<password>@<host>:<port>/<database>")  
db = client["web_crawler"]
professors_collection = db["professors"]

def parse_faculty_info(html):
    soup = BeautifulSoup(html, "html.parser")
    faculty_info = []

    # Assuming the faculty information is structured in a certain way on the page.
    # Modify this part according to the actual structure of the HTML.
    faculty_blocks = soup.find_all("div", class_="clearfix")

    for block in faculty_blocks:
        name = block.find("h2").text.strip()

        # Extracting other information
        title = block.select_one("p strong:contains('Title')").next_sibling.strip()
        office = block.select_one("p strong:contains('Office')").next_sibling.strip()
        phone = block.select_one("p strong:contains('Phone')").next_sibling.strip()
        email = block.select_one("p strong:contains('Email')").next_sibling.strip()
        website = block.select_one("p strong:contains('Web')").next_sibling.find("a")["href"].strip()

        faculty_info.append({
            "name": name,
            "title": title,
            "office": office,
            "phone": phone,
            "email": email,
            "website": website
        })

    return faculty_info


def persist_faculty_data(data):
    for professor_data in data:
        professors_collection.insert_one(professor_data)

def find_permanent_faculty_page():
    # Modify this based on the actual URL structure or content in your MongoDB
    target_url = "https://www.cpp.edu/sci/computerscience/faculty-and-staff/permanent-faculty.shtml"
    page = db.pages.find_one({"url": target_url})

    if page:
        return page["html"]

    return None

def main():
    # If you couldn't finish question 4 properly, you can directly include the HTML data
    # of the Permanent Faculty page in MongoDB.
    faculty_html = find_permanent_faculty_page()

    if faculty_html:
        faculty_data = parse_faculty_info(faculty_html)
        persist_faculty_data(faculty_data)
        print("Faculty information parsed and persisted successfully.")
    else:
        print("Permanent Faculty page HTML not found in MongoDB. Please check your data.")

if __name__ == "__main__":
    main()
