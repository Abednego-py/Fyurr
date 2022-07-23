# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

from cgitb import reset
from email.policy import default
from ssl import ALERT_DESCRIPTION_UNRECOGNIZED_NAME
import dateutil.parser
import babel
from flask import render_template, request, flash, redirect, url_for
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from datetime import datetime
from datetime import *
from dateutil import *
from dateutil.tz import *
import pytz
from config import SQLALCHEMY_DATABASE_URI
from models import app, db, Venue, Artist, Shows

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#


moment = Moment(app)
app.config.from_object("config")
db.init_app(app)

app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format="full"):
    date = dateutil.parser.parse(value)
    if format == "full":
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == "medium":
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


locale = "en"
app.jinja_env.filters["datetime"] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route("/")
def index():
    return render_template("pages/home.html")


#  Venues
#  ----------------------------------------------------------------


@app.route("/venues")
def venues():

    data_ = []
    venue = []
    venueObj = {}

    # get the venue data order by city
    result = Venue.query.order_by(Venue.city).all()

    # loop through the venue data and store the result in a list
    for i in result:
        if i.city not in data_:
            data_.append(i)

    for i in range(len(result)):
        if (
            result[i].city != result[i - 1].city
            and result[i].state != result[i - 1].state
        ):
            venueObj = {}
            venue = []
            venueObj["id"] = result[i].id
            venueObj["name"] = result[i].name
            shows = Shows.query.filter(
                Shows.start_time > datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ).all()
            num = [j for j in range(len(shows)) if result[i].id == shows[j].venue_id]
            venueObj["num_upcoming_shows"] = len(num)
            venue.append(venueObj)
            data_[i].venues = venue

        else:
            venueObj = {}
            venueObj["id"] = result[i].id
            venueObj["name"] = result[i].name
            shows = Shows.query.filter(
                Shows.start_time > datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ).all()
            num = [j for j in range(len(shows)) if result[i].id == shows[j].venue_id]
            venueObj["num_upcoming_shows"] = len(num)
            venue.append(venueObj)
            data_[i].venues = venue

    data = []
    for i in range(len(data_)):
        if data_[i].city != data_[i - 1].city and data_[i].state != data_[i - 1].state:
            data.append(data_[i])

    return render_template("pages/venues.html", areas=data)


