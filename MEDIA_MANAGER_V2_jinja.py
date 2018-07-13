import configparser
import os
import sys
import requests
import xml.etree.ElementTree as xml_handle
import sqlite3
from flask import Flask, request, send_from_directory
from flask import render_template as flask_render
import re
import time
import threading
import socket
import subprocess
from urllib.parse import quote
import json
from jinja2 import Environment, PackageLoader, FileSystemLoader
#import gi
#gi.require_version('Gtk', '3.0')
#gi.require_version('WebKit2', '2.0')
import webview
#from gi.repository import Gtk, WebKit2

base_url = "https://api.thetvdb.com"
login = "/login"
search = "/search/series"
headers = {'content-type': 'application/json'}
credentials = {}
credentials["apikey"] = "9A8EBE44153F0B20"
credentials["username"] = "I_AM_NEW_TO_THIS"
credentials["userkey"] = "23B6A48E1FEE6CEE"

def load_config():
    global program_settings
    program_settings = {}
    config = configparser.ConfigParser()
    # pc_name = os.environ['COMPUTERNAME'] # This would not work on ubuntu
    pc_name = socket.gethostname()
    config[pc_name] = {'Film Directory': 'C:\\Users\\Mum\\Documents\\data',
                           'Music Directory': 'empty',
                           'Tv Directory': 'empty',
                           'Port' : '5005',
                           'VLC EXE': 'empty',
                           'VLC User': '',
                           'VLC Password': 'no',
                            'Moviedb User': '',
                            'Moviedb Password': '',
                            'Moviedb Key': '',
                            'Tvdb User': '',
                            'Tvdb Password': '',
                            'Tvdb Key': ''}
    if os.path.isfile('Media Manager Settings.ini') != True:
        print("Config File Not Found, Creating...")
        with open('Media Manager Settings.ini', 'w') as configfile:
            config.write(configfile)
    if os.path.isfile('Media Manager Settings.ini') == True:
        print("Config File Found")
        print("Checking Integrity Of Config File")
        # need to check if config file is okay before use
        config.read('Media Manager Settings.ini')
        for i in config[pc_name]:
            program_settings[i] = config[pc_name][i]
        return 1
    else:
        print("Config File Not Found")
        return 0

def save_settings(the_settings):
    global program_settings
    config = configparser.ConfigParser()
    config.read('Media Manager Settings.ini')
    pc_name = socket.gethostname()
    if os.path.isfile('Media Manager Settings.ini') == True:
        for i in program_settings:
            setting_text = the_settings[list(program_settings.keys()).index(i)]
            if setting_text != program_settings[i]:
                config.set(pc_name, i, setting_text)
                with open('Media Manager Settings.ini', 'w') as configfile:
                    config.write(configfile)
    load_config()
    TEMPLATE_ENVIRONMENT = Environment(autoescape=False, loader=FileSystemLoader("templates"), trim_blocks=False)
    create_index_html()
    print(program_settings)

def cache_media(media_directories, file_type):
    global media_cache_dict
    print("Generating Cache")
    media_cache_dict = {}
    media_cache_dict[file_type] = {}
    media_cache_dict[file_type]['files'] = {}
    media_cache_dict[file_type]['folders'] = {}
    for directory in media_directories:
        if os.path.isdir(directory) == True:
            for directory_base, directories, all_files in os.walk(directory):
                for file_name in all_files:
                    full_path = os.path.join(directory_base, file_name)
                    media_cache_dict[file_type]['files'][file_name.split(".")[0]] = full_path
                for directory_name in directories:
                    full_directory = os.path.join(directory_base, directory_name)
                    media_cache_dict[file_type]['folders'][directory_name] = full_directory
            print("Cache Generated")
            return 1
        else:
            print("Cannot Generate Cache, Directory Not Found")
            return 0

def search_media(search):
    global media_cache_dict
    for file_types in media_cache_dict:
        for folders_files in media_cache_dict[file_types]:
            for names in media_cache_dict[file_types][folders_files]:
                if search == names:
                    return media_cache_dict[file_types][folders_files][names]
    # search cache first, then directories
    
