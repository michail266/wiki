from django.shortcuts import render
from django import forms
from django.core.exceptions import ValidationError
import markdown2
import random

from . import util

class NewPageForm(forms.Form):
    #this helped a lot https://docs.djangoproject.com/en/5.2/ref/forms/widgets/
    title = forms.CharField(label="Title", max_length=20)
    content = forms.CharField(label="", widget=forms.Textarea(attrs={
        "style":"height: 300px; width: 600px;"
    
    }))

def titleCheck(value):
    entries=util.list_entries()
    for i in range (len(entries)): #not case sessitive search
        if value.lower() == entries[i].lower():
            return util.get_entry(entries[i])
    return None


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

    #not case-sessitive search
    if  titleCheck(query):
        return render(request,"encyclopedia/entry.html",{
        "title":query,
        "content":markdown2.markdown(titleCheck(query))
        })
    
    #  no exact match found, look for substrings. This logic helped me a lot https://stackoverflow.com/questions/43302810/linear-search-python

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
    if request.method == "POST": #2.if the form is submitted       
        form = NewPageForm(request.POST)
        if form.is_valid(): #3.all validation rules pass
            title=form.cleaned_data["title"]
            content=form.cleaned_data["content"]
            if titleCheck(title): #4.and the title does not exist already
                return render (request,"encyclopedia/errors/findError.html",{
                    "message":f"A wiki with the title \"{title}\" already exists."
                })        
            
            util.save_entry(title,content)
            return render(request,"encyclopedia/index.html",{"entries":util.list_entries()})#5.successful creation   
         
        else:        
             return render(request,"encyclopedia/createNewPage.html",{
                "form":NewPageForm()
                })  
        
    return render(request,"encyclopedia/createNewPage.html",{ #1.first time visit
    "form":NewPageForm
    })

def editPage(request,title):#I had to add remove_entry in util.py to avoid duplicates, the rest is similar to createNewPage
    if request.method == "POST":
        form = NewPageForm(request.POST)
        util.remove_entry(title)  
        if form.is_valid():
            title=form.cleaned_data["title"]
            content=form.cleaned_data["content"]               
            util.save_entry(title,content)
            return render(request,"encyclopedia/entry.html",{
                "content":markdown2.markdown(content),
                "title":title
                })
        else:
            return render(request,"encyclopedia/edit.html",{
                "form":form,
                "title":title
                })
    return render(request,"encyclopedia/edit.html",{
        "form":NewPageForm(initial={
            "title":title,
            "content":util.get_entry(title)
        }),
        "title":title
        })

def randomPage(request): #very simple, it can show multiple times the same page
    entries=util.list_entries()
    randomChoice=random.choice(entries)
    return render(request,"encyclopedia/entry.html",{
        "title":randomChoice,
        "content":markdown2.markdown(util.get_entry(randomChoice))  
        })  