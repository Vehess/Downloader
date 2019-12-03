import os
import urllib3
from bs4 import BeautifulSoup
import re
# TODO ==> pip install wget
import wget

http = urllib3.PoolManager()
# TODO ==> ajouter choix de l'adresse web
r = http.request('GET', 'http://rendezvousavecmrx.free.fr/page/liste.php')
soup = BeautifulSoup(r.data, 'lxml')

lien = 0
nom = 0
link = []
name = []
const = "http://rendezvousavecmrx.free.fr/"


print("#### je me lance ####")

mp3_files_info = []

LINK_FMT = "http://rendezvousavecmrx.free.fr/audio/%s"
DOWNLOAD_PATH = "./download"
DOWNLOAD_PATH_FMT = DOWNLOAD_PATH + "/%s"

# Definition des nom pour les group a matcher par expression reguliere
# pour recuperer le resutat de la regexp par nom et non par index
# pour faciliter la lecture 
REGEXP_LINK_GROUP_NAME      = "matched_link"
REGEXP_FILE_NAME_GROUP_NAME = "matched_file_name"
REGEXP_ALT_GROUP_NAME       = "matched_alt"
REGEXP_TITLE_GROUP_NAME     = "matched_titile"
# \s ==> whitespace
# ?P<%s> ==> nom d'un group
# url au format xxxxx/audio/xxxxx.mp3
# exemple ==> <a href="http://rendezvousavecmrx.free.fr/page/detail_emission.php?cle_emission=695">10 mai 1941, l'etrange voyage de Rudolf Hess</a></td>
# Oulala grosse galere de faire la regexp ==> amelioration possible etre robuste a des espaces ou tabs entre les valeurs (ne pas utiliser .* entre les parametre
# car on ne devrait avoir que des espaces ou des tabs)
# la ca marche alors j'arrete pour le moment
# OK ca n'aide pas vraiement a la lecture de la la regexp de definir des noms pour les groupes mais au parse c'est plus clair je trouve
REGEXP_MATCH_MP3_FILE       = r"<a[^>]*href=\"(?P<%s>[^\"]*audio/(?P<%s>(.*\.mp3)))\".*alt=\"(?P<%s>([^\"]*))\".*title=\"(?P<%s>(.*))\".*></a>" \
                                % (REGEXP_LINK_GROUP_NAME, REGEXP_FILE_NAME_GROUP_NAME, REGEXP_ALT_GROUP_NAME, REGEXP_TITLE_GROUP_NAME)
                                
mp3_file_match_pattern = re.compile(REGEXP_MATCH_MP3_FILE)

# classe contenant les informations d'un fichier mp3
class MP3_file_data(object):
    # constructeur
    def __init__(self, i_link, i_file_name, i_alt, i_title):
        self.__link      = i_link
        self.__file_name = " ".join(i_file_name.split()) # suppression des espaces en double
        self.__alt       = " ".join(i_alt.split()) # suppression des espaces en double
        self.__title     = " ".join(i_title.split()) # suppression des espaces en double
    # retourne le nom de destination du fichier
    def name(self):
        # TODO faire dans le constructeur pour le faire uniquement a la construction
        # Le probleme est que certains titres contiennent des caracteres non autorise dans un nom de fichier
        not_allowed_chars_replacement = [('<', ' '), ('>', ' '), (':', ' '), ('"', "'"), ('/', '_'), ('\\', '_'), ('|', ' '), ('?', ' '), ('*', ' ')]
        # TODO verifier que le nom est un nom de fichier valide
        if self.__title:
            name = "%s.mp3" % self.__title
        elif self.__alt:
            name = "%s.mp3" % self.__alt
        elif self.__file_name:
            name = self.__file_name
        
        # TODO suppression des caracteres non autorise
        for char in not_allowed_chars_replacement:
            name = name.replace(char[0], char[1])
        return name
    # retourne le chemin
    def url(self):
        return self.__link

for a in soup.findAll('a'):
    #if 'mp3' in a.get('href'):
    #    link.append(a.get('href'[2:]))
    #    print (a.get('href'))#retourne les liens
    #    lien = lien + 1
    for m in mp3_file_match_pattern.finditer(unicode(a)):
        try:
            #link        = m.group(REGEXP_LINK_GROUP_NAME) # en fait le lien lu est du type ../audio/xxxx et non pas "http://rendezvousavecmrx.free.fr/audio/xxxx" alors lien refait a partir du nom du fichier
            file_name   = m.group(REGEXP_FILE_NAME_GROUP_NAME) 
            link        = LINK_FMT % file_name
            alt         = m.group(REGEXP_ALT_GROUP_NAME)
            title       = m.group(REGEXP_TITLE_GROUP_NAME)
            mp3_files_info.append( MP3_file_data(link, file_name, alt, title) )
            #print(link)
            #print(file_name)
            #print(alt)
            #print(title)
        except:
            print("Oups petit souci avec '%s', je continue, rien ne m'arrete..." % unicode(a))

# Creation du repertoire de download
if not os.path.isdir(DOWNLOAD_PATH):
    os.mkdir(DOWNLOAD_PATH)
# Download des fichiers
for mp3_file in mp3_files_info:
    # TODO clean des fichiers tmp en cas d'erreur + mettre les tmp dans un autre repertoire
    print("##### Download file '%s' ######" % mp3_file.name())
    file_name = wget.download(mp3_file.url(), DOWNLOAD_PATH_FMT % mp3_file.name())
    print("")
    #print(file_name)
    
print("#### j'ai fini ####")

#for b in soup.findAll('img'):
#    #name = list(map(getstring, a.get('title')))
#    name.append(str(b.get('title')))
#    print(b.get('title'))#retourne les titres
#    nom = nom + 1
#
#with open("mr_x_2013_04_27.mp3", "wb") as Pypdf:
#    total_length = int(r.headers.get('content-length'))
#    for ch in progress.bar(r.iter_content(chunk_size = 2391975), expected_size=(total_length/1024) + 1):
#         if ch:
#             Pypdf.write(ch)

"""
# getting length of list 
length = len(link)
for i in range(length):
    print("Le liens " + link[i] +" correspond a "+ name[i+4])


name_link = zip(name, link)
print("Printing name_link")
print(name_link)

for name, link in name_link:
    print('Downloading %s' % link)
    os.system("wget -cO - %s > %s.mp3".format(link,name))
"""