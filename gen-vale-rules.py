#!/usr/bin/python

#TODO: handle empty "incorrect forms" fields
#TODO: validate the rules
#TODO: Allow for capitalization in the terminology

import glob
import os
import re
import shutil
import requests, zipfile, io

def main():

    try: 

        #initialize some variables
        vale_rules_gen_dir = os.path.abspath(os.getcwd())
        adoc_dir = '/supplementary-style-guide-master/supplementary_style_guide/glossary_terms_conventions/general_conventions/' 
        out_dir = "SupplementaryStyleGuide"
        temp_dir = "temp"
        ssg_zip_url = "https://github.com/redhat-documentation/supplementary-style-guide/archive/refs/heads/master.zip"

        clean_old_build(vale_rules_gen_dir, out_dir)

        #grab the ssg source from github and unzip it to /temp
        get_ssg_source(temp_dir, ssg_zip_url)

        #scans *.adoc files in adoc_dir for word terms and creates vale rules for each incorrect word usage entry in vale_rules_gen_dir.
        create_vale_rules(vale_rules_gen_dir, adoc_dir, temp_dir, out_dir)

        #remove the temp folder                
        clean_up(vale_rules_gen_dir, temp_dir)

    except OSError as e:
        print(str(e))

    except getopt.GetoptError:
        #printUsage()
        sys.exit(2)

def clean_old_build(vale_rules_gen_dir, out_dir):
    if not os.path.exists(vale_rules_gen_dir + "/" + out_dir):
        os.makedirs(vale_rules_gen_dir + "/" + out_dir, exist_ok=True)
    files = glob.glob(vale_rules_gen_dir + "/" + out_dir + "/*")
    for f in files:
        os.remove(f)

def create_vale_rules(vale_rules_gen_dir, adoc_dir, temp_dir, out_dir):
    os.chdir(vale_rules_gen_dir + "/" + temp_dir + "/" + adoc_dir)
    for in_file in glob.glob("*.adoc"):
        in_file_folder = os.path.dirname(in_file)
        with open(in_file, 'r+', encoding='utf-8') as w:
            data = w.read()
            data = re.findall(r'\[\[(.*)\]\]\n(====) (.*) \(.*\)\n\*Description\*: (.*)\n\n\*Use it\*: yes\n\n\*Incorrect forms\*: (.*)', data) 
            for word_usage in data:
                word_id = word_usage[0]
                correct_form = word_usage[2]
                incorrect_forms = re.sub(r', ', '|', word_usage[4])
                #clean out yes/no image refs
                incorrect_forms = re.sub(r'image:images\/yes\.png\[yes\] ', '', incorrect_forms)
                incorrect_forms = re.sub(r'image:images\/no\.png\[no\] ', '', incorrect_forms) 
                correct_form = re.sub(r'image:images\/yes\.png\[yes\] ', '', correct_form)
                correct_form = re.sub(r'image:images\/no\.png\[no\] ', '', correct_form)
                #clean out other items
                incorrect_forms = re.sub(r' \(capitalized\)', '', incorrect_forms)
                incorrect_forms = re.sub(r', and so on', '', incorrect_forms)
                incorrect_forms = re.sub(r' \(without trademark symbol\)', '', incorrect_forms)
                incorrect_forms = re.sub(r' \(unless at the start of a sentence\).', '', incorrect_forms)
                #clean regex special characters hack - this needs to be handled correctly
                incorrect_forms = re.sub(r'\/', ' ', incorrect_forms)
                incorrect_forms = re.sub(r'\^', '', incorrect_forms)
                incorrect_forms = re.sub(r'\(', '\(', incorrect_forms)
                incorrect_forms = re.sub(r'\)', '\)', incorrect_forms)
                #create a word.yml for every word
                with open(word_id + ".yml", "w+", encoding='utf-8') as out_file:
                    out_file.write('---' + '\n')
                    out_file.write('extends: existence' + '\n')
                    out_file.write('message: Use "' + correct_form + '" instead of \'%s\'."' + '\n')
                    out_file.write('link: https://redhat-documentation.github.io/supplementary-style-guide/#' + word_id + '\n')
                    out_file.write('ignorecase: true' + '\n')
                    #only use nonword if a special character is present
                    if bool(re.search('\(|\)', str(incorrect_forms))) == True:
                        out_file.write('nonword: true' + '\n')
                    else:
                        out_file.write('nonword: false' + '\n')
                    out_file.write('level: error' + '\n')
                    out_file.write('source: SupplementaryStyleGuide' + '\n')
                    out_file.write('tokens:' + '\n')
                    out_file.write('    -  ' + incorrect_forms + '\n')
                    out_file.close()
                    #move the yml files to an output folder
                    for file in glob.glob("*.yml"):
                        shutil.move(os.path.abspath(file), vale_rules_gen_dir + "/" + out_dir + "/" + file)

def get_ssg_source(temp_dir, ssg_zip_url):
    r = requests.get(ssg_zip_url)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall(temp_dir)

def clean_up(vale_rules_gen_dir, temp_dir):
    shutil.rmtree(vale_rules_gen_dir + "/" + temp_dir)

if __name__ == "__main__":
    main()
