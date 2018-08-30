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
import re
import copy

import win32ui
#import gi
#gi.require_version('Gtk', '3.0')
#gi.require_version('WebKit2', '2.0')
#import webview # IE on windows
#from gi.repository import Gtk, WebKit2
#import webbrowser #python way of opening browser

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
    if not os.path.isfile('Media Manager Settings.ini'):
        print("Config File Not Found, Creating...")
        with open('Media Manager Settings.ini', 'w') as configfile:
            config.write(configfile)
    if os.path.isfile('Media Manager Settings.ini'):
        print("Config File Found")
        print("Checking Integrity Of Config File")
        config.read('Media Manager Settings.ini')
        if not pc_name in config:
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
            with open('Media Manager Settings.ini', 'w') as configfile:
                config.write(configfile)
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
    if os.path.isfile('Media Manager Settings.ini'):
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
        if os.path.isdir(directory):
            for directory_base, directories, all_files in os.walk(directory):
                for file_name in all_files:
                    full_path = os.path.join(directory_base, file_name)
                    media_cache_dict[file_type]['files'][file_name.split(".")[0]] = full_path
                for directory_name in directories:
                    full_directory = os.path.join(directory_base, directory_name)
                    media_cache_dict[file_type]['folders'][directory_name] = full_directory
            continue
        else:
            print("Cannot Generate Cache, Directory Not Found")
            continue
    return True

def search_media(search):
    global media_cache_dict
    for file_types in media_cache_dict:
        for folders_files in media_cache_dict[file_types]:
            for names in media_cache_dict[file_types][folders_files]:
                if search == names or search in names:
                    return media_cache_dict[file_types][folders_files][names]
    return False
    # search cache first, then directories

def play(path, mode, resume_point = None):
    global program_settings
    if path == None:
        return False
    command_string = '"' + program_settings['vlc exe'] + '"' + " " + '"' + path + '"'
    # -I http to launch with web interface. removes requitment of user to change vlc settings
    # --http-password <your password here> to set password
    # detirmine if transcoding is needed dont assume it is. guess by bitrate?
    if "resume" in mode:
        command_string = command_string + " " + ":start-time=" + resume_point
    if "stream" in mode: # transcoding not needed for my files so should remove it from the command string
        command_string = command_string + " " + """--sout=#transcode{vcodec=h264, vb=500, venc=x264{profile=baseline},
                                                    scale=Auto,width=480,height=360,acodec=mp3,ab=128,channels=2,
                                                    samplerate=44100}:http{mux=ffmpeg{mux=flv},dst=:8080/yes}"""
    print(command_string)
    p = subprocess.Popen(command_string)
    time.sleep(2)
    vlc_play_next()
    
def vlc_play_previous():
    s = requests.Session()
    s.auth = (program_settings['vlc user'], program_settings['vlc password'])
    r = s.get("http://127.0.0.1:8080/requests/status.xml?command=pl_previous")

def vlc_play_next():
    s = requests.Session()
    s.auth = (program_settings['vlc user'], program_settings['vlc password'])
    r = s.get("http://127.0.0.1:8080/requests/status.xml?command=pl_next")

def next_ep():
    global vlc_result
    next_ep_same_season = vlc_result['name'] + " - s" + vlc_result['series'] + "e" + str("{:02}".format(int(vlc_result['episode'])+1))
    is_file = search_media(next_ep_same_season)
    if is_file != False:
        play(is_file, "play")
    else:
        next_season_first_ep = vlc_result['name'] + " - s" + str("{:02}".format(int(vlc_result['series'])+1)) + "e01"
        is_file = search_media(next_season_first_ep)
        if is_file != False:
            play(is_file, "play")
        else:
            return False
    return True
        
def previous_ep():
    global vlc_result
    past_ep_same_season = vlc_result['name'] + " - s" + vlc_result['series'] + "e" + str("{:02}".format(int(vlc_result['episode'])-1))
    is_file = search_media(past_ep_same_season)
    if is_file != False:
        play(is_file, "play")
    else:
        for x in range(51, 0, -1):
            last_season_last_ep = vlc_result['name'] + " - s" + str("{:02}".format(int(vlc_result['series'])-1)) + "e" + str("{:02}".format(x))
            is_file = search_media(last_season_last_ep)
            if is_file != False:
                play(is_file, "play")
                break
    return True
    
