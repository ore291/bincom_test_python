from __future__ import annotations
from flask import Flask, render_template, flash, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from typing import List
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from datetime import datetime

# create the object of Flask
app = Flask(__name__)

app.config['SECRET_KEY'] = 'BAmbooty291..'


# SqlAlchemy Database Configuration With Mysql
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://sql8632439:g5ISZDB2Aw@sql8.freemysqlhosting.net/sql8632439'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)


class Lga(db.Model):
    __tablename__ = 'lga'
    uniqueid = db.Column(db.Integer, primary_key=True)
    lga_id = db.Column(db.Integer)
    lga_name = db.Column(db.String(100))
    wards: Mapped[List["Ward"]] = db.relationship(
        'Ward', back_populates='lga', lazy=True)
    polling_units: Mapped[List["Pu"]] = db.relationship(
        'Pu', back_populates='lga', lazy=True)


class Ward(db.Model):
    __tablename__ = 'ward'
    uniqueid = db.Column(db.Integer, primary_key=True)
    ward_id = db.Column(db.Integer)
    ward_name = db.Column(db.String(100))
    lga_id: Mapped[int] = mapped_column(ForeignKey("lga.lga_id"))
    lga: Mapped["Lga"] = relationship(back_populates="wards", lazy=True)
    polling_units: Mapped[List["Pu"]] = db.relationship(
        'Pu', back_populates='ward', lazy=True)


class Pu(db.Model):
    __tablename__ = 'polling_unit'
    uniqueid = db.Column(db.Integer, primary_key=True)
    polling_unit_id = db.Column(db.Integer)
    polling_unit_name = db.Column(db.String(100))
    lat = db.Column(db.String(100))
    long = db.Column(db.String(100))
    polling_unit_description = db.Column(db.String(100))
    polling_unit_number = db.Column(db.String(100))
    entered_by_user = db.Column(db.String(100))
    ward_id: Mapped[int] = mapped_column(ForeignKey("ward.ward_id"))
    ward: Mapped["Ward"] = relationship(
        back_populates="polling_units", lazy=True)
    lga_id: Mapped[int] = mapped_column(ForeignKey("lga.uniqueid"))
    lga: Mapped["Lga"] = relationship(
        back_populates="polling_units", lazy=True)
    results: Mapped[List["Result"]] = db.relationship(
        'Result', back_populates='polling_unit', lazy=True)


class Result(db.Model):
    __tablename__ = 'announced_pu_results'
    result_id = db.Column(db.Integer, primary_key=True)
    party_score = db.Column(db.Integer)
    party_abbreviation = db.Column(db.String(100))
    entered_by_user = db.Column(db.String(100))
    date_entered = db.Column(db.DateTime())
    polling_unit_uniqueid: Mapped[int] = mapped_column(
        ForeignKey("polling_unit.uniqueid"))
    polling_unit: Mapped["Pu"] = relationship(
        back_populates="results", lazy=True)


# creating our routes
@app.route('/')
def index():
    lgas = Lga.query.all()
    return render_template('index.html', lgas=lgas)


@app.route('/lgas')
def lga_results():
    lgas = Lga.query.all()
    return render_template('result.html', lgas=lgas)


@app.route('/add', methods=['GET', 'POST'])
def add_lga_results():
    lgas = Lga.query.all()
    if request.method == 'POST':
        party_names = request.form.getlist('party')
        vote_counts = request.form.getlist('votes')
        polling_unit_name = request.form['polling_unit_name']
        ward_id = request.form['ward_id']
        lga_id = request.form['lga_id']
        polling_unit_description = request.form['polling_unit_description']
        polling_unit_number = request.form['polling_unit_number']
        polling_unit_id = request.form['polling_unit_id']
        long = request.form['long']
        lat = request.form['lat']
        entered_by_user = request.form['entered_by_user']
        new_polling_unit = Pu(polling_unit_name=polling_unit_name, lat=lat, long=long, ward_id=ward_id, lga_id=lga_id,
                              polling_unit_description=polling_unit_description, polling_unit_number=polling_unit_number, polling_unit_id=polling_unit_id, entered_by_user=entered_by_user)
        try:
            db.session.add(new_polling_unit)
            db.session.flush()

            for party, votes in zip(party_names, vote_counts):
                result = Result(party_abbreviation=party, party_score=votes, entered_by_user=entered_by_user,
                                polling_unit_uniqueid=new_polling_unit.uniqueid, date_entered=datetime.now())
                db.session.add(result)

            db.session.commit()

            return render_template('save.html', lgas=lgas,status="success" , message='Vote results added successfully!')
        except:
            return render_template('save.html', lgas=lgas,status="danger", message='Error, Vote results not saved!')

  
    return render_template('save.html', lgas=lgas)


@app.route('/wards/<lga_id>')
def get_wards(lga_id):
    wards = Ward.query.filter_by(lga_id=lga_id).all()
    ward_list = [{'id': ward.ward_id, 'name': ward.ward_name}
                 for ward in wards]
    return jsonify(ward_list)


@app.route('/pu/<ward_id>')
def get_polling_units(ward_id):
    polling_units = Pu.query.filter_by(ward_id=ward_id).all()
    pu_list = [{'id': pu.uniqueid, 'name': pu.polling_unit_name}
               for pu in polling_units]
    return jsonify(pu_list)


@app.route('/get_results/<pu_id>')
def get_polling_units_results(pu_id):
    results = Result.query.filter_by(polling_unit_uniqueid=pu_id).all()
    results_list = [{'id': result.result_id, 'name': result.party_abbreviation,
                     'score': result.party_score} for result in results]
    return jsonify(results_list)


@app.route('/lga_results/<id>')
def get_lga_results(id):
    # Retrieve all results for the given local government
    results = db.session.query(Result).join(Pu).join(
        Ward).join(Lga).filter(Lga.lga_id == id).all()
    party_votes = {}
    total_votes = 0
    for result in results:
        total_votes += result.party_score
        party = result.party_abbreviation
        votes = result.party_score
        if party in party_votes:
            party_votes[party] += votes
        else:
            party_votes[party] = votes

    return jsonify({'results': party_votes, 'total': total_votes})


# run flask app
if __name__ == "__main__":
    with app.app_context():
        db.reflect()
    app.run(debug=True)
