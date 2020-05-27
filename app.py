#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import date, datetime, time
from sqlalchemy.orm import relationship
from sqlalchemy import func
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:postgres@localhost:5432/fyyur'
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.ARRAY(db.String(120)))
    website = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean, default=True)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref=db.backref('Venue', lazy=True, cascade='all,delete'))

    def __init__(self, name, city, state, address, phone, facebook_link, genres, image_link='', website='', seeking_talent=False, seeking_description=''):
      self.name = name
      self.city = city
      self.state = state
      self.address = address
      self.phone = phone
      self.image_link = image_link
      self.facebook_link = facebook_link
      self.genres = genres
      self.website = website
      self.seeking_talent = seeking_talent

    def create(self):
      db.session.add(self)
      db.session.commit()

    def update(self):
      db.session.commit()

    def delete(self):
      db.session.delete(self)
      db.session.commit()

    @property
    def serialize(self):
      return {
        'id': self.id,
        'name': self.name,
        'city': self.city,
        'state': self.state,
        'address': self.address,
        'phone': self.phone,
        'image_link': self.image_link,
        'facebook_link': self.facebook_link,
        'genres': self.genres,
        'seeking_talent': self.seeking_talent,
        'seeking_description': self.seeking_description,
        'website': self.website
      }

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(500))
    seeking_venues = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref=db.backref('Artist', lazy=True))

    def create(self):
      db.session.add(self)
      db.session.commit()

    def update(self):
      
      db.session.commit()

    def artist_id_name(self):
      return {
        'id': self.id,
        'name': self.name
      }

    @property
    def serialize(self):
      return {
        'id': self.id,
        'name': self.name,
        'city': self.city,
        'state': self.state,
        'phone': self.phone,
        'genres': self.genres,
        'image_link': self.image_link,
        'facebook_link': self.facebook_link,
        'website': self.website,
        'seeking_venues': self.seeking_venues,
        'seeking_description': self.seeking_description
      }

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id', ondelete='CASCADE'))
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
    start_time = db.Column(db.DateTime())

    def __init__(self, venue_id, artist_id, start_time):
      self.venue_id = venue_id
      self.artist_id = artist_id
      self.start_time = start_time

    def create(self):
      db.session.add(self)
      db.session.commit()

    def delete(self):
      db.session.delete(self)
      db.session.commit()

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  # query city and state uniquely without any duplicates.
  unique_city_state = Venue.query.with_entities(
    Venue.city, Venue.state).distinct().all()
  data = []
  for cs in unique_city_state:
    venues = Venue.query.filter_by(city=cs[0], state=cs[1]).all()
    data.append({'city': cs[0], 'state': cs[1], 'venues': venues})
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  
  search_term = request.form.get('search_term', None) 
  query_venues = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_term))).all()
  count_venues = len(query_venues)
  data = {
    "count": count_venues,
    "data": [b.serialize for b in query_venues]
  }
  return render_template('pages/search_venues.html', results=data, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
  upcoming_shows = []
  past_shows = []
  shows = Show.query.filter_by(venue_id=venue_id).all()
  now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  for show in shows:
    artist = Artist.query.get(show.artist_id)
    artist_info = {
        'artist_id': show.artist_id,
        'artist_name': artist.name,
        'artist_image_link': artist.image_link,
        'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    }
    if show.start_time.strftime('%Y-%m-%d %H:%M:%S') > now:
      upcoming_shows.append(artist_info)
    else:
      past_shows.append(artist_info)

  venue = Venue.query.get(venue_id)
  data = {
    'id': venue.id,
    'name': venue.name,
    'city': venue.city,
    'state': venue.state,
    'address': venue.address,
    'phone': venue.phone,
    'image_link': venue.image_link,
    'facebook_link': venue.facebook_link,
    'website': venue.website,
    'genres': venue.genres,
    'seeking_talent': venue.seeking_talent,
    'seeking_description': venue.seeking_description,
    'upcoming_shows': upcoming_shows, 
    'upcoming_shows_count': len(upcoming_shows),
    'past_shows': past_shows,
    'past_shows_count': len(past_shows)
  }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    genres = request.form.getlist('genres')
    facebook_link = request.form['facebook_link']
    data = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres, facebook_link=facebook_link)
    Venue.create(data)
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  except:
    flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<int:venue_id>', methods=['POST'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    data = Venue.query.get(venue_id)
    Venue.delete(data)
    show_data = Show.query.get(venue_id)
    Show.delete(show_data)
    flash('Venue ' + data.name + ' was successfully deleted!')
  except:
    flash('An error occurred. Venue ' + data.name + ' could not be deleted.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  # >> Please look at the delete button in the show_venue.html

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  query_artists = Artist.query.all()
  data = map(Artist.artist_id_name, query_artists)
  list_data = list(data)
  return render_template('pages/artists.html', artists=list_data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_term = request.form.get('search_term', None)
  query_artists = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_term))).all()
  count_artists = len(query_artists)
  response = {
    "count": count_artists,
    "data": [b.serialize for b in query_artists]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  upcoming_shows = []
  past_shows = []
  shows = Show.query.filter_by(artist_id=artist_id).all()
  now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  for show in shows:
    venue = Venue.query.get(show.venue_id)
    show_info = {
      'venue_id': show.venue_id,
      'venue_name': venue.name,
      'venue_image_link': venue.image_link,
      'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    }
    if show.start_time.strftime('%Y-%m-%d %H:%M:%S') > now:
      upcoming_shows.append(show_info)
    else:
      past_shows.append(show_info)

  artist = Artist.query.get(artist_id)
  data = {
    'id': artist.id,
    'name': artist.name,
    'city': artist.city,
    'state': artist.state,
    'phone': artist.phone,
    'website': artist.website,
    'genres': artist.genres,
    'image_link': artist.image_link,
    'facebook_link': artist.facebook_link,
    'seeking_venues': artist.seeking_venues,
    'upcoming_shows': upcoming_shows,
    'upcoming_shows_count': len(upcoming_shows),
    'past_shows': past_shows,
    'past_shows_count': len(past_shows)
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  # TODO: populate form with fields from artist with ID <artist_id>
  artist = Artist.query.get(artist_id)
  form.name.data = artist.name
  form.genres.data = artist.genres
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.facebook_link.data = artist.facebook_link  
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    form = ArtistForm(request.form)
    artist = Artist.query.get(artist_id)
    artist.name = request.form['name']
    artist.genres = request.form.getlist('genres')
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.facebook_link = request.form['facebook_link']
    Artist.update(artist)
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # TODO: populate form with values from venue with ID <venue_id>
  venue = Venue.query.get(venue_id)
  form.name.data = venue.name
  form.genres.data = venue.genres
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.facebook_link.data = venue.facebook_link
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    venue.name = request.form['name']
    venue.genres = request.form.getlist('genres')
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.facebook_link = request.form['facebook_link']
    Venue.update(venue)
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    genres = request.form.getlist('genres')
    facebook_link = request.form['facebook_link']
    data = Artist(name=name, city=city, state=state, phone=phone, genres=genres, facebook_link=facebook_link)
    Artist.create(data)

    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  except:
    flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  
  data = []
  shows = Show.query.all()
  for show in shows:
    venue = Venue.query.get(show.venue_id)
    artist = Artist.query.get(show.artist_id)
    data.append({
      "venue_id": show.venue_id,
      "venue_name": venue.name,
      "artist_id": show.artist_id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']
    data = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    Show.create(data)
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  except:
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