def connect_db(database):
    conn = sqlite3.connect(database + ".db")
    c = conn.cursor()
    return c, conn

def close_db(conn):
    conn.commit()
    conn.close()

def write_db(database, mode, table, columns, values=None, this=None, that=None): # doesnt support columns with spaces
    c, conn = connect_db(database) # move this outside the write_db
    if mode == "INSERT":  # Insert: Supports Single Or Multiple Columns At A Time. Depending On Whether A String Or List Is Passed To It
        if isinstance(columns, list):
            c.execute("PRAGMA table_info(`%s`)" % table)
            data = c.fetchall()
            if len(data) == len(columns):
                c.execute("INSERT INTO `%s` VALUES (%s)" % (table, ', '.join("?"*len(columns))), (columns))
            else:
                print("Cannot Insert More Or Less Columns Than Defined In The Table")
                close_db(conn)
                return False
        elif isinstance(columns, str):
            c.execute("PRAGMA table_info(`%s`)" % table)
            data = c.fetchall()
            if len(data) == 1:
                # noinspection PyRedundantParentheses
                c.execute("INSERT INTO `%s` VALUES (?)" % (table), (columns,))
            else:
                print("Cannot Insert More Or Less Columns Than Defined In The Table")
                close_db(conn)
                return False
        else:
            print("INSERT - Invalid Type For 'column' Argument In INSERT, Must Be str or list")
            close_db(conn)
            return False
    elif mode == "UPDATE":  # Update: Supports Updating Of Multiple Rows From Array Where Specified From And Array Or Updating A Single Row
        if isinstance(columns, list) and isinstance(values, list) and isinstance(this, list) and isinstance(that, list):
            for i in range(len(columns)):
                if "row_exists" in locals():
                    if columns[i] in row_exists:
                        c.execute("UPDATE `%s` SET %s = ? WHERE %s = ?" % (table, columns[i], this[i]), (values[i], that[i]))
                    else:
                        c.execute("SELECT %s FROM `%s` WHERE %s = ?" % (columns[i], table, this[i]), (that[i],))
                        # c.execute("SELECT " + columns[i] + " FROM " + table + " WHERE " + columns[i] + " = ?", (values[i])) # select statement could be replaced with read_db()
                        if c.fetchone():
                            row_exists.append(columns[i])
                            c.execute("UPDATE `%s` SET %s = ? WHERE %s = ?" % (table, columns[i], this[i]), (values[i], that[i]))
                        else:
                            print("Cannot Update, Column Not Found")
                            continue
                else:
                    row_exists = []
                    c.execute("SELECT %s FROM `%s` WHERE %s = ?" % (columns[i], table, this[i]), (that[i],))
                    # c.execute("SELECT " + columns[i] + " FROM " + table + " WHERE " + columns[i] + " = ?", (values[i])) # select statement could be replaced with read_db()
                    if c.fetchone():
                        row_exists.append(columns[i])
                        c.execute("UPDATE `%s` SET %s = ? WHERE %s = ?" % (table, columns[i], this[i]), (values[i], that[i]))
                    else:
                        print("Cannot Update, Column Not Found")
                        continue
        elif isinstance(columns, str) and isinstance(values, str) and isinstance(this, str) and isinstance(that, str):
            print("UPDATE `%s` SET %s = ? WHERE %s = ?" % (table, columns, this), (values, that))
            c.execute("SELECT %s FROM `%s` WHERE %s = ?" % (columns, table, columns), (values,))
            if c.fetchone():
                print("Cannot Update, Column Not Found")
                close_db(conn)
                return False
            c.execute("UPDATE `%s` SET %s = ? WHERE %s = ?" % (table, columns, this), (values, that))
        else:
            print("UPDATE - Invalid Type For Arguments, All Must Be String Or All Must Be List")
            close_db(conn)
            return False
    elif mode == "CREATE":  # Create: Creates A Table With Multiple Or One Column, Depending On Whether An Array Or String Is Passed To It
        if isinstance(columns, list):
            c.execute("CREATE TABLE `%s` (%s)" % (table, ', '.join(columns)))
        elif isinstance(columns, str):
            c.execute("CREATE TABLE `%s` (%s)" % (table, columns))
        else:
            print("Invalid Type For 'column' Argument In CREATE, Must Be str or list")
            close_db(conn)
            return False
    elif mode == "ALTER":
        print("ALTER Not Built Yet")
        close_db(conn)
        return False
    else:
        print("Mode Not Found")
        close_db(conn)
        return False
    close_db(conn)
    return True

