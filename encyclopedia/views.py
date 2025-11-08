from django.shortcuts import render
import markdown2

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    content=util.get_entry(title)
    if content is None:
        return render (request,"encyclopedia/error.html",{
            "message":f"The requested {title}  page was not found."
        })
    
    content_html= markdown2.markdown(content)
    return render(request,"encyclopedia/entry.html",{
        "title":title,
        "content":content_html
    })