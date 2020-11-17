from django.shortcuts import render
from random import choice

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def wiki(request, title):
    wiki_page = util.get_entry(title)
    if wiki_page:
        wiki_page = util.compress_newlines(wiki_page)
        wiki_page = util.md_to_html(wiki_page)
    else:
        wiki_page = False
    return render(request, "encyclopedia/wiki.html", {
        "wiki_page": wiki_page, "page_name": title
    })  


def edit(request, title):
    if request.method == "POST":
        content = request.POST['content']
        util.save_entry(title, content)
        return wiki(request, title)
    get_content = util.get_entry(title)
    wiki_content = util.compress_newlines(get_content)
    return render(request, "encyclopedia/edit.html", {
            "wiki_title": title, "wiki_content": wiki_content
        })


def new(request):
    if request.method == "POST":
        wiki_title = request.POST['title']
        wiki_content = request.POST['content']
        if wiki_title == '':
            message = 'Article name field is blank.'
            return error(request, message)
        if not util.get_entry(wiki_title):
            util.save_entry(wiki_title, wiki_content)
            return wiki(request, wiki_title)
        message = 'Article already exist.'
        return error(request, message)
    return render(request, "encyclopedia/new.html")

def new_title(request, title):
    if request.method == "POST":
        wiki_title = request.POST['title']
        wiki_content = request.POST['content']
        if not util.get_entry(wiki_title):
            util.save_entry(wiki_title, wiki_content)
            return wiki(request, wiki_title)
        message = 'Article already exist.'
        return error(request, message)
    return render(request, "encyclopedia/new.html", {
            "wiki_title": title
        })



def search(request):
    if request.method == "POST":
        wiki_page = request.POST['q']
        if util.get_entry(wiki_page):
            return wiki(request, wiki_page)
        else:
            search_list = []
            all_pages = util.list_entries()
            for page in all_pages:
                if (page.lower().find(wiki_page.lower()) + 1):
                    search_list.append(page)
            return render(request, "encyclopedia/search.html", {
                "search_list": search_list, "wiki_page": wiki_page
            })
    else:
        return index(request)


def random(request):
    return wiki(request, choice(util.list_entries()))

def error(request, message):
    return render(request, "encyclopedia/error.html", {
        "message": message
    })
