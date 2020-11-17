import re

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django import forms

def list_entries():
    """
    Returns a list of all names of encyclopedia entries.
    """
    _, filenames = default_storage.listdir("entries")
    return list(sorted(re.sub(r"\.md$", "", filename)
                for filename in filenames if filename.endswith(".md")))


def save_entry(title, content):
    """
    Saves an encyclopedia entry, given its title and Markdown
    content. If an existing entry with the same title already exists,
    it is replaced.
    """
    filename = f"entries/{title}.md"
    if default_storage.exists(filename):
        default_storage.delete(filename)
    default_storage.save(filename, ContentFile(content))


def get_entry(title):
    """
    Retrieves an encyclopedia entry by its title. If no such
    entry exists, the function returns None.
    """
    try:
        f = default_storage.open(f"entries/{title}.md")
        return f.read().decode("utf-8")
    except FileNotFoundError:
        return None

def compress_newlines(text):
    template = re.compile(r'[\n\r][\n\r][\n\r]')
    text = template.sub('\n', text)
    return text

def md_to_html(text):
    """
    Returns text with html.
    """
    text = head_html(text)
    text = link_html(text)
    text = b_html(text)
    text = ul_html(text) 
    text = p_html(text)
    return text

def b_html(text):
    bold = re.compile(r'\*\*')
    bold_len = len(bold.findall(text))
    if (bold_len == 0 or bold_len == 1):
        pass
    else:
        shatter = bold.split(text)
        non_bold_part = False
        if (bold_len % 2) == 1:
            non_bold_part = shatter.pop()
        line_switch = False
        formated = []
        for line in shatter:
            if line_switch:
                line_switch = False
                formated.append('<b>' + line + '</b>')
            else:
                line_switch = True
                formated.append(line)

        text = ''.join(formated)
        if non_bold_part:
            text += '**' + non_bold_part
    return text

def link_html(text):
    link = re.compile(r'\[.[^\s]+\]\([\w\?/:]+\)')
    link_name_template = re.compile(r'\[.[^\s]+\]')
    link_route_template = re.compile(r'\([\w\?/:]+\)')
    if link.search(text):
        link_list = link.findall(text)
        for link_tag in link_list: 
            link_name = link_name_template.search(link_tag)
            link_route = link_route_template.search(link_tag)
            compiled_link = f'<a href="{link_route.group()[1:-1]}">{link_name.group()[1:-1]}</a>'     
            text = text.replace(link_tag, compiled_link)
    return text

def head_html(text):
    head_template = re.compile('#+ .+')
    head_size_template = re.compile('#+')
    if head_template.search(text):
        head_list = head_template.findall(text)
        for head_tag in head_list:
            head_size = str(len(head_size_template.search(head_tag).group()))
            slice_chara = 1 + int(head_size)
            sliced_head_tag = head_tag[slice_chara:(len(head_tag))]
            compiled_head =  '<h{}>{}</h{}><br>'.format(head_size, sliced_head_tag.strip("\t\n\r\f\v"), head_size)
            text = text.replace(head_tag, compiled_head, 1)
    return text


def ul_html(text):
    ul_template = re.compile(r'[\*-]+ .+')
    op_li = '<li>'
    end_li = '</li>'
    if ul_template.search(text):
        ul_list = ul_template.findall(text)
        for li_tag in ul_list:
            compiled_li = '{}{}{}'.format(op_li, li_tag[2:].strip('\n\r'), end_li)
            if li_tag == ul_list[0]:
                compiled_li = f'<ul>{compiled_li}'
            if li_tag == ul_list[-1]:
                compiled_li = f'{compiled_li}</ul>'
            text = text.replace(li_tag, compiled_li, 1)
    return text

def p_html(text):
    tag_template = re.compile(r'\<ul\>|\<h[1-9]\>')
    text = text.strip('\n\r')
    newlines_template = re.compile(r'[\n\r]{2,}')
    splitted_text = re.split(newlines_template, text)
    p_text = ''
    for part in splitted_text:
        if tag_template.search(part):
            p_list = tag_template.findall(part)
            for p_tag in p_list:
                tempo_part_list = part.split(p_tag, 1)
                if tempo_part_list[0] == '':
                    p_text = '{}{}'.format(p_text, part)
                else:
                    tempo_part_str = tempo_part_list[0] + '</p>' + p_tag + tempo_part_list[1]
                    p_text = '{}<p>{}'.format(p_text, tempo_part_str)
                break
        else:  
            p_text = '{}<p>{}</p>'.format(p_text, part)
    if p_text != '':
        text = p_text
    return text