from django.shortcuts import render

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def wiki(request, title):
    page_name = title
    wiki_page = util.get_entry(title)
    if wiki_page:
        valueX = wiki_page
    else:
        valueX = False
    return render(request, "encyclopedia/wiki.html", {
        "value": valueX, "page_name": page_name
    })  

def add(request):
    if request.method == "POST":
        # request.POST - submited data 1.25 time in lecture
        valueX = True
    else:
        valueX = False
    return render(request, "encyclopedia/add.html", {
        "value": valueX
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