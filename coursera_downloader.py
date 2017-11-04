from selenium import webdriver
from selenium.webdriver.support import ui
from time import sleep
import urllib
import os
import csv

COURSERA_HOME = "C:\\Coursera\\"
COURSE_URL = "https://www.coursera.org/learn/introduction-to-software-product-management/home/welcome"
COURSE_NAME = "introduction-to-software-product-management"


class Video:
    def __init__(self, week_id=None, week_name=None, topic_id=None, topic_name=None, url=None):
        self.week_id = week_id
        self.week_name = week_name
        self.topic_id = topic_id
        self.topic_name = topic_name
        self.url = url


class Account:
    def __init__(self, email, password, course):
        self.email = email
        self.password = password
        self.course = course
        self.driver = webdriver.Chrome("C:\\Chromedriver\\chromedriver.exe")
        self.wait = ui.WebDriverWait(self.driver, 10)
        self.week_names = dict()
        self.topic_names = dict()
        self.videos = list()

    def login(self):
        self.driver.get("https://accounts.coursera.org/signin")
        self.driver.maximize_window()
        email = self.driver.find_element_by_id("signin-email")
        password = self.driver.find_element_by_id("signin-password")
        email.send_keys(self.email)
        password.send_keys(self.password)
        password.submit()

    def get_videos(self):
        if os.path.exists(COURSE_NAME.replace("-", "_") + "_video_urls.csv"):
            return
        videos = list()
        self.login()
        sleep(3)
        self.driver.get("https://www.coursera.org/learn/introduction-to-software-product-management/home/welcome")
        self.wait.until(
            lambda driver: self.driver.find_elements_by_xpath("//div[@class='rc-UngradedItemSection flex-4']//a"))
        weeks = self.driver.find_elements_by_xpath("//div[@class='rc-UngradedItemSection flex-4']//a")
        counter = 0
        week_urls = dict()
        for week in weeks:
            if counter % 2 == 0:
                # print(counter / 2 + 1, week.get_attribute("href"))
                week_id = int(counter / 2 + 1)
                week_url = str(week.get_attribute("href"))
                week_urls[week_id] = week_url
                self.week_names[week_id] = str(week_id) + "_" + week_url.split("/")[-1].replace("-", "_")
            counter += 1

        for week_id in week_urls.keys():
            print("Week:", week_id)
            self.driver.get(week_urls[week_id])
            self.wait.until(
                lambda driver: self.driver.find_elements_by_xpath("//ul[@class='rc-LessonItems nostyle']//a"))
            topics = self.driver.find_elements_by_xpath("//ul[@class='rc-LessonItems nostyle']//a")
            topic_urls = dict()
            for id, topic in enumerate(topics):
                topic_id = id + 1
                topic_url = topic.get_attribute("href")
                topic_urls[topic_id] = topic_url
                self.topic_names[topic_id] = str(topic_id) + "_" + topic_url.split("/")[-1].replace("-", "_")
                print("\tTopic:", topic_id, topic_url)

            for topic_id in topic_urls.keys():
                self.driver.get(topic_urls[topic_id])
                # sleep(5)
                self.wait.until(lambda driver: self.driver.find_element_by_xpath(
                    "//li[@class='rc-LectureDownloadItem resource-list-item']//a"))
                video = self.driver.find_element_by_xpath("//li[@class='rc-LectureDownloadItem resource-list-item']//a")
                video_url = video.get_attribute("href")
                # print("\t\tVideo:", video_url)
                # self.videos.append(Video(week_id, self.week_names[week_id], topic_id, self.topic_names[topic_id], video_url))
                videos.append([week_id, self.week_names[week_id], topic_id, self.topic_names[topic_id], video_url])
                print([week_id, self.week_names[week_id], topic_id, self.topic_names[topic_id], video_url])

        with open(COURSE_NAME.replace("-", "_") + "_video_urls.csv", "w") as f:
            for video in videos:
                f.write(",".join([str(v) for v in video]))
                f.write("\n")

    def download_videos(self):
        # url = urllib.request.urlopen(
        #     "https://d18ky98rnyall9.cloudfront.net/bLEZtq-LEeeCYRJSuVvCkA.processed/full/360p/index.mp4?Expires=1509753600&Signature=k0-mxhFUeJl41m2NpmBxWQR573ivlxgnLVGq~Bt1RZZpNUy9NqGu4wgcPPJGMIpa9o7SV1hT799rcjkVuyld1WitQnFt22zgSMKepTw1UGifttm8wLXI9VfLvnjbAveeRymm29~0~xBRQU9r9Cygj1LyZ~FoGY0JekeJDlF28BY_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A")
        # with open("first_video.mp4", "wb") as video_file:
        #     video_file.write(url.read())

        with open("video_urls.csv", "r") as url_file:
            reader = csv.reader(url_file)
            for video in reader:
                # print(video)
                self.videos.append(Video(video[0], video[1], video[2], video[3], video[4]))

        course_home = COURSERA_HOME + self.course
        if not os.path.isdir(course_home):
            os.mkdir(course_home)
        for week in self.week_names:
            week_home = course_home + "\\" + self.week_names[week]
            if not os.path.isdir(week_home):
                os.mkdir(week_home)

        for video in self.videos:
            print("Downloading: " + course_home + "\\" + video.week_name + "\\" + video.topic_name + ".mp4")
            url = urllib.request.urlopen(video.url)
            with open(course_home + "\\" + video.week_name + "\\" + video.topic_name + ".mp4", "wb") as video_file:
                video_file.write(url.read())


def main():
    coursera_account = Account("email@example.com", "password", COURSE_NAME)
    coursera_account.get_videos()
    coursera_account.download_videos()


if __name__ == '__main__':
    main()