def play(path, mode, resume_point = None):
    global program_settings
    command_string = '"' + program_settings['vlc exe'] + '"' + " " + '"' + path + '"'
    # -I http to launch with web interface
    # --http-password <your password here> to set password
    if "resume" in mode:
        command_string = command_string + " " + ":start-time=" + resume_point
    if "stream" in mode:
        command_string = command_string + " " + """--sout=#transcode{vcodec=h264, vb=500, venc=x264{profile=baseline},
                                                    scale=Auto,width=480,height=360,acodec=mp3,ab=128,channels=2,
                                                    samplerate=44100}:http{mux=ffmpeg{mux=flv},dst=:8080/yes}"""
    print(command_string)
    p = subprocess.Popen(command_string)

def connect_db(database = "Media Manager):
    conn = sqlite3.connect(database + ".db")
    c = conn.cursor()
    tables = c.fetchall()
    if len(tables) == 0:
        try:
            c.execute("CREATE TABLE Film ('Show', 'Series', 'Episode', 'Elapsed Time', 'Thumbnail', 'Description', 'Genre', 'Rating')")
        except Exception as e:
            print("ERROR")
    return c, conn
    
def close_db(conn):
    conn.commit()
    conn.close()
    
def read_db(select_colum, where_this, where_that):
    c, conn = connect_db()
    c.execute("SELECT " + select_colum + " FROM " + "Film" + " WHERE " + where_this + "=" + "'" + where_that.replace("'", "''") + "'")
    #c.execute("SELECT ? FROM FILM WHERE ? = ?", (select_colum, where_this, where_that))
    for i in c.fetchall():
        result = i[0]
        break
    close_db(conn)
    if 'result' not in locals():
        return None
    return result
    
def write_db(show, series = None, episode = None, elapsed_time = None, thumb = None, descrip = None, genre = None, rating = None):
    c, conn = connect_db()
    print("SELECT " + "Show" + " FROM " + "Film" + " WHERE " + "Show" + "=" + "'" + show + "'")
    #c.execute("SELECT Show FROM Film WHERE Show = ?", (show))
    c.execute("SELECT " + "Show" + " FROM " + "Film" + " WHERE " + "Show" + " = " + "'" + show.replace("'", "''") + "'")
    if c.fetchone():
        if thumb != None and descrip != None and genre != None and rating != None:
            c.execute("UPDATE Film SET Description = ? WHERE Show = ?", (descrip, show))
            c.execute("UPDATE Film SET Thumbnail = ? WHERE Show = ?", (thumb, show))
            c.execute("UPDATE Film SET Genre = ? WHERE Show = ?", (genre, show))
            c.execute("UPDATE Film SET Rating = ? WHERE Show = ?", (rating, show))
            return 1
        if series == None or episode == None:
            c.execute("UPDATE Film SET 'Elapsed Time' = '" + elapsed_time + "'" + "WHERE Show = " + "'" + show + "'")
        else:
            c.execute("UPDATE Film SET Series = '" + series + "'" + "WHERE Show = " + "'" + show + "'")
            c.execute("UPDATE Film SET Episode = '" + episode + "'" + "WHERE Show = " + "'" + show + "'")
        print("Updated Table Film")
    else:
        c.execute("INSERT INTO Film VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (show, series, episode, elapsed_time, thumb, descrip, genre, rating))
    close_db(conn)
    
def new_write_db(database, mode, table, columns, values, this=None, that=None):
    c, conn = connect_db(database) # should implement some error handling in the connect_db function
    if this == None or that == None:
            if isinstance(columns, list) == True and isinstance(values, list) == True:
                if len(columns) == len(values):
                    for i in range(len(columns)):
                        c.execute("SELECT " + colums[i] + " FROM " + table + " WHERE " + columns[i] + " = ?", (values[i]))
                        if c.fetchone():
                            c.execute("UPDATE " + table + " SET " + colums[i] + " = ?", (values[i]))
                        else:
                            c.execute("INSERT INTO " + table + " VALUES (?)", (values[i]))
                else:
                    print("Invalid Number Of Arguments. Columns = " + str(len(columns)) + ", Values = " + str(len(values)) + ", (WHERE) This = " + str(len(this)) + ", (WHERE) That = " + str(len(that)))
                    return False
            else:
                c.execute("UPDATE " + table + " SET " + colums + " = ?", (values))
    else:
        if isinstance(columns, list) == True and isinstance(values, list) == True:
            if isinstance(this, list) == True and isinstance(that, list) == True:
                if len(columns) == len(values) and len(columns) == len(this) and len(columns) == len(that):
                    for i in range(len(columns)):
                        c.execute("SELECT " + colums[i] + " FROM " + table + " WHERE " + columns[i] + " = ?", (values[i]))
                        if c.fetchone():
                            c.execute("UPDATE " + table + " SET " + colums[i] + " = ? WHERE " + this[i] + " = ?", (values[i], that[i]))
                        else:
                            c.execute("INSERT INTO " + table + " VALUES (?)", (values[i]))
                else:
                    print("Invalid Number Of Arguments. Columns = " + str(len(columns)) + ", Values = " + str(len(values)) + ", (WHERE) This = " + str(len(this)) + ", (WHERE) That = " + str(len(that)))
                    return False
            else:
                if len(columns) == len(values):
                    for i in range(len(columns)):
                        c.execute("UPDATE " + table + " SET " + colums[i] + " = ? WHERE " + this + " = ?", (values[i], that))
        else:
            print("This Functionality Is Not Ready Yet")
            return False
        
    elif mode == "ALTER TABLE":

    else:
        print("Mode " + str(mode) + " Not Found")
        close_db(conn)
        return False:
    
def html_interface():
    app = Flask(__name__)
    @app.route('/')
    def serve_page():
        print("placeholder")
        return flask_render("output.html")

    @app.route('/refresh_meta')
    def refresh_meta():
        print("Refreshing...")
        fetch_film_metadata()
        fetch_tv_metadata()
        return "success"

    @app.route('/save_settings', methods=['POST'])
    def save_settings_interface():
        print("saving...")
        data = request.form
        print(data)
        for i in data:
            data = i
        settings = []
        for i in data.split(","):
            if i == "":
                settings.append("None")
            else:
                settings.append(i)
        print(settings)
        save_settings(settings)
        return "success"

    @app.route("/play", methods=['POST'])
    def play_from_post():
        print("playing..")
        data = request.form.to_dict()
        #print(request.form)
        for i in data:
            print(i)
            break
        #data = request.form['query']
        play(search_media(i), "play")
        return "success"

    @app.route("/resume", methods=['POST'])
    def resume_from_post():
        data = request.form['query']
        play(search_media(data), "resume")

    @app.route("/stream", methods=['POST'])
    def stream_from_post():
        data = request.form['query']
        play(search_media(data), "stream")

    @app.route("/stream_resume", methods=['POST'])
    def resume_stream_from_post():
        data = request.form['query']
        play(search_media(data), "stream, resume")

    @app.route('/example')
    def example():
        print("placeholder")
        
    @app.route('/playback_toggle')
    def pause():
        print("placeholder")
        
    @app.route("/stream_toggle")
    def stream_toggle():
        print("placeholder")
        
    @app.route("/next")
    def next_ep():
        print("placeholder")
        
    @app.route("/previous")
    def previous_ep():
        print("placeholder")

    @app.route('/vol_up')
    def volup():
        print("placeholder")

    @app.route('/vol_down')
    def voldown():
        print("placeholder")

    @app.route('/sub_toggle')
    def subtitles():
        print("placeholder")
        
    @app.route('/vlc_window')
    def vlc_window():
        print("manipulations of the vlc window")
        
    @app.after_request
    def add_header(r):
        """
        Add headers to both force latest IE rendering engine or Chrome Frame,
        and also to cache the rendered page for 10 minutes.
        """
        r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        r.headers["Pragma"] = "no-cache"
        r.headers["Expires"] = "0"
        r.headers['Cache-Control'] = 'public, max-age=0'
        return r

    if __name__ == '__main__':
        #app.run(debug=True, use_reloader=False, host='0.0.0.0', port = int(program_settings['port'])) 
        app.run(debug=True, use_reloader=False, host='0.0.0.0', port = 5006) #currently having issues with above becase windows
    
def vlc_state():
    global vlc_result
    vlc_result = {}
    vlc_result['time'] = {}
    vlc_result['length'] = {}
    vlc_result['name'] = {}
    vlc_result['series'] = {}
    vlc_result['episode'] = {}
    vlc_url = "http://localhost:8080/requests/status.xml"
    s = requests.Session()
    s.auth = (program_settings['vlc user'], program_settings['vlc password'])
    try:
        r = s.get(vlc_url)
    except Exception as e:
        print("Error In Reaching VLC Server")
        #print(e)
        return 0
    if r.status_code == 200:
        print("VLC Server Is Running")
        root = xml_handle.fromstring(r.text)
        vlc_result['time'] = root.findall('time')[0].text
        vlc_result['length'] = root.findall('length')[0].text
        for child in root.iter('info'):
            if child.attrib['name'] == 'filename':
                vlc_result['name'] = child.text
                if "Series" in vlc_result['name'] and "Episode" in vlc_result['name']:
                    result = re.search('Series (.*) Episode', vlc_result['name'])
                    vlc_result['series'] = result.group(1)
                    result = re.search('Episode (.*) -', vlc_result['name'])
                    vlc_result['episode'] = result.group(1)
                    vlc_result['name'], unused = vlc_result['name'].split(" Series ")
                    write_db(str(vlc_result['name']), str(vlc_result['series']), str(vlc_result['episode']), str(vlc_result['time']))
                    return 1
        vlc_result['name'], extension = vlc_result['name'].split(".")
        write_db(str(vlc_result['name']), None, None, str(vlc_result['time']))
        return 1
    else:
        print(r.status_code)
        return 0

def fetch_film_metadata():
    global program_settings, media_cache_dict
    for i in media_cache_dict['video']['files']:
        film = i
        proc_film = quote(film)
        film_api_url = "https://api.themoviedb.org/3/"
        full_url = film_api_url + "search/movie?api_key=" + program_settings['moviedb key'] + "&language=en&query=" + proc_film + "&include_adult=false"
        results_raw = requests.get(full_url)
        results_json = json.loads(results_raw.text)
        if results_raw.status_code == 200:
            if results_raw.text != "":
                if os.path.isdir("thumbs") == False:
                    os.makedirs("thumbs")
                    print("directory made")
                if len(results_json['results']) == 0:
                    print("No Results Found For " + str(i))
                    continue
                print("https://image.tmdb.org/t/p/w500" + results_json['results'][0]['poster_path'])
                r = requests.get("https://image.tmdb.org/t/p/w500" + results_json['results'][0]['poster_path'], allow_redirects=True)
                open("thumbs" + str(results_json['results'][0]['poster_path']), 'wb').write(r.content)
                print(str(results_json['results'][0]['poster_path']).replace("/", ""))
                write_db(film, None, None, None, "thumbs" + str(results_json['results'][0]['poster_path']), str(results_json['results'][0]['overview']), str(results_json['results'][0]['genre_ids']), str(results_json['results'][0]['vote_average']))
        else:
            print(results_raw.status_code)
        time.sleep(0.5)

def login_tvdb():
    r = requests.post(base_url + login, json.dumps(credentials), headers=headers)
    if r.status_code == 200:
        tvdb_token = json.loads(r.text)['token']
        print(tvdb_token)
        return tvdb_token
    else:
        print("Failed Login With Status Code " + str(r.status_code))
        return False
def fetch_tv_metadata():
    login_status = login_tvdb()
    if login_status == False:
        return False
    else:
        for directory in media_cache_dict['video']['folders']:
            if directory.isdigit() == True or "Extras" in directory or "Subs" in directory or "Specials" in directory or "Season" in directory:
                print("Blocked Request for " + str(directory))
            else:
                auth_header = {}
                auth_header["Authorization"] = "Bearer " + login_status
                print(base_url + search + "?name=" + quote(directory))
                time.sleep(3)
                r = requests.get(base_url + search + "?name=" + quote(directory), headers=auth_header)
                if r.status_code == 200:
                    print(directory)
                    results = json.loads(r.text)['data']
                    series_id = json.loads(r.text)['data'][0]['id']
                    series_thumb = json.loads(r.text)['data'][0]['banner']
                    series_description = json.loads(r.text)['data'][0]['overview']
                    print(series_id)
                    series_thumb = series_thumb.replace("graphical/", "")
                    print(series_thumb)
                    print(series_description)
                    
                    if os.path.isdir("thumbs") == False:
                        os.makedirs("thumbs")
                        print("Directory made")
                    print("https://www.thetvdb.com/banners/graphical/" + series_thumb)
                    time.sleep(1)
                    r = requests.get("https://www.thetvdb.com/banners/graphical/" + series_thumb, allow_redirects=True)
                    open("thumbs/" + str(series_thumb), 'wb').write(r.content)
                    write_db(directory, None, None, None, "thumbs/" + str(series_thumb), str(series_description), "TVSHOW", "tvdb shit")


                    #for loop here
                    #print(base_url + "/series/" + str(series_id) + "episodes/query?airedSeason=" + str(season) + "airedEpisode=" + str(episode))
                    # start query for data about individual episodes...
                    #r = requests.get(base_url + "/series/" + str(series_id) + "episodes/query?airedSeason=" + str(season) + "airedEpisode=" + str(episode), headers=auth_header)
                    print("")
                else:
                    print("Failed Search With Status Code " + str(r.status_code))
                    #return False
            

def render_template(template_filename, context):
    return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)

def create_index_html():
    global program_settings, media_cache_dict
    film_names = []
    thumbnail_metadata = []
    description_metadata = []
    score_metadata = []
    setting_names = []
    setting_values = []
    print("create_index_html")
    print(program_settings)
    for i in media_cache_dict['video']['files']:
        if read_db("Thumbnail", "Show", i) == None:
            print("No Metadata For " + str(i))
            continue
        else:
            film_names.append(i)
            thumbnail_metadata.append(read_db("Thumbnail", "Show", i))
            description_metadata.append(read_db("Description", "Show", i))
            score_metadata.append(read_db("Rating", "Show", i))

    #
    #
    #
    #   space for seperate handling of tv metadata
    #
    #
    for i in program_settings:
        setting_names.append(i)
        setting_values.append(program_settings[i])

    media_with_metadata = zip(film_names, thumbnail_metadata, description_metadata, score_metadata)
    settings = zip(setting_names, setting_values)
    fname = "templates/output.html"
    context = {
        'settings': settings,
        'metadata' : media_with_metadata
    }
    #
    with open(fname, 'w', encoding='utf-8') as f:
        html = render_template('main.html', context)
        f.write(html)

def exit_all():
    print("Quitting")
    os._exit(0)

if load_config() == True:
    print("Config File Loaded")
else:
    print("Failed To Load Config File, Exiting")
    exit_all()
   
if cache_media([program_settings['film directory'], program_settings['tv directory']], "video") == True:
    print("Cache Loaded")
else:
    print("Failed to Load Cache")
    
#play(search_media("ENCODED_20170601_120017"), "play")
TEMPLATE_ENVIRONMENT = Environment(autoescape=False, loader=FileSystemLoader("templates"), trim_blocks=False)
create_index_html()
h = threading.Thread(target=html_interface)
h.start()

time.sleep(1)
"""
window = Gtk.Window()
window.set_title("Media Manager")
window.connect("destroy", exit_all)
webview = WebKit2.WebView()
#webview.load_uri("http://0.0.0.0:5005/")# this wont work on windows
webview.load_uri("http://localhost:5005/")# WebKit2 version 3.0 has displays incorrectly. need to use 4.0
window.add(webview)
window.maximize()
window.show_all()
Gtk.main()
"""

webview.create_window("Media Manager", "http://localhost:5006/") #create window blocks unit the window is closed
exit_all()

"""
while True:
    if vlc_state() == 1:
        print("VLC Server Information Read")
    else:
        print("Could Not Read VLC Server")
    time.sleep(5)
    #print(vlc_result)
"""