def read_db(database, mode, table, columns = None, this_column = None, that_value = None):
    c, conn = connect_db(database)
    if mode == "DUMP":
        c.execute("SELECT * FROM `%s`" % (table))
    elif mode == "SINGLE":
        c.execute("SELECT %s FROM `%s` WHERE %s = ?" % (columns, table, this_column), (that_value,))
    elif mode == "MULTIPLE":
        if isinstance(columns, list) and isinstance(this_column, list) and isinstance(that_value, list):
            for i in range(len(columns)):
                c.execute("SELECT %s FROM `%s` WHERE %s = ?" % (columns[i], table, this_column[i]), (that_value[i],))
    elif mode == "EXISTS":
        if columns is None and this_column is None and that_value is None:
            c.execute("SELECT name FROM sqlite_master WHERE type='table'")
            data = c.fetchall()
            for row in data:
                if table == row[0]:
                    close_db(conn)
                    return True
        elif columns is not None and this_column is None and that_value is None:
            c.execute("PRAGMA table_info(`%s`)" % table)
            data = c.fetchall()
            for row in data:
                if columns == row[1]:
                    close_db(conn)
                    return True
        elif columns is not None and this_column is not None and that_value is not None:
            c.execute("SELECT %s FROM `%s` WHERE %s = ?" % (columns, table, this_column), (that_value,))
            if c.fetchone():
                close_db(conn)
                return True
        else:
            print("Unsure How To Check If Exists")
    elif mode == "SCHEMA":
        pass
    else:
        print("Mode Not Found")
    result = []
    for i in c.fetchall():
        result.append(i)
    close_db(conn)
    if 'result' not in locals():
        return False
    # noinspection PyUnboundLocalVariable
    return result