@app.route("/venues/search", methods=["POST"])
def search_venues():

    search_term = request.form.get("search_term")
    response = {
        "count": len(
            Venue.query.filter(Venue.name.ilike("%" + search_term + "%")).all()
        ),
        "data": Venue.query.filter(Venue.name.ilike("%" + search_term + "%")).all(),
    }

    return render_template(
        "pages/search_venues.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


@app.route("/venues/<int:venue_id>")
def show_venue(venue_id):

    result = Venue.query.all()
    data_ = []
    dataObj = {}

    """
  Loop through each record in the Venues table and get the required data. Then append the object to a list
  
  """
    for i in range(len(result)):
        dataObj["id"] = result[i].id
        dataObj["city"] = result[i].city
        dataObj["state"] = result[i].state
        dataObj["name"] = result[i].name
        dataObj["phone"] = result[i].phone
        dataObj["address"] = result[i].address
        dataObj["website_link"] = result[i].website_link
        dataObj["facebook_link"] = result[i].facebook_link
        dataObj["seeking_talent"] = result[i].seeking_talent
        dataObj["image_link"] = result[i].image_link
        dataObj["seeking_description"] = result[i].seeking_description
        # the genres record is a string so we have to modify the data to a list of string
        result[i].genres = result[i].genres.replace("{", "")
        result[i].genres = result[i].genres.replace("}", "")
        dataObj["genres"] = [i for i in list((result[i].genres).split(","))]

        dataObj["past_shows"] = (
            db.session.query(Shows)
            .join(Venue)
            .filter(Shows.venue_id == result[i].id)
            .filter(Shows.start_time < datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            .all()
        )
        dataObj["upcoming_shows"] = (
            db.session.query(Shows)
            .join(Venue)
            .filter(Shows.venue_id == result[i].id)
            .filter(Shows.start_time > datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            .all()
        )
        dataObj["past_shows_count"] = len(dataObj["past_shows"])
        dataObj["upcoming_shows_count"] = len(dataObj["upcoming_shows"])

        for i in range(len(dataObj["past_shows"])):
            dataObj["past_shows"][i].artist_name = dataObj["past_shows"][i].artist.name
            dataObj["past_shows"][i].artist_image_link = dataObj["past_shows"][
                i
            ].artist.image_link

        for i in range(len(dataObj["upcoming_shows"])):
            dataObj["upcoming_shows"][i].artist_name = dataObj["upcoming_shows"][
                i
            ].artist.name
            dataObj["upcoming_shows"][i].artist_image_link = dataObj["upcoming_shows"][
                i
            ].artist.image_link

        data_.append(dataObj)
        dataObj = {}

    data = list(filter(lambda d: d["id"] == venue_id, data_))[0]
    return render_template("pages/show_venue.html", venue=data)


#  Create Venue
#  ----------------------------------------------------------------


@app.route("/venues/create", methods=["GET"])
def create_venue_form():
    form = VenueForm()
    return render_template("forms/new_venue.html", form=form)


@app.route("/venues/create", methods=["POST"])
def create_venue_submission():

    form = VenueForm()
    try:
        name = form.name.data
        address = form.address.data
        city = form.city.data
        state = form.state.data
        phone = form.phone.data
        image_link = form.image_link.data
        facebook_link = form.facebook_link.data
        genre = form.genres.data
        website_link = form.website_link.data
        seeking_talent = form.seeking_talent.data
        seeking_description = form.seeking_description.data

        venue = Venue(
            name=name,
            city=city,
            state=state,
            address=address,
            phone=phone,
            image_link=image_link,
            facebook_link=facebook_link,
            genres=genre,
            seeking_talent=seeking_talent,
            seeking_description=seeking_description,
            website_link=website_link,
        )
        db.session.add(venue)
        db.session.commit()
        flash("Venue " + request.form["name"] + " was successfully listed!")
    except:
        db.session.rollback()
        flash(
            "An error occurred. Venue " + request.form["name"] + " could not be listed."
        )
    finally:
        db.session.close()
    return render_template("pages/home.html")


@app.route("/venues/<venue_id>", methods=["DELETE"])
def delete_venue(venue_id):
    error = False
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for("venues"))


#  Artists
#  ----------------------------------------------------------------
@app.route("/artists")
def artists():

    return render_template("pages/artists.html", artists=Artist.query.all())


@app.route("/artists/search", methods=["POST"])
def search_artists():
    search_term = request.form.get("search_term")
    response = {
        "count": len(
            Artist.query.filter(Artist.name.ilike("%" + search_term + "%")).all()
        ),
        "data": Artist.query.filter(Artist.name.ilike("%" + search_term + "%")).all(),
    }
    return render_template(
        "pages/search_artists.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


@app.route("/artists/<int:artist_id>")
def show_artist(artist_id):

    result = Artist.query.all()
    data_ = []
    dataObj = {}

    """
  Loop through the Artist table and get the fields for each record. Store each data using an object. Then append
  to a list
  """

    for i in range(0, len(result)):
        dataObj["id"] = result[i].id
        dataObj["name"] = result[i].name
        result[i].genres = result[i].genres.replace("{", "")
        result[i].genres = result[i].genres.replace("}", "")
        dataObj["genres"] = [i for i in list((result[i].genres).split(","))]
        dataObj["city"] = result[i].city
        dataObj["state"] = result[i].state
        dataObj["phone"] = result[i].phone
        dataObj["seeking_venue"] = result[i].seeking_venue
        dataObj["image_link"] = result[i].image_link
        dataObj["facebook_link"] = result[i].facebook_link
        dataObj["website"] = result[i].website_link
        dataObj["seeking_description"] = result[i].seeking_description

        dataObj["past_shows"] = (
            db.session.query(Shows)
            .join(Artist)
            .filter(Shows.artist_id == result[i].id)
            .filter(Shows.start_time < datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            .all()
        )
        dataObj["upcoming_shows"] = (
            db.session.query(Shows)
            .join(Artist)
            .filter(Shows.artist_id == result[i].id)
            .filter(Shows.start_time > datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            .all()
        )
        dataObj["past_shows_count"] = len(dataObj["past_shows"])
        dataObj["upcoming_shows_count"] = len(dataObj["upcoming_shows"])

        for i in range(len(dataObj["past_shows"])):
            dataObj["past_shows"][i].venue_name = dataObj["past_shows"][i].venue.name
            dataObj["past_shows"][i].venue_image_link = dataObj["past_shows"][
                i
            ].venue.image_link

        for i in range(len(dataObj["upcoming_shows"])):
            dataObj["upcoming_shows"][i].venue_name = dataObj["upcoming_shows"][
                i
            ].venue.name
            dataObj["upcoming_shows"][i].venue_image_link = dataObj["upcoming_shows"][
                i
            ].venue.image_link

        data_.append(dataObj)
        dataObj = {}

    data = list(filter(lambda d: d["id"] == artist_id, data_))[0]
    return render_template("pages/show_artist.html", artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route("/artists/<int:artist_id>/edit", methods=["GET"])
def edit_artist(artist_id):
    form = ArtistForm()
    import re

    currentArtist = Artist.query.filter(Artist.id == artist_id).first()
    form.name.data = re.sub("[()" ",]", "", str(currentArtist.name))
    form.genres.data = currentArtist.genres
    form.city.data = currentArtist.city
    form.state.data = currentArtist.state
    form.phone.data = currentArtist.phone
    form.website_link.data = currentArtist.website_link
    form.facebook_link.data = currentArtist.facebook_link
    form.seeking_venue.data = currentArtist.seeking_venue
    form.seeking_description.data = currentArtist.seeking_description
    form.image_link.data = currentArtist.image_link

    return render_template("forms/edit_artist.html", artist=currentArtist, form=form)


@app.route("/artists/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):

    form = ArtistForm()
    currentArtist = Artist.query.filter(Artist.id == artist_id).first()
    currentArtist.name = form.name.data
    currentArtist.genres = form.genres.data
    currentArtist.city = form.city.data
    currentArtist.state = form.state.data
    currentArtist.phone = form.phone.data
    currentArtist.website_link = form.website_link.data
    currentArtist.facebook_link = form.facebook_link.data
    currentArtist.seeking_venue = form.seeking_venue.data
    currentArtist.seeking_description = form.seeking_description.data
    currentArtist.image_link = form.image_link.data
    db.session.commit()

    return redirect(url_for("show_artist", artist_id=artist_id))


@app.route("/venues/<int:venue_id>/edit", methods=["GET"])
def edit_venue(venue_id):
    form = VenueForm()

    import re

    currentVenue = Venue.query.filter(Venue.id == venue_id).first()
    form.name.data = re.sub("[()" ",]", "", str(currentVenue.name))
    form.genres.data = currentVenue.genres
    form.address.data = currentVenue.address
    form.city.data = currentVenue.city
    form.state.data = currentVenue.state
    form.phone.data = currentVenue.phone
    form.website_link.data = currentVenue.website_link
    form.facebook_link.data = currentVenue.facebook_link
    form.seeking_talent.data = currentVenue.seeking_talent
    form.seeking_description.data = currentVenue.seeking_description
    form.image_link.data = currentVenue.image_link

    return render_template("forms/edit_venue.html", form=form, venue=currentVenue)


@app.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):

    form = VenueForm()
    currentVenue = Venue.query.filter(Venue.id == venue_id).first()
    currentVenue.name = form.name.data
    currentVenue.genres = form.genres.data
    currentVenue.city = form.city.data
    currentVenue.address = form.address.data
    currentVenue.state = form.state.data
    currentVenue.phone = form.phone.data
    currentVenue.website_link = form.website_link.data
    currentVenue.facebook_link = form.facebook_link.data
    currentVenue.seeking_venue = form.seeking_talent.data
    currentVenue.seeking_description = form.seeking_description.data
    currentVenue.image_link = form.image_link.data
    db.session.commit()

    return redirect(url_for("show_venue", venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------


@app.route("/artists/create", methods=["GET"])
def create_artist_form():
    form = ArtistForm()
    return render_template("forms/new_artist.html", form=form)


@app.route("/artists/create", methods=["POST"])
def create_artist_submission():
    form = ArtistForm()
    try:
        name = form.name.data
        genres = form.genres.data
        city = form.city.data
        state = form.state.data
        phone = form.phone.data
        image_link = form.image_link.data
        facebook_link = form.facebook_link.data
        seeking_venue = form.seeking_venue.data
        seeking_description = form.seeking_description.data
        website_link = form.website_link.data

        artist = Artist(
            name=name,
            city=city,
            state=state,
            genres=genres,
            phone=phone,
            image_link=image_link,
            facebook_link=facebook_link,
            seeking_venue=seeking_venue,
            seeking_description=seeking_description,
            website_link=website_link,
        )
        db.session.add(artist)
        db.session.commit()
        flash("Artist " + request.form["name"] + " was successfully listed!")
    except:
        db.session.rollback()
        flash(
            "An error occurred. Artist "
            + request.form["name"]
            + " could not be listed."
        )
    finally:
        db.session.close()

    return render_template("pages/home.html")


#  Shows
#  ----------------------------------------------------------------


@app.route("/shows")
def shows():

    showsData = {}
    dataObj = {}
    data_ = []
    utc_zone = tz.tzutc()
    utc_tz = pytz.utc
    result = Shows.query.all()
    for i in range(len(result)):
        dataObj["venue_id"] = result[i].venue_id
        dataObj["artist_id"] = result[i].artist_id
        dataObj["start_time"] = (
            (datetime.strptime(result[i].start_time, "%Y-%m-%d %H:%M:%S")).astimezone(
                utc_tz
            )
        ).strftime("%Y-%m-%d %H:%M:%S")
        dataObj["artist_name"] = result[i].artist.name
        dataObj["venue_name"] = result[i].venue.name
        dataObj["artist_image_link"] = result[i].artist.image_link
        data_.append(dataObj)
        dataObj = {}

    return render_template("pages/shows.html", shows=data_)


@app.route("/shows/create")
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template("forms/new_show.html", form=form)


@app.route("/shows/create", methods=["POST"])
def create_show_submission():
    form = ShowForm()
    try:
        venue_id = form.venue_id.data
        artist_id = form.artist_id.data
        start_time = form.start_time.data

        show = Shows(venue_id=venue_id, artist_id=artist_id, start_time=start_time)
        db.session.add(show)
        db.session.commit()
        flash("Show was successfully listed!")
    except:
        db.session.rollback()
        flash("An error occured. Show could not be listed")
    finally:
        db.session.close()
    return render_template("pages/home.html")


@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500


@app.errorhandler(400)
def FunctionName(args):
    return render_template("errors/400.html"), 400


@app.errorhandler(403)
def FunctionName(args):
    return render_template("errors/403.html"), 403


if not app.debug:
    file_handler = FileHandler("error.log")
    file_handler.setFormatter(
        Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("errors")

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == "__main__":
    app.run(debug=True)

# Or specify port manually:
"""
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
"""
