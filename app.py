from distutils.log import debug
from fileinput import filename
from flask import *
import requests
import json
import discogs_client
import re

app = Flask(__name__)  
 
@app.route('/')  
def main():  
    return render_template("index.html")  
 
@app.route('/success', methods = ['POST'])  
def success():  
    if request.method == 'POST':  
        f = request.files['file']
        f.save(f.filename)  
        name = f.filename
        data = {
        'api_token': '35d10cc597ed552cea87d8c221a380bd',
        'accurate_offsets': 'true',
        'skip': '2',
        'every': '1',
        }
        files = {
            'file': open(str(name), 'rb'),
        }

        result = requests.post('https://api.audd.io/', data=data, files=files)

        dict=json.loads(result.text)

        shazam_audd = {
            'Название': str(dict['result']['title']),
            'Исполнитель': str(dict['result']['artist']),
            'Дата релиза': str(dict['result']['release_date']),
            'Жанр': '',
            'Стиль': '',
            'Текст песни':''
        }






        music_name = str(shazam_audd['Исполнитель'])+' '+str(shazam_audd['Название'])
        url = "https://genius-song-lyrics1.p.rapidapi.com/search/"

        querystring = {"q":str(music_name),"per_page":"1","page":"1"}

        headers = {
            "X-RapidAPI-Key": "8d5b7b83admsh2b09484bcea92f9p155153jsna63f71772814",
            "X-RapidAPI-Host": "genius-song-lyrics1.p.rapidapi.com"
        }

        response = requests.request("GET", url, headers=headers, params=querystring)



        dict1=json.loads(response.text)

        if (dict1 == {'hits': []}):

            shazam_Genius = {
                'title': '',
                'artist_name': '',
                'release_date': '',
                'genre': '',
                'style': '',
                'song_text':''
            }
        else:
            artist_id = (dict1['hits'][0]['result']['id'])


            url = "https://genius-song-lyrics1.p.rapidapi.com/song/lyrics/"

            querystring_song = {"id":str(artist_id)}

            headers = {
                "X-RapidAPI-Key": "8d5b7b83admsh2b09484bcea92f9p155153jsna63f71772814",
                "X-RapidAPI-Host": "genius-song-lyrics1.p.rapidapi.com"
            }

            response_song = requests.request("GET", url, headers=headers, params=querystring_song)

            dict_song=json.loads(response_song.text)

            CLEANR = re.compile('<.*?>') 

            cleantext = re.sub(CLEANR, '', (dict_song['lyrics']['lyrics']['body']['html']))
        
            shazam_Genius = {
                'title': str(dict1['hits'][0]['result']['full_title']),
                'artist_name': str(dict1['hits'][0]['result']['artist_names']),
                'release_date': str(dict1['hits'][0]['result']['release_date_for_display']),
                'genre': str(dict_song['lyrics']['tracking_data']['primary_tag']),
                'style': '',
                'song_text':str(cleantext)
            }

        d = discogs_client.Client('ExampleApplication/0.1', user_token="xldYxYHkUwshNGqQaIUZNwzghtVwIyjsLPuVfuFC")

        results = d.search(str(shazam_audd['Название']), artist=str(shazam_audd['Исполнитель']), type='release')
        x = (results.page(1))
        if (x == []):
            shazam_discogs = {
                'title':'',
                'artist_name': '',
                'release_date': '',
                'genre': '',
                'style': '',
                'song_text':''
            }

        else:
            x_id = (' '.join(map(str, x))).split()[1]
            art = (' '.join(map(str,(d.release(x_id).artists)))).split()
            del art[:2]

            art1 = ' '.join(map(str,art))

            art1 = art1.replace("'>","")
            art1 = art1.replace("'","")

            if ((d.release(x_id).genres) is None):
                genr = ''
            else:
                genr = str(' '.join(map(str,(d.release(x_id).genres))))

            if ((d.release(x_id).genres) is not None):
                stl = ''
            else:
                stl = str(' '.join(map(str,(d.release(x_id).styles))))
            
        
            shazam_discogs = {
                'title': '',
                'artist_name': str(art1),
                'release_date': str(d.release(x_id).year),
                'genre': genr,
                'style': stl,
                'song_text':''
            }

        return render_template("Acknowledgement.html",result_audd = shazam_audd,result_genius=shazam_Genius,result_discogs = shazam_discogs)

if __name__ == '__main__':  
    app.run(debug=True)