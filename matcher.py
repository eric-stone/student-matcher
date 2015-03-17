def importfromspreadsheetcsvfiles():
    """
    This function reads input from csv files in a hard coded location
    For stand alone testing only
    This function will be removed upon integration with the canonical data sources
    """
    import pandas as pd

    studentsFile = '/home/user/HOME/Dropbox/documents-export-2015-03-04/students.csv'
    teachersFile = '/home/user/HOME/Dropbox/documents-export-2015-03-04/teachers.csv'

    studentsdf = pd.read_csv(studentsFile)
    teachersdf = pd.read_csv(teachersFile)

    timeKeys = ('M420', 'M500', 'M540', 'M620', 'M700',
                'T420', 'T500', 'T540', 'T620', 'T700',
                'W420', 'W500', 'W540', 'W620', 'W700',
                'R420', 'R500', 'R540', 'R620', 'R700',
                'F420', 'F500', 'F540', 'F620', 'F700')

    students = {}
    for rowNum in range(1, len(studentsdf)):
        studentID = studentsdf.iloc[rowNum, 1]
        studentIDs.append(studentID)
        students[studentID] = {}
        students[studentID]['name'] = str(studentsdf.iloc[rowNum, 2]) + " " + str(studentsdf.iloc[rowNum, 3])
        students[studentID]['instruments'] = [
            str(studentsdf.iloc[rowNum, 16]).lower().strip(),
            str(studentsdf.iloc[rowNum, 17]).lower().strip(),
            str(studentsdf.iloc[rowNum, 18]).lower().strip(),
        ]
        students[studentID]['language'] = [x.lower().strip() for x in str(studentsdf.iloc[rowNum, 44]).split()]
        students[studentID]['times'] = []
        for i in range(54, 79):
            if studentsdf.iloc[rowNum, i] == 'Y':
                students[studentID]['times'].append(timeKeys[i - 54])

    teachers = {}
    for rowNum in range(1, len(teachersdf)):
        teacherID = teachersdf.iloc[rowNum, 1]
        teacherIDs.append(teacherID)
        teachers[teacherID] = {}
        teachers[teacherID]['name'] = str(teachersdf.iloc[rowNum, 3]) + " " + str(teachersdf.iloc[rowNum, 4])
        teachers[teacherID]['instruments'] = [x.lower().strip() for x in str(teachersdf.iloc[rowNum, 15]).split()]
        teachers[teacherID]['language'] = ['english' if x == 'nan' else x.lower().strip() for x in
                                           str(teachersdf.iloc[rowNum, 19]).split()]
        teachers[teacherID]['times'] = []
        for i in range(32, 57):
            if teachersdf.iloc[rowNum, i] == 'Y':
                teachers[teacherID]['times'].append(timeKeys[i - 32])

    inPotentialMatches = set()

    for student in students.keys():
        for teacher in teachers.keys():
            for time in students[student]['times']:
                if time in teachers[teacher]['times']:
                    langs = set(students[student]['language']).intersection(set(teachers[teacher]['language']))
                    if len(langs) > 0:
                        insts = set(students[student]['instruments']).intersection(
                            set(teachers[teacher]['instruments']))
                        if len(insts) > 0:
                            if (student, teacher) not in inPotentialMatches:
                                inPotentialMatches.add((student, teacher))
                                potentialMatches.append([student, teacher, time, langs, insts])


studentIDs = []
teacherIDs = []
potentialMatches = []

importfromspreadsheetcsvfiles()


def potentialmatchesbyteacher(teacher):
    lst = [pmt[0] for pmt in potentialMatches if pmt[1] == teacher]
    lst.sort()
    return lst


def potentialmatchesbystudent(student):
    lst = [pms[1] for pms in potentialMatches if pms[0] == student]
    lst.sort()
    return lst


matches = set()


def ismatched(someone):
    for (match_s, match_t) in matches:
        if someone == match_s or someone == match_t:
            return True
    return False


def matchpair(student, teacher):
    global matches

    assert student in studentIDs
    assert teacher in teacherIDs

    for matched_s, matched_t in matches:
        assert matched_s != student, str(matched_s) + " already matched"
        assert matched_t != teacher, str(matched_t) + " already matched"

    matches.add((student, teacher))


def unmatch(someone):
    global matches

    for ms, mt in matches:
        if someone == ms or someone == mt:
            matchToRemove = (ms, mt)
            matches.remove(matchToRemove)
            return
    assert False, "unable to unmatch: " + str(someone) + " from " + str(matches)


def getMatch(someone):
    global matches

    for (ms, mt) in matches:
        if someone == ms:
            return mt
        if someone == mt:
            return ms
    return False


def requestPush(newStudent, teacher, priorPath):
    currentStudent = getMatch(teacher)

    if teacher in priorPath:
        return
    priorPath.append(teacher)

    if ismatched(newStudent):
        return

    pm = [tt for tt in potentialmatchesbystudent(currentStudent)]
    for tt in pm:
        unmatch(currentStudent)
        requestPush(currentStudent, tt, priorPath)
        if not ismatched(currentStudent):
            matchpair(currentStudent, teacher)

    if not ismatched(teacher):
        matchpair(newStudent, teacher)
        return


for s in studentIDs:
    for t in potentialmatchesbystudent(s):
        requestPush(s, t, list())

print "Matches Found:"
matchesFound = [(s, t) for s, t in matches]
matchesFound.sort()
for (s, t) in matchesFound:
    print s + " matched with " + t
print "\nmatched teachers = " + str(len(matches)) + "/" + str(len(teacherIDs)) + " " + str(
    float(len(matches)) / len(teacherIDs))
print "matched students = " + str(len(matches)) + "/" + str(len(studentIDs)) + " " + str(
    float(len(matches)) / len(studentIDs))
