import re

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


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

def md_to_html(text):
    """
    Returns text with html.
    """
    #print('md_to_html initial: ' + text)
    text = head_html(text)
    #print('md_to_html after head_html: ' + text)  
    text = link_html(text)
    #print('md_to_html after link: ' + text)
    text = b_html(text)
    #print('md_to_html after b_html: ' + text)
    text = ul_html(text)
    #print('md_to_html after ul_html: ' + text)  
    text = p_html(text)
    print('md_to_html after p_html: ' + text) 
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
            compiled_head = f'<h{head_size}>{head_tag[slice_chara:]}</h{head_size}><br>'
            text = text.replace(head_tag, compiled_head, 1)
    return text


def ul_html(text):
    ul_template = re.compile(r'[\*-]+ .+')
    if ul_template.search(text):
        ul_list = ul_template.findall(text)
        for li_tag in ul_list:
            compiled_li = '<li>{}</li>'.format(li_tag[2:])
            if li_tag == ul_list[0]:
                compiled_li = f'<ul>{compiled_li}'
            if li_tag == ul_list[-1]:
                compiled_li = f'{compiled_li}</ul>'   
            text = text.replace(li_tag, compiled_li, 1)
    return text


def p_html(text):
    p_template = re.compile(r'[\n\r][\n\r].+\<u|[\n\r][\n\r].+[\n\r][\n\r]|[\n\r][\n\r].+\<h', flags=re.DOTALL)

    if p_template.search(text):
        p_list = p_template.findall(text)
        for p_tag in p_list:
            print('PTAG: ' + p_tag)
            compiled_p = '<p>{}</p>'.format(p_tag[2:-2])
            text = text.replace(p_tag, compiled_p, 1)
    return text