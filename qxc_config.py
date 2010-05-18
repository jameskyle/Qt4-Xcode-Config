#!/opt/local/bin/python

# Script expects xml formated project.pbxproj file
#  plutil -convert xml1 project.pbxproj

import sys
import os
import plistlib

def qmake(q_cmd="/usr/local/Trolltech/Qt-4.7.0/bin/qmake"):
    from subprocess import Popen, PIPE
    out = Popen([q_cmd, "-spec", "macx-xcode"], stdout=PIPE).communicate()[0]
    print("qmake output: {0}".format(out))

def get_project_file(proj_filename = "project.pbxproj"):
    import glob

    pfile = None
    xcode_projects = glob.glob(os.path.join("./", "*.xcodeproj"))
    proj_file = None

    if len(xcode_projects) <= 0:
        print("No Xcode projects found in current path.")
        exit()
    elif len(xcode_projects) == 1:
        project = xcode_projects[0]
        proj_file = os.path.join(project, proj_filename)
    else:
        for proj in xcode_projects:
            print("{0} {1}".format(xcode_projects.index(proj) + 1, proj))
        sys.stdout.write("Please enter the number of the project "
                         "you wish to customize: ")
        index = int(raw_input()) - 1

        proj_file = os.path.join(xcode_projects[index],
                                         proj_filename)

    return proj_file

def convert_to_xml(proj_file):
    from subprocess import Popen, PIPE

    convert = ["plutil", "-convert", "xml1", proj_file]

    try:
        output = Popen(convert, stdout=PIPE).communicate()[0]
    except IOError, e:
        print(e)

    if len(output) != 0:
        print(output)
        exit()

def yaml_config(yaml_file):
    import yaml
    data = None
    with open(yaml_file) as f:
        data = yaml.load(f)
    return data

def parse_plist(proj_file):
    convert_to_xml(proj_file)

    try:
        plist = plistlib.readPlist(proj_file)

    except IOError, e:
        print(e)

    return plist

def modify_plist(plist, conf):
    pbxproj = plist["objects"][plist["rootObject"]]
    build_conf_list = plist["objects"][pbxproj["buildConfigurationList"]]

    # this is going to be a list of UID's for active xcode project confs
    conf_list = build_conf_list["buildConfigurations"]

    # build a hash of build configs with name as key

    for key in conf["pbxproject"].keys():
        pbxproj[key] = conf["pbxproject"][key]

    for build_key in conf_list:
        build_conf = plist["objects"][build_key]
        name = build_conf["name"]
        print("Found: {0}, key: {1}".format(name, build_key))

        if conf.has_key(name):
            for key in conf[name].keys():
                build_conf["buildSettings"][key] = conf[name][key]

    return plist


def main():
    proj_file = None
    # first run qmake
    qmake()
    if len(sys.argv) > 1:
        proj_file = sys.argv[1]
    else:
        proj_file = get_project_file()

    if not proj_file:
        print("[undefined error] No project file found!")
        exit()

    print("Configuring: {0}".format(proj_file))
    conf = yaml_config("xcode.yaml")

    if not conf:
        sys.stderr.write("Failed to load yaml config\n")
        exit()

    plist = parse_plist(proj_file)

    plist = modify_plist(plist, conf)

    plistlib.writePlist(plist, proj_file)

if __name__  == "__main__":
    main()



