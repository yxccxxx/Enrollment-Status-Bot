import smtplib
import sys
import time
import requests

from bs4 import BeautifulSoup
from email.message import EmailMessage


# Replace the following items with your information
# Follow https://www.letscodemore.com/blog/smtplib-smtpauthenticationerror-username-and-password-not-accepted/ to retrieve gmail app password
YOUR_EMAIL = "YOUR_EMAIL@gmail.com"
YOUR_APP_PASSWORD = ""
YOUR_COURSES = ["CS 5356"]
YOUR_SEMESTER = "SP23"
YOUR_CHECK_FREQUENCY = 120  # 2 mins


def find_open_courses(courses):
    url = f"https://classes.cornell.edu/search/roster/{YOUR_SEMESTER}"
    headers = {
        "Referer": f"https://classes.cornell.edu/browse/roster/{YOUR_SEMESTER}",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"}

    open_courses = []
    for course in courses:
        subject, course_number = course.split()
        payload = {
            "q": course_number,
            "days-type": "any",
            "pi": ""}
        soup = BeautifulSoup(requests.get(url, headers=headers, params=payload).content, "lxml")

        course_full_name = soup.find("a", attrs={"href": f"/browse/roster/{YOUR_SEMESTER}/class/{subject}/{course_number}", "id": f"dtitle-{subject}{course_number}"})["aria-label"]
        print(f"Checking availability for {course_full_name} ...")

        sections = soup.find("div", attrs={"class": "node", "data-subject": subject, "data-catalog-nbr": course_number}).find("div",class_ = "sections")
        status = sections.find("span", attrs = {"class": lambda x: x and x.startswith("fa fa-")})
        enrollment_status = status["class"][2]
        if enrollment_status == "open-status-open":
            print(f"{course_full_name} is open!")
            open_courses.append(course_full_name)
        elif enrollment_status == "open-status-closed":
            print(f"{course_full_name} is closed.")
        else:
            print(f"{course_full_name}'s status is {enrollment_status}.")

    return open_courses


def send_email(open_courses, email, password):
    msg = EmailMessage()
    open_courses_str = ", ".join(open_courses)
    msg["Subject"] = f"{open_courses_str} enrollment is open!"
    msg["From"] = email
    msg["To"] = email
    msg.set_content(
        f"{open_courses_str} enrollment is open! Visit studentcenter.cornell.edu to enroll."
    )
    print(msg)

    s = smtplib.SMTP("smtp.gmail.com", 587)
    s.starttls()
    s.login(email, password)
    s.send_message(msg)
    s.quit()


def main():
    try:
        while True:
            open_courses = find_open_courses([YOUR_COURSES])
            if open_courses:
                send_email(open_courses, YOUR_EMAIL, YOUR_APP_PASSWORD)
            time.sleep(YOUR_CHECK_FREQUENCY)
    except KeyboardInterrupt:
        sys.exit()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit()