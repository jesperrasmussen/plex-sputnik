# PMS plugin framework
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *
import sputnik

Query = sputnik.Query()
Profile = sputnik.Profile()

def Start():
    Plugin.AddPrefixHandler('/video/sputnik', MainMenu, L('Title'), 'icon.png', 'backdrop.png')
    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
    Plugin.AddViewGroup("MediaPreview", viewMode="MediaPreview", mediaType="items")
    Plugin.AddViewGroup("Coverflow", viewMode="Coverflow", mediaType="items")

    MediaContainer.art          = R('backdrop.png')
    MediaContainer.title1       = L('Title')
    DirectoryItem.thumb         = R('icon.png')
    InputDirectoryItem.thumb    = R('icon.png')
    PrefsItem.thumb             = R('icon.png')

def CreatePrefs():
    Prefs.SetDialogTitle('Sputnik account settings')
    Prefs.Add(id = 'username', type = 'text', default = None, label = 'Username')
    Prefs.Add(id = 'password', type = 'text', default = None, label = 'Password', option = 'hidden')

def MainMenu():
    dir = MediaContainer(viewGroup="List")
    dir.Append(Function(DirectoryItem(Latest, L('Latest'))))
    dir.Append(Function(DirectoryItem(Popular, L('Popular'))))
    dir.Append(Function(DirectoryItem(Sneakpreview, L('Sneakpreview'))))
    dir.Append(Function(DirectoryItem(Series, L('Series'))))
    dir.Append(Function(DirectoryItem(Categories, L('Categories'))))
    dir.Append(Function(DirectoryItem(Live, L('Live'))))
    dir.Append(Function(InputDirectoryItem(Search, L('Search'), L('Search for:'))))
    dir.Append(PrefsItem(L('Settings'), L('Sputnik account settings')))
    return dir

def Message(sender, headline, message):
    return MessageContainer(headline, message)

def ProgramItem(source, type="program"):
    if source.nocharge == True or source.group in Profile.groups or source.id in Profile.singles:
        return WebVideoItem(
            "http://sputnik-dyn.tv2.dk/player/simple/id/"+source.id+"/type/"+type+"/",
            title    = source.fulltitle,
            summary  = source.description,
            subtitle = source.subtitle,
            thumb    = source.image.url
        )

    else:
        Log(source.group)
        return Function(DirectoryItem(
            Message,
            title    = source.fulltitle,
            summary  = source.description,
            subtitle = source.subtitle,
            thumb    = source.image.url
        ), headline = "Program unavailable", message = "Please consult sputnik.dk for purchasing options")


def SeriesItem(source):
    return Function(DirectoryItem(
        SeriesPrograms,
        title   = source.title,
        summary = source.description,
        subtitle = source.subtitle,
        thumb = source.image.url), id = source.id
    )

def CategoryItem(source):
    return Function(DirectoryItem(
        Categories,
        title   = source.title,
        summary = source.description,
        subtitle = source.subtitle,
        thumb = source.image.url), id = source.id
    )

def UnknownItem(source):
    if isinstance(source, sputnik.Series):
        return SeriesItem(source)
    if isinstance(source, sputnik.Program):
        return ProgramItem(source)
    if isinstance(source, sputnik.Category):
        return CategoryItem(source)
    raise Exception('source type not known')

def Live(sender):
    Profile = Query.AccessProfile()
    dir = MediaContainer(viewGroup="InfoList", title2=sender.itemTitle)
    response = Query.LiveChannels()
    for program in response:
        dir.Append(ProgramItem(program, type="broadcast"))
    return dir

def Series(sender):
    dir = MediaContainer(viewGroup="InfoList", title2=sender.itemTitle)
    response = Query.Series()
    for serie in response["series"]:
        dir.Append(SeriesItem(serie))
    return dir

def Latest(sender):
    Profile = Query.AccessProfile()
    dir = MediaContainer(viewGroup="InfoList", title2=sender.itemTitle)
    response = Query.Programs()
    for program in response["programs"]:
        dir.Append(ProgramItem(program))
    return dir

def Popular(sender):
    Profile = Query.AccessProfile()
    dir = MediaContainer(viewGroup="InfoList", title2=sender.itemTitle)
    response = Query.Programs(sort = "popularity")
    for program in response["programs"]:
        dir.Append(ProgramItem(program))
    return dir

def Sneakpreview(sender):
    Profile = Query.AccessProfile()
    dir = MediaContainer(viewGroup="InfoList", title2=sender.itemTitle)
    response = Query.ProgramsSneakpreview()
    for program in response["programs"]:
        dir.Append(ProgramItem(program))
    return dir

def SeriesPrograms(sender, id):
    Profile = Query.AccessProfile()
    dir = MediaContainer(viewGroup="InfoList", title2=sender.itemTitle)
    response = Query.SeriesPrograms(id)
    for program in response["programs"]:
        dir.Append(ProgramItem(program))

    pages = int(response["total_pages"])
    if pages > 1:
        for i in range(2, pages + 1):
            response = Query.SeriesPrograms(id, page = str(i))
            for program in response["programs"]:
                dir.Append(ProgramItem(program))

    return dir

def Categories(sender, id = None):
    Profile = Query.AccessProfile()
    dir = MediaContainer(viewGroup="InfoList", title2=sender.itemTitle)
    response = Query.Categories(id)
    for category in response["categories"]:
        dir.Append(CategoryItem(category))

    if len(dir) == 0:
        response = Query.CategoryContent(id)
        for item in response["items"]:
            dir.Append(UnknownItem(item))

    return dir


def Search(sender, query):
    Profile = Query.AccessProfile()
    dir = MediaContainer(viewGroup="InfoList", title2=query)
    response = Query.Search(query)
    if response == False:
        return MessageContainer('No results found', 'search for "'+query+'" returned no results');
    
    if len(response["programs"]) == 0 and len(response["series"]) == 0:
        return MessageContainer('No results found', 'search for "'+query+'" returned no results');
    
    for series in response["series"]:
        dir.Append(SeriesItem(series))

    for program in response["programs"]:
        dir.Append(ProgramItem(program))

    return dir
