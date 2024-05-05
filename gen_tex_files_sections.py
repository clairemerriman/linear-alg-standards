#!/usr/bin/env python
import sys
from os.path import isfile 
from csv import DictReader
import re
import random


exam_name = 'MiniB'
first_section = 4 #0 for Mini Exam A for first section included
last_section = 4

master_template_path = 'main_template.tex'

# Sections that do not need a name printed at the top
# This could be all sections or the first one of a particular exam
# Depends on gradescope set up
SECTIONS_WITHOUT_NAME = {'section_R4'}


#Are there different versions?
#The code handles versioning by section
#Leave as [] if only one version
version_endings = []

# Paths to the relevant files and directories
def various_paths(exam_number):
    grade_path = f'standards{exam_number}.csv'
    template_path = f'template{exam_number}.tex'
    questions_dir = f'pool{exam_number}'
    output_dir = f'tests{exam_number}'
    return grade_path,template_path,questions_dir,output_dir


#To divide the standards by Mini(R0), Exam 1, Exam 2, etc
last_standard_R0 = 3
last_standard_R1 = 8
last_standard_R2 = 14
last_standard_R3 = 19
last_standard_R4 = 24 #there are in fact 24 standards

#Mini Exam heads and names
mini_a_number= 0
mini_b_number= 6



def various_paths(exam_number):
    grade_path = f'standards{exam_number}.csv'
    template_path = f'template{exam_number}.tex'
    questions_dir = f'pool{exam_number}'
    output_dir = f'tests{exam_number}'
    return grade_path,template_path,questions_dir,output_dir

def load_grade_data(grade_path):
    
    if not isfile(grade_path):
        sys.stdout.write("{0} does not exist.\n".format(grade_path))
        sys.exit()

    # use utf-8 encoding for the file reader to avoid errors related to
    # a BOM Excel adds to the beginning of any .csv
    with open(grade_path, encoding='utf-8-sig') as grade_file: 
        csv_table = DictReader(grade_file)

        student_data = {}
        
        for row in csv_table:
            student_id = row['ID']
            student_name = row['Name']
            student_grades = {column:value for column,value in row.items() if column not in ['ID','Name','Last Name']}

            student_data[student_id] = {}
            student_data[student_id]['Name'] = student_name
            student_data[student_id]['grades'] = student_grades


    return student_data


def generate_sections(section_list, question_sections, versions_list, name, student_grades, questions_dir):
    sections = section_list
    questions = question_sections
    versions = versions_list

    question_template = '\n\\setcounter{{question}}{{{question_id}-1}}\n\question \input{{../{question_file_name}}}\n'

    for question,grade in student_grades:
        if grade!='U':
            for i in range(first_section,last_section+1):
                if int(question) <= globals()[f'last_standard_R{i}']:
                    if versions:
                        version = versions[i-first_section]
                    else:
                        version = ''
                    question_file_name = f'{questions_dir}/{question}{exam_name}{version}.tex'

                    if isfile(question_file_name):
                
                        questions[f'questions_R{i}'] += question_template.format(question_id=question, question_file_name=question_file_name)
                        break
    for i in range(first_section,last_section+1):
        if questions[f'questions_R{i}']:
            #Add name at top of section if desired
            if f'section_R{i}' in SECTIONS_WITHOUT_NAME:
                sections[f'section_R{i}'] = ''
            else:
                sections[f'section_R{i}'] += f'{name}'
            
            #Add section heading, different for mini exams
            if i == mini_a_number:
                sections[f'section_R{i}']+= f'\n\\section*{{Mini Exam Standards}}'
            else:
                sections[f'section_R{i}']+= f'\n\\section*{{Exam {i} Standards}}'
            
            #Add questions
            sections[f'section_R{i}']+= '''\n\\begin{questions}'''
            # To make sure next section starts on a new piece of paper
            # Definition of blankpage in preamble
            # This allows separating sections for grading
            sections[f'section_R{i}'] += questions[f'questions_R{i}']
            sections[f'section_R{i}'] += '''
\\end{questions}
\\blankpage'''  
    
    return sections


def generate_tests(student_data, questions_dir, output_dir, template_path):
#     # Copy preamble.tex into output_dir
#     shutil.copy('preamble.tex', output_dir)


    with open(template_path) as template_file:
        template = template_file.read()
    
    
    for student_id in student_data:
        test_file_name = '{output}/{id}.tex'.format(output=output_dir,
                                                    id=student_id.zfill(2))
        grades = student_data[student_id]['grades'].items()
        name = student_data[student_id]['Name']

        sections = {}
        question_sections = {}
        versions = []
        for i in range(5):
            sections[f'section_R{i}'] = ''
            question_sections[f'questions_R{i}'] = ''

        for i in range(first_section,last_section+1):
            sections[f'section_R{i}'] = ''

            if version_endings:
                # Randomly choose a version for the section
                versions.append(random.choice(version_endings))

        section_content = generate_sections(sections,question_sections,versions,name, grades, questions_dir)

        section_variables = []
        # Turning sections into LaTeX variabls
        for section, content in section_content.items():
            locals()[section] = content
            section = locals()[section]
            section_variables.append(section)
        

        with open(test_file_name,'w') as test_file:
            test_content = template.format(name = name,
                                           section_R0 = section_variables[0],
                                           section_R1 = section_variables[1],
                                           section_R2 = section_variables[2],
                                           section_R3 = section_variables[3],
                                           section_R4 = section_variables[4])
            test_file.write(test_content)


def generate_master_file(student_data,output_dir, master_template_path):

    with open(master_template_path) as master_template_file:
        master_content = master_template_file.read()

    content = ''
    master_path = '{output}/main{exam}.tex'.format(output=output_dir, exam=exam_name)

    for student_id in student_data:
        content += '\\subfile{{{id}}}\n\\ \\\\\\clearpage\n'.format(id=student_id.zfill(2))
        
    with open(master_path,'w') as master_file:
        master_file.write(master_content.format(content=content))
    
# Finds the header by looking for \begin{document}
def find_header_doc(file):
    header = re.search(r'.*(?=\\begin{{document}})', file, re.S)
    return header.group(0)

def generate_blank_test(questions_dir, output_dir, template_path):

    with open(template_path) as template_file:
        template = template_file.read()
        #Only keep the body of the document
        template = re.search(r'\\begin{{document}}(.*?\\end{{document}})', template, re.S).group(0)

    # Use the header from the main template
    # This allows the blank test to be compiled one its own
    with open(master_template_path, 'r') as header_template_file:
        header_template_content = header_template_file.read()

    #Test template uses subfiles cls
    #main_template provides exam cls and preamble
    exam_cls_header = find_header_doc(header_template_content)

    # exam_cls_header = exam_cls_header.replace(r'\\', r'\\\\')


    template = exam_cls_header + '\\printanswers\n' + template 
    

    # generating blank grade data
    if first_section == 0:
        first_standard = 1
    else:
        first_standard = globals()[f'last_standard_R{first_section-1}'] +1

    last_standard =globals()[f'last_standard_R{last_section}']

    blank_data = {}
    blank_id = 'blank'
    blank_name = f'\\hrulefill'
    blank_grades = {str(i): 'X' for i in range(first_standard, last_standard+1)}

    blank_data[blank_id] = {}
    blank_data[blank_id]['Name'] = blank_name
    blank_data[blank_id]['grades'] = blank_grades

    grades = blank_data[blank_id]['grades'].items()

    sections = {}
    question_sections = {}
    versions = version_endings
        
    for i in range(5):
        sections[f'section_R{i}'] = ''

    for i in range(first_section,last_section+1):
        question_sections[f'questions_R{i}'] = ''

    if versions:
        for version in versions:
            for i in range(first_section,last_section+1):
                question_sections[f'questions_R{i}'] = ''
            test_file_name = '{output}/blank{exam}_Version{version}.tex'.format(output=output_dir,exam= exam_name,version=version)
            version_list = [version, version, version, version, version]
            section_content = generate_sections(sections,question_sections,version_list,blank_name, grades, questions_dir)

            section_variables = []
            # Turning sections into LaTeX variabls
            for section, content in section_content.items():
                locals()[section] = content
                section = locals()[section]
                section_variables.append(section)
        

            with open(test_file_name,'w') as test_file:
                test_content = template.format(name = blank_name,
                                               section_R0 = section_variables[0],
                                                section_R1 = section_variables[1],
                                                section_R2 = section_variables[2],
                                                section_R3 = section_variables[3],
                                                section_R4 = section_variables[4])
                test_file.write(test_content)
    
    else:
        test_file_name = f'{output_dir}/blank{exam_name}.tex'
        version_list = []
        section_content = generate_sections(sections,question_sections,version_list,blank_name, grades, questions_dir)

        section_variables = []
        # Turning sections into LaTeX variabls
        for section, content in section_content.items():
            locals()[section] = content
            section = locals()[section]
            section_variables.append(section)
        

        with open(test_file_name,'w') as test_file:
            test_content = template.format(name = blank_name,
                                           section_R0 = section_variables[0],
                                           section_R1 = section_variables[1],
                                           section_R2 = section_variables[2],
                                           section_R3 = section_variables[3],
                                           section_R4 = section_variables[4])
            return test_file.write(test_content)



if __name__=="__main__":
    grade_path,template_path,questions_dir,output_dir = various_paths(exam_name)
    student_data = load_grade_data(grade_path)
    generate_tests(student_data,questions_dir,output_dir,template_path) 
    generate_master_file(student_data,output_dir,master_template_path)
    generate_blank_test(questions_dir,output_dir,template_path)
