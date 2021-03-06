from bs4 import BeautifulSoup
# import urllib.request as urllib2
import urllib2
import datetime
import re
import ast


def Weekdays():
    return ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

# Before September 1st 20XX year, the timetable displayed will be for the 20XX-1 -- 20XX academic year.
# On and after September 1st 20XX year, the timetable displayed will be for the 20XX -- 20XX+1 academic year.
def Get_url():
    now = datetime.datetime.now()
    if now.month < 9:
        ac_year_start = now.year % 100 - 1
    else:
        ac_year_start = now.year % 100
    return "http://web.inf.ed.ac.uk/infweb/student-services/ito/admin/timetables/lecture-timetable-20" + str(
        ac_year_start) + "-" + str(ac_year_start + 1)

# Get all course times and add a dash between them
def Get_times_list():
    url = Get_url()
    soup = BeautifulSoup(urllib2.urlopen(url).read(), "lxml")
    times = soup.table.thead.tr.find_all("th")
    times = times[1:]
    TIMES_LIST = []
    for time in times:
        start_time = time.text[0:4]
        end_time = time.text[-4:]
        TIMES_LIST.append(start_time + " - " + end_time)
    return TIMES_LIST


# Scrape the Course Codes webpage
def Get_course_dict():
    COURSE_DICT = {}
    url_course = "http://course.inf.ed.ac.uk/"
    soup_course = BeautifulSoup(urllib2.urlopen(url_course).read(), "lxml")
    course_table = soup_course.table.tbody.find_all("tr")

    for row in course_table:
        cols = row.find_all("td")
        col_list = []
        course_url = cols[0].find("a").get("href")
        lecturers = cols[11].find_all("a")
        lecturer_dict = {}
        for lecturer in lecturers:
            lecturer_dict[lecturer.get_text()] = lecturer.get("href")
        drps = cols[1].find("a").get("href")
        for col in cols:
            col_list.append(col.text)
        course_type = []
        for x in range(3, 7):
            if col_list[x]:
                course_type.append(col_list[x])

        COURSE_DICT[(col_list[2]).strip()] = {"course": col_list[0],
                                              "year": col_list[9],
                                              "credits": col_list[8],
                                              "course_url": course_url,
                                              "types": course_type,
                                              "drps": drps,
                                              "level": col_list[7],
                                              "semester": col_list[10][1],
                                              "lecturers": lecturer_dict
                                              }
    return COURSE_DICT

# Scrape the Venue Codes webpage
def Get_venue_dict():
    VENUE_DICT = {}
    url_venue = "http://web.inf.ed.ac.uk/infweb/student-services/ito/admin/venue-codes"
    soup_venue = BeautifulSoup(urllib2.urlopen(url_venue).read(), "lxml")
    building_and_room_codes = soup_venue.find("section", {"id": "block-system-main"}).find_all("ul")
    building_codes = building_and_room_codes[0].find_all("li")

    for building_code in building_codes:
        VENUE_DICT[building_code.find("strong").get_text().replace(" ", "")] = {
            "venue_name": building_code.find("a").get_text(),
            "venue_url": building_code.find("a").get("href")}
    return VENUE_DICT


# Create manually an additional dictionary with venues missing from the official Venue Codes webpage
def Get_alternate_venue_dict():
    ALTERNATE_VENUE_DICT = {
                            'EVOHSE':                    {'venue_url': 'http://www.ed.ac.uk/maps/maps?building=evolution-house',
                                                          'venue_name': 'Evolution House'},
                            'GSQ LT':                     {'venue_url': 'http://www.ed.ac.uk/maps/maps?building=george-square-lecture-theatre',
                                                          'venue_name': 'George Square Lecture Theatre'},
                            'Informatics Forum':         {'venue_url': 'http://www.ed.ac.uk/maps/maps?building=informatics-forum',
                                                          'venue_name': 'Informatics Forum'},
                            '21BP':                      {'venue_url': '',
                                                          'venue_name': '21 Buccleuch Place'},
                            'AH':                        {'venue_url': '',
                                                          'venue_name': 'Adam House'}
                           }
    return ALTERNATE_VENUE_DICT


