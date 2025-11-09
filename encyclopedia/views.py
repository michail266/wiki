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
        return render (request,"encyclopedia/errors/findError.html",{
            "message":f"The requested \"{title}\" wiki, was not found."
        })
    
    content_html= markdown2.markdown(content)
    return render(request,"encyclopedia/entry.html",{
        "title":title,
        "content":content_html
    })

def search(request):
    query=request.GET.get("q","")
    entries=util.list_entries()
    if query in entries:   
      return render(request,"encyclopedia/entry.html",{
           "title":query,
          "content":markdown2.markdown(util.get_entry(query))
        })
    
    suggestions=[entry for entry in entries if query.lower() in entry.lower()]
    if not suggestions:
        return render (request,"encyclopedia/errors/findError.html",{
            "message":f"No search results found for \"{query}\"."
        })
    return render(request,"encyclopedia/errors/searchError.html",{
        "suggestions":suggestions
        })


