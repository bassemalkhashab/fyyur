#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from operator import ge
import re
import dateutil.parser
import babel
import datetime
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form, form
from flask_wtf import CSRFProtect
from sqlalchemy.orm import backref
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

# TODO: connect to a local postgresql database
app = Flask(__name__)
csrf = CSRFProtect()
csrf.init_app(app)
moment = Moment(app)
app.config.from_object('config')


db = SQLAlchemy(app)
migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


from models import *

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
  data=[]
  state_data= db.session.query(Venue.state, Venue.city).group_by(Venue.state, Venue.city).all()

  for i in range(len(state_data)):
    data.append({
      'city':state_data[i][1],
      'state':state_data[i][0],
      'venues':db.session.query(Venue.name, Venue.id).filter_by(state= state_data[i][0], city=state_data[i][1]).all()
    })
  
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search = request.form.get('search_term')
  countResponse = db.session.query(Venue).filter(Venue.name.ilike(f'%{search}%')).count()
  data =  db.session.query(Venue).filter(Venue.name.ilike(f'%{search}%')).all()
  response={
    "count": countResponse,
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data = db.session.query(Venue).filter_by(id = venue_id).first()
  upcommingShows = db.session.query(Artist.name.label('artist_name'), Show.artist_id.label('artist_id'),Artist.image_link.label('artist_image_link') , Show.start_time).join(Show, Artist.id == Show.artist_id).filter(Show.venue_id == venue_id).filter(Show.past_or_upcomming == 'upcomming').all()
  pastShows = db.session.query(Artist.name.label('artist_name'), Show.artist_id.label('artist_id'),Artist.image_link.label('artist_image_link') , Show.start_time).join(Show, Artist.id == Show.artist_id).filter(Show.venue_id == venue_id).filter(Show.past_or_upcomming == 'past').all()
  data.past_shows = pastShows
  data.upcoming_shows = upcommingShows
  data.upcoming_shows_count = len(upcommingShows)
  data.past_shows_count = len(pastShows)
  
  
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
  form = VenueForm()
  if form.validate_on_submit():
    try:
      name= request.form.get('name')
      city= request.form.get('city')
      state= request.form.get('state')
      address= request.form.get('address')
      phone= request.form.get('phone')
      genres = request.form.get('genres')
      facebook_link= request.form.get('facebook_link')
      image_link= request.form.get('image_link')
      _seekingTalent= request.form.get('seeking_talent')
      seekingTalent= True if _seekingTalent == "y" else False
      seekingTalentDescription = request.form.get('seeking_description')
      website = request.form.get('website')
      venue= Venue(name= name, city= city, state= state, address= address, phone= phone, genres= genres, facebook_link= facebook_link, image_link= image_link, seeking_talent= seekingTalent, seeking_description= seekingTalentDescription, website= website)
      db.session.add(venue)
      db.session.commit()
    # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
      db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
      flash('An error occurred. Venue ' + name + ' could not be listed.')
    finally:
      db.session.close()

  else:
    for error in form.errors:
      flash(error)
      print(error)
    print(form)
    print(form.errors)
  return render_template('pages/home.html')
  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data=db.session.query(Artist.id, Artist.name).all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search = request.form.get('search_term')
  countResponse = db.session.query(Artist).filter(Artist.name.ilike(f'%{search}%')).count()
  data =  db.session.query(Artist).filter(Artist.name.ilike(f'%{search}%')).all()
  response={
    "count": countResponse,
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
  data = db.session.query(Artist).filter_by(id = artist_id).first()
  upcommingShows = db.session.query(Venue.name.label('venue_name'), Show.venue_id.label('venue_id'),Venue.image_link.label('venue_image_link'), Show.start_time).join(Show, Venue.id == Show.venue_id).filter(Show.artist_id == artist_id).filter(Show.past_or_upcomming == 'upcomming').all()
  pastShows = db.session.query(Venue.name.label('venue_name'), Show.venue_id.label('venue_id'),Venue.image_link.label('venue_image_link'), Show.start_time).join(Show, Venue.id == Show.venue_id).filter(Show.artist_id == artist_id).filter(Show.past_or_upcomming == 'past').all()
  data.past_shows = pastShows
  data.upcoming_shows = upcommingShows
  data.upcoming_shows_count = len(upcommingShows)
  data.past_shows_count = len(pastShows)

  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = db.session.query(Artist).filter_by(id = artist_id).first()
  
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm()
  if form.validate_on_submit():
    try:
      _artist = db.session.query(Artist).filter_by(id = artist_id).first()
      _artist.name = request.form.get('name')
      _artist.city = request.form.get('city')
      _artist.state = request.form.get('state')
      _artist.phone = request.form.get('phone')
      _artist.genres = request.form.get('genres')
      _artist.facebook_link = request.form.get('facebook_link')
      _artist.website = request.form.get('website') 
      _seekingVenue = request.form.get('seeking_venue') 
      _artist.seeking_venue = True if _seekingVenue == "y" else False
      _artist.seeking_description = request.form.get('seeking_description') 
      _artist.image_link = request.form.get('image_link') 
      db.session.commit()
    except:
      db.session.rollback()
    finally:
      db.session.close()

  else:
    for error in form.errors:
      flash(error)
      print(error)
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = db.session.query(Venue).filter_by(id = venue_id).first()
  
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm()
  if form.validate_on_submit():
    try:
      _venue = db.session.query(Venue).filter_by(id = venue_id).first()
      _venue.name = request.form.get('name')
      _venue.city = request.form.get('city')
      _venue.state = request.form.get('state')
      _venue.phone = request.form.get('phone')
      _venue.address = request.form.get('address')
      _venue.genres = request.form.get('genres') 
      _venue.facebook_link = request.form.get('facebook_link') 
      _venue.website = request.form.get('website') 
      _seekingArtist = request.form.get('seeking_talent') 
      _venue.seeking_talent = True if _seekingArtist == "y" else False
      _venue.seeking_description = request.form.get('seeking_description') 
      _venue.image_link = request.form.get('image_link') 
      db.session.commit()
    except:
      db.session.rollback()
    finally:
      db.session.close()

  else:
    for error in form.errors:
      flash(error)
      print(error)
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
  
  form = ArtistForm()
  if form.validate_on_submit():
    try:
      name = request.form.get('name')
      city = request.form.get('city')
      state = request.form.get('state')
      phone = request.form.get('phone')
      genres = request.form.get('genres')
      facebook_link = request.form.get('facebook_link')
      image_link= request.form.get('image_link')
      _seekingVenue= request.form.get('seeking_venue')
      seekingVenue= True if _seekingVenue == "y" else False
      seekingVenueDescription = request.form.get('seeking_description')
      website = request.form.get('website')
      artist= Artist(name= name, city= city, state= state, phone= phone, genres= genres, facebook_link= facebook_link, image_link=image_link, website= website, seeking_venue=seekingVenue, seeking_description= seekingVenueDescription)
      db.session.add(artist)
      db.session.commit()
    # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
      db.session.rollback()
      # TODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
      flash('An error occurred. Artist ' + name + ' could not be listed.')
    finally:
      db.session.close()

  else:
    for error in form.errors:
      flash(error)
      print(error)
  return redirect(url_for('index'))

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
    data.append({
      "venue_id": show.venues[0].id,
      "venue_name": show.venues[0].name,
      "artist_id": show.artists[0].id,
      "artist_name": show.artists[0].name,
      "artist_image_link": show.artists[0].image_link,
      "start_time": str(show.start_time)
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

    artistId = request.form.get('artist_id')
    venueId = request.form.get('venue_id')
    startTime = request.form.get('start_time')
    artist = Artist.query.filter_by(id = artistId).first()
    venue = Venue.query.filter_by(id = venueId).first()
    date_now = str(datetime.now())
    pastOrUpcomming = "past" if startTime < date_now else "upcomming"
    show = Show(start_time= startTime , past_or_upcomming =pastOrUpcomming , artist_id = artistId , venue_id = venueId)
    db.session.add(show)
    artist.show_artists.append(show)
    venue.show_venues.append(show)
    db.session.commit()
  # on successful db insert, flash success
    flash('Show was successfully listed!')

  except:

    db.session.rollback()
  # TODO: on unsuccessful db insert, flash an error instead.
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  # e.g., flash('An error occurred. Show could not be listed.')
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
