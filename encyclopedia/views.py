from django.shortcuts import render
from django import forms
from django.core.exceptions import ValidationError
import markdown2

from . import util

class NewPageForm(forms.Form):
    #this helped a lot https://docs.djangoproject.com/en/5.2/ref/forms/widgets/
    title = forms.CharField(label="Title", max_length=20)
    content = forms.CharField(label="Content", widget=forms.Textarea(attrs={
        "style":"height: 300px; width: 600px;"
    
    }))

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
    for i in range (len(entries)): #not case sessitive search
        if query.lower() == entries[i].lower():
            return render(request,"encyclopedia/entry.html",{
                "title":query,
                "content":markdown2.markdown(util.get_entry(entries[i]))
                })
    #  no exact match found, look for substrings
    suggestions=[entry for entry in entries if query.lower() in entry.lower()]
    # if no suggestions found
    if not suggestions:
        return render (request,"encyclopedia/errors/findError.html",{
            "message":f"No search results found for \"{query}\"."
        })
    
    return render(request,"encyclopedia/errors/searchError.html",{
        "suggestions":suggestions
        })

def createNewPage(request):
    if request.method == "POST":       
        form = NewPageForm(request.POST)
        if form.is_valid():
            title=form.cleaned_data["title"]
            content=form.cleaned_data["content"]

            if title.lower() in [t.lower() for t in util.list_entries()]:#to do: create a fucntion to check if title exists true/false
                form.add_error('title', 'A wiki with this title already exists.')
                return render (request,"encyclopedia/errors/findError.html",{
                    "message":f"A wiki with the title \"{title}\" already exists."
                })        
            

            util.save_entry(title,content)
            return render(request,"encyclopedia/index.html",{"entries":util.list_entries()})   
         
        else:        
             return render(request,"encyclopedia/createNewPage.html",{
                "form":NewPageForm()
                })  
        
    return render(request,"encyclopedia/createNewPage.html",{
    "form":NewPageForm
    })