def html_interface(): # all user input will go through here, consider checking it before sending it to database functions
    app = Flask(__name__)
    @app.route('/')
    def serve_page():
        print("placeholder")
        TEMPLATE_ENVIRONMENT = Environment(autoescape=False, loader=FileSystemLoader("templates"), trim_blocks=False)
        create_index_html(True) # Leave this in for testing changes without restarting program
        return flask_render("output.html") # Serving image files through flask is slow, should consider doing it from apache or a different webserver

    @app.route('/reveal')
    def serve_reveal():
        return flask_render("reveals_out.html") # Serving image files through flask is slow, should consider doing it from apache or a different webserver

    @app.route('/refresh_meta')
    def refresh_meta():
        print("Refreshing...")
        #fetch_film_metadata()
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
                settings.append("")
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
        if "i" in locals():
            play(search_media(i), "play")
            return "success"

    @app.route("/resume", methods=['POST'])
    def resume_from_post():
        #data = request.form['query']
        data = request.form.to_dict()
        #print(request.form)
        for i in data:
            print(i)
            break
        #data = request.form['query']
        if "i" in locals():
            data, time_in_sec = i.split(" ppp ")
            play(search_media(data), "resume", time_in_sec)
            return "success"

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
    def play_next_ep():
        print("flask next", file=sys.stderr)
        if next_ep() == False: # Won't play next episode straight away, waits till current is finished. fix
            print("Failed To Play Next Episode")
            return "False"
        time.sleep(2)
        vlc_play_next()
        return "True"
        
    @app.route("/previous")
    def play_previous_ep():
        if previous_ep() == False:
            print("Failed To Play Previous Episode")
            return "False"
        time.sleep(2)
        vlc_play_previous()
        return "True"

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
        code doesnt support Edge
        """
        r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        r.headers["Pragma"] = "no-cache"
        r.headers["Expires"] = "0"
        r.headers['Cache-Control'] = 'public, max-age=0'
        return r

    if __name__ == '__main__':
        #app.run(debug=True, use_reloader=False, host='0.0.0.0', port = int(program_settings['port'])) 
        app.run(debug=True, use_reloader=False, host='0.0.0.0', port = 5006, threaded=True) #currently having issues with above becase windows
    
def vlc_state():
    global vlc_result
    vlc_result, vlc_result['time'], vlc_result['length'], vlc_result['name'], vlc_result['series'], vlc_result['episode'] = {}, {}, {}, {}, {}, {}
    vlc_url = "http://localhost:8080/requests/status.xml"
    s = requests.Session()
    s.auth = (program_settings['vlc user'], program_settings['vlc password'])
    try:
        r = s.get(vlc_url)
    except Exception as e:
        print("Error In Reaching VLC Server")
        #print(e)
        return False
    if r.status_code == 200:
        print("VLC Server Is Running")
        root = xml_handle.fromstring(r.text)
        vlc_result['time'] = root.findall('time')[0].text
        vlc_result['length'] = root.findall('length')[0].text
        for child in root.iter('info'):
            if child.attrib['name'] == 'filename':
                result = re.search("(.*) - s(\d{2})e(\d{2})", child.text) # If I Make This Expression A Setting Any Naming Scheme Could Be Used
                if result:
                    vlc_result['name'] = str(result.group(1))
                    vlc_result['series'] = str(result.group(2))
                    vlc_result['episode'] = str(result.group(3))
                    if not read_db("Media Manager", "EXISTS", "playback_tv"): # should skip ifs and replace with try catch and own seperate function
                        if not write_db("Media Manager", "CREATE", "playback_tv",
                                        ["show", "series", "episodes", "elapsed_time"]):
                            return False
                    if not read_db("Media Manager", "EXISTS", "playback_tv", "show", "show", vlc_result['name']):
                        if write_db("Media Manager", "INSERT", "playback_tv", [vlc_result['name'], vlc_result['series'],
                                                                        vlc_result['episode'], vlc_result['time']]):
                            return True
                        else:
                            return False
                    else:
                        if write_db("Media Manager", "UPDATE", "playback_tv",
                                ["series", "episodes", "elapsed_time"],
                                [vlc_result['series'], vlc_result['episode'], vlc_result['time']],
                                ["show", "show", "show"],
                                [vlc_result['name'], vlc_result['name'], vlc_result['name']] ):
                            return True
                        else:
                            return False
                else:
                    if not read_db("Media Manager", "EXISTS", "playback_film"):
                        if not write_db("Media Manager", "CREATE", "playback_film",
                                        ["show", "elapsed_time", "view count"]):
                            return False
                    if not read_db("Media Manager", "EXISTS", "playback_film", "show", "show", child.text):
                        if write_db("Media Manager", "INSERT", "playback_film", [child.text, vlc_result['time'], None]):
                            return True
                        else:
                            return False
                    else:
                        if write_db("Media Manager", "UPDATE", "playback_film",
                                ["elapsed_time", "view count"],
                                [vlc_result['time'], None],
                                ["show", "show", "show"],
                                [child.text, child.text, child.text] ):
                            return True
                        else:
                            return False
        return True
    else:
        print(r.status_code)
        return False

def fetch_film_metadata():
    global program_settings, media_cache_dict
    for i in media_cache_dict['video']['files']:
        result = re.search("(.*) - s(\d{2})e(\d{2})", i)  # If I Make This Expression A Setting Any Naming Scheme Could Be Used
        if result:
            continue
        # actually checking the file is a video file would help
        film = i
        proc_film = quote(film)
        film_api_url = "https://api.themoviedb.org/3/"
        full_url = film_api_url + "search/movie?api_key=" + program_settings['moviedb key'] + "&language=en&query=" + proc_film + "&include_adult=false"
        results_raw = requests.get(full_url)
        results_json = json.loads(results_raw.text)
        if results_raw.status_code == 200:
            if results_raw.text != "":
                if not os.path.isdir("static\\thumbs"):
                    os.makedirs("static\\thumbs")
                    print("directory made")
                if len(results_json['results']) == 0:
                    # manipulate the string and retry (remove junk in file name)
                    print("No Results Found For " + str(i))
                    if not read_db("Media Manager", "EXISTS", "metadata_missing_film"):
                        if not write_db("Media Manager", "CREATE", "metadata_missing_film", ["show"]):
                            return False
                    if not read_db("Media Manager", "EXISTS", "metadata_missing_film", "show", "show", film):
                        if write_db("Media Manager", "INSERT", "metadata_missing_film", [film]):
                            continue
                        else:
                            return False
                # check the validity of results. If multiple results make sure top few matches are not similar. battlestar galactica has a remake, make sure you get the version you have
                # if top few matches are similar just grab the most recent one unless a date is found in the file name
                print("https://image.tmdb.org/t/p/w500" + results_json['results'][0]['poster_path'])
                r = requests.get("https://image.tmdb.org/t/p/w500" + results_json['results'][0]['poster_path'], allow_redirects=True)
                open("static\\thumbs" + str(results_json['results'][0]['poster_path']), 'wb').write(r.content)
                print(str(results_json['results'][0]['poster_path']).replace("/", ""))
                if not read_db("Media Manager", "EXISTS", "metadata_film"):
                    if not write_db("Media Manager", "CREATE", "metadata_film",
                                    ["show", "thumbnail", "description", "genre", "rating", "tags", "relatedness"]):
                        return False
                if not read_db("Media Manager", "EXISTS", "metadata_film", "show", "show", film):
                    if write_db("Media Manager", "INSERT", "metadata_film", [film,
                                                        "static\\thumbs\\" + str(results_json['results'][0]['poster_path'].replace("/", "")),
                                                        results_json['results'][0]['overview'],
                                                        str(results_json['results'][0]['genre_ids']),
                                                        results_json['results'][0]['vote_average'], None, None]):
                        continue
                    else:
                        return False
                if write_db("Media Manager", "UPDATE", "metadata_film",
                            ["thumbnail", "description", "genre", "rating", "tags", "relatedness"],
                            ["static\\thumbs\\" + str(results_json['results'][0]['poster_path'].replace("/", "")),
                             results_json['results'][0]['overview'],
                             str(results_json['results'][0]['genre_ids']),
                             results_json['results'][0]['vote_average'], None, None],
                            ["show", "show", "show", "show", "show", "show"], [film, film, film, film, film, film]):
                    continue
                else:
                    return False
        else:
            print(results_raw.status_code)
        time.sleep(1)

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
    login_status = login_tvdb() # Returns True if succesful
    if not login_status:
        return False
    else:
        for directory in media_cache_dict['video']['folders']:
            if directory.isdigit() == True or "Extras" in directory or "Subs" in directory or "Specials" in directory or "Season" in directory:
                print("Blocked Request for " + str(directory))
            else:
                auth_header = {}
                auth_header["Authorization"] = "Bearer " + login_status
                time.sleep(2)
                r = requests.get(base_url + search + "?name=" + quote(directory), headers=auth_header)
                if r.status_code == 200:
                    # check the validity of results. If multiple results make sure top few matches are not similar. battlestar galactica has a remake, make sure you get the version you have
                    # if top few matches are similar just grab the most recent one unless a date is found in the file name
                    results = json.loads(r.text)['data']
                    iterate_till_valid = 0
                    while iterate_till_valid < len(results): # TVDB sometimes returns results that are missing everything
                        series_id = json.loads(r.text)['data'][iterate_till_valid]['id']
                        series_thumb = json.loads(r.text)['data'][iterate_till_valid]['banner']
                        series_description = json.loads(r.text)['data'][iterate_till_valid]['overview']
                        if series_thumb != "":
                            break
                        iterate_till_valid = iterate_till_valid + 1
                    series_thumb = series_thumb.replace("graphical/", "")
                    if not os.path.isdir("static\\thumbs"):
                        os.makedirs("static\\thumbs")
                    time.sleep(0.5) # If too many requests made in a short space of time the website will block you
                    r = requests.get("https://www.thetvdb.com/banners/graphical/" + series_thumb, allow_redirects=True)
                    open("static\\thumbs\\" + str(series_thumb), 'wb').write(r.content) # Save thumbnail
                    if not read_db("Media Manager", "EXISTS", "metadata_tv"): # Check the table for tv metadata exists, create if not. if creation fails return False
                        if not write_db("Media Manager", "CREATE", "metadata_tv",
                                        ["show", "thumbnail", "description"]):
                            return False
                    if not read_db("Media Manager", "EXISTS", "metadata_tv", "show", "show", directory): # Check that an entry is present. If not insert. Otherwise update
                        if not write_db("Media Manager", "INSERT", "metadata_tv", [directory,
                                                                                    "static\\thumbs\\" + str(series_thumb),
                                                                                    series_description, None]):
                            return False
                    else:
                        if not write_db("Media Manager", "UPDATE", "metadata_tv",
                                        ["thumbnail", "description"],
                                        ["static\\thumbs\\" + str(series_thumb),
                                        series_description],
                                        ["show", "show"],
                                        [directory, directory]): # If Not
                            return False
                    for media in media_cache_dict['video']['files']:
                        result = re.search("(.*) - s(\d{2})e(\d{2})", media) # If I Make This Expression A Setting Any Naming Scheme Could Be Used
                        if result:
                            if result.group(1) == directory: # Only files with "name - sxxexx" name format, this filters out episodes from media_cache_dict['video']['files']:
                                time.sleep(0.3)
                                r = requests.get(base_url + "/series/" + str(series_id) + "/episodes/query?airedSeason=" + str(result.group(2)) + "airedEpisode=" + str(result.group(3)), headers=auth_header)
                                try:
                                    whatisthis = json.loads(r.text)['data'][int(result.group(3)) - 1]['episodeName']
                                except:
                                    continue
                                if r.status_code == 200: # The tvdb api returns all episodes even if a specific episode is in query, bastards
                                    episode_no = json.loads(r.text)['data'][int(result.group(3)) - 1]['airedEpisodeNumber']
                                    season_no = json.loads(r.text)['data'][int(result.group(3)) - 1]['airedSeason']
                                    episode_name = json.loads(r.text)['data'][int(result.group(3)) - 1]['episodeName']
                                    episode_desc = json.loads(r.text)['data'][int(result.group(3)) - 1]['overview']
                                    if not read_db("Media Manager", "EXISTS", directory): # Create table if not exists
                                        if not write_db("Media Manager", "CREATE", directory,
                                                        ["episode_name", "season_number", "episode_number", "description"]):
                                            return False
                                    if not read_db("Media Manager", "EXISTS", directory, "episode_name", "episode_name", episode_name): # If not exists, insert. Otherwise update
                                        print("inserting")
                                        if not write_db("Media Manager", "INSERT", directory, [episode_name,
                                                                                                   season_no,
                                                                                                   episode_no,
                                                                                                   episode_desc]):
                                            return False
                                    else:
                                        print("updating")
                                        if not write_db("Media Manager", "UPDATE", directory,
                                                        ["episode_name", "season_number", "episode_number", "description"],
                                                        [episode_name, season_no, episode_no, episode_desc],
                                                        ["episode_name", "episode_name", "episode_name", "episode_name"],
                                                        [episode_name, episode_name, episode_name, episode_name]):
                                            return False
                                else:
                                    print("Failed Search With Status Code " + str(r.status_code))
                    print("")
                else:
                    print("Failed Search With Status Code " + str(r.status_code))
                    #return False

def render_template(template_filename, context):
    return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)

def create_index_html(debug = False):
    global program_settings, media_cache_dict
    setting_names, setting_values = [], []
    film_names, film_thumbnail, film_description, film_score = [], [], [], []
    tv_names, tv_thumbnail, tv_description = [], [], []
    tv_show_dict = {}
    print("create_index_html")
    print(program_settings)
    print(read_db("Media Manager", "EXISTS", "metadata_film"))
    if not read_db("Media Manager", "EXISTS", "metadata_film"):
        write_db("Media Manager", "CREATE", "metadata_film", ["show", "thumbnail", "description", "genre", "rating", "tags", "relatedness"])
    film_metadata = read_db("Media Manager", "DUMP", "metadata_film")
    for i in film_metadata:
        if i[0] in media_cache_dict['video']['files'] or debug == True:
            film_names.append(i[0])
            film_thumbnail.append(i[1])
            film_description.append(i[2])
            film_score.append(i[4])
        else:
            film_names.append(i[0])
            film_thumbnail.append("thumbs/none.jpg")
            film_description.append("No Metadata For This File!")
            film_score.append("NA")
    if not read_db("Media Manager", "EXISTS", "metadata_tv"):
        write_db("Media Manager", "CREATE", "metadata_tv", ["show", "thumbnail", "description", "tags"])
    tv_metadata = read_db("Media Manager", "DUMP", "metadata_tv")
    for i in tv_metadata:
        if i[0] in media_cache_dict['video']['folders'] or debug == True:
            tv_names.append(i[0])
            tv_thumbnail.append(i[1])
            tv_description.append(i[2])
            tv_show_dict[i[0]] = {}
            if not read_db("Media Manager", "EXISTS", i[0]): # Create table if not exists
                if not write_db("Media Manager", "CREATE", i[0],
                                ["episode_name", "season_number", "episode_number", "description"]):
                    return False
            season_metadata = read_db("Media Manager", "DUMP", i[0])
            for x in season_metadata:
                if len(str(x[1])) == 1:
                    season = "0" + str(x[1])
                else:
                    season = str(x[1])
                if len(str(x[2])) == 1:
                    ep = "0" + str(x[2])
                else:
                    ep = str(x[2])
                if not season in tv_show_dict[i[0]]:
                    tv_show_dict[i[0]][season] = {}
                if not ep in tv_show_dict[i[0]][season]:
                    tv_show_dict[i[0]][season][ep] = {}
                tv_show_dict[i[0]][season][ep][str(x[0])] = x[3]
        else:
            tv_names.append(i[0])
            tv_thumbnail.append("thumbs/none.jpg")
            tv_description.append("No Metadata For This File!")
            tv_show_dict[i[0]] = {}
            tv_show_dict[i[0]]['0'] = {}
            tv_show_dict[i[0]]['0']['0'] = {}
            tv_show_dict[i[0]]['0']['0']['0'] = "NA"
    for i in program_settings:
        setting_names.append(i)
        setting_values.append(program_settings[i])

    film_metadata = zip(film_names, film_thumbnail, film_description, film_score)
    tv_metadata = zip(tv_names, tv_thumbnail, tv_description)
    settings = zip(setting_names, setting_values)
    fname = "templates/output.html"
    context = {
        'settings': settings,
        'film_metadata' : film_metadata,
        'tv_metadata' : tv_metadata,
        'episode_metadata' : tv_show_dict,
        'tv_resume' : read_db("Media Manager", "DUMP", "playback_tv")
        #'film_resume' : read_db("Media Manager", "DUMP", "playback_film")
    }
    context2 = copy.deepcopy(context) # Must deepcopy, can't reuse. Not sure why.
    #
    with open(fname, 'w', encoding='utf-8') as f:
        html = render_template('main.html', context)
        f.write(html)
    #
    with open("templates/reveals_out.html", 'w', encoding='utf-8') as f:
        html = render_template('reveals.html', context2)
        f.write(html)
	
def exit_all():
    print("Quitting")
    os._exit(0)

if load_config():
    print("Config File Loaded")
else:
    print("Failed To Load Config File, Exiting")
    exit_all()
   
if cache_media([program_settings['film directory'], program_settings['tv directory']], "video"):
    print("Cache Loaded")
else:
    print("Failed to Load Cache")
    
#play(search_media("ENCODED_20170601_120017"), "play")
TEMPLATE_ENVIRONMENT = Environment(autoescape=False, loader=FileSystemLoader("templates"), trim_blocks=False)
create_index_html(True) # Pass True To Display Metadata In Database Without Any Media Attatched
h = threading.Thread(target=html_interface)
h.start()

time.sleep(1)

chrome_path = r'"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"'
#chrome_path = r'"E:\chrome\GoogleChromePortable"' # Portable Chrome
url = "http://localhost:5006/"
#p = subprocess.Popen(chrome_path + " --app=" + url)

while True:
    if vlc_state() == True:
        print("VLC Server Information Read")
        if int(vlc_result['length']) - int(vlc_result['time']) <= 10:
            if next_ep() == True:
                print("Playing Next Episode")
                time.sleep(11) # need to make this less lazy
            else:
                print("Failed To Play Next Episode")
    else:
        print("Could Not Read VLC Server")
    time.sleep(5)
    #print(vlc_result)