# Create manually dictionary with the more cryptic room codes and their corresponding names
def Get_room_dictionary():
    ROOM_DICTIONARY = {
                         'LT1': 'Lecture Theatre 1',
                         'LT2': 'Lecture Theatre 2',
                         'LT3': 'Lecture Theatre 3',
                         'LT4': 'Lecture Theatre 4',
                         'LT5': 'Lecture Theatre 5',
                         'LHA': 'Lecture Hall A',
                         'LHB': 'Lecture Hall B',
                         'LHC': 'Lecture Hall C',
                         'SR1': 'Seminar Room 1',
                         'SR2': 'Seminar Room 2',
                         'SR3': 'Seminar Room 3',
                         'GSQ LT': 'George Square Lecture Theatre',
                         'RM 425 Anatomy LT': 'Anatomy Lecture Theatre, Doorway 3 (1.425)',
                         'Teviot LT': 'Meadows Lecture Theatre, Doorway 4 (G.07)',
                         'SSLT': 'Sydney Smith Lecture Theatre, Doorway 1 (2.520)',
                         'HRB LT': 'H.R.B Lecture Theatre',
                         'BLT LT': 'Basement Lecture Theatre'
    }
    return ROOM_DICTIONARY

# Scrapes and parses the page with JSON variables
def Get_UOE_venue_data():
    url = "http://webproxy.is.ed.ac.uk/web-proxy/maps_edweb/data.php"
    soup = BeautifulSoup(urllib2.urlopen(url).read(), "lxml")
    content = soup.get_text()
    var_list = content.split(";")
    var_list[1] = var_list[1].split("=")[1].strip()
    pointsOfInterest = ast.literal_eval(var_list[1])
    return pointsOfInterest

# Main content creator
def Get_content_dict():
    semesters_list = []
    soup = BeautifulSoup(urllib2.urlopen(Get_url()).read(), "lxml")
    tables = soup.find_all("table")
    for table in tables:
        semester_dict = {}
        contents = table.tbody.find_all("tr")
        for content in contents:
            row_items = content.find_all("td")
            first = True
            day_of_the_week = ""
            for row_item in row_items:
                if first:
                    semester_dict[row_item.text] = []
                    day_of_the_week = row_item.text
                    first = False
                else:
                    courses_that_hour = row_item.find_all(["p", "div"])
                    onlyOneCourseInTimeslot = False
                    if not (courses_that_hour):
                        courses_that_hour = [row_item]
                        onlyOneCourseInTimeslot = True
                    final_array_courses_that_hour = []
                    checkForCourseWithoutATag = True
                    for index, course_that_hour in enumerate(courses_that_hour):
                        ## if it contains a year in square brackets
                        if re.search("\[[0-9]\]", course_that_hour.text):
                            first_split = course_that_hour.text.split("[", 1)  # split on first square bracket
                            acronym = first_split[0].strip();
                            second_split = first_split[1].split("]", 1)
                            year = first_split[1].split("]", 1)[0].strip()
                            room = second_split[1].split(",", 1)[0].strip()
                            details = second_split[1].strip()
                            dict_course_that_hour = {'course_acr': acronym,
                                                     'course_year': year,
                                                     'course_details': details,
                                                     'course_room': room}
                            final_array_courses_that_hour.append(dict_course_that_hour)
                            if re.search("wk", details, re.IGNORECASE):
                                dict_course_that_hour['course_specific_weeks'] = True
                                if re.search("wk.*?wk", details, re.IGNORECASE):
                                    dict_course_that_hour['course_two_locations'] = True
                            ## if the course details have been separated to be in two <p> or <div> tags
                            if not room and len(courses_that_hour) >= index+2:
                                alternative_details = courses_that_hour[index+1].text
                                dict_course_that_hour['course_room'] = alternative_details.split(",")[0].strip()
                                dict_course_that_hour['course_details'] = alternative_details
                        ## after last element has been processed:
                        if index == len(courses_that_hour)-1 and checkForCourseWithoutATag and not(onlyOneCourseInTimeslot):
                            checkForCourseWithoutATag = False
                            emptied_row_item = row_item
                            for p_and_div_tags in emptied_row_item.find_all(['p', 'div']):
                                p_and_div_tags.clear()
                            courses_that_hour.append(emptied_row_item)
                    semester_dict[day_of_the_week].append(final_array_courses_that_hour)
        semesters_list.append(semester_dict)
    return semesters_list
