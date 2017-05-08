#!/usr/bin/env python
# ~*~ coding: utf-8 ~*~
# >>
#   © Vivint, inc. 2017
#   blake, afjr-sprinklers
# <<
from gevent.monkey import patch_all
patch_all()

import os
import time
import logging
from datetime import datetime

from flask import Flask, render_template, jsonify, abort, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from gevent import Greenlet, sleep
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Numeric, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy_utils import ChoiceType
from wtforms.validators import NumberRange
from wtforms_alchemy import model_form_factory

logger = logging.getLogger(__name__)

HOST = 'localhost'
PORT = 8000
DEBUG = True
START_TIME = datetime.utcnow()

threads = []
db_path = os.path.join(os.getcwd(), 'db.sqlite')
engine = create_engine('sqlite:///%s' % db_path, echo=True)
Base = declarative_base(bind=engine)
BaseModelForm = model_form_factory(FlaskForm)


class TimeMixin(object):
    created = Column(DateTime, default=datetime.utcnow)
    updated = Column(DateTime, default=datetime.utcnow)


class Data(TimeMixin, Base):
    __tablename__ = 'data'

    id = Column(Integer, primary_key=True)
    sensor_id = Column(Integer, ForeignKey('sensors.id'))
    sensor = relationship('Sensor', back_populates='data')

    intval = Column(Integer, default=None, nullable=True)
    strval = Column(String, default=None, nullable=True)
    floval = Column(Numeric(4), default=None, nullable=True)


class Event(TimeMixin, Base):
    __tablename__ = 'events'

    EVENT_TYPES = [
        ('water_manual', 'Water Manually'),
        ('water_automatic', 'Water Automatic'),
        ('water_start', 'Started Watering'),
        ('water_end', 'Ended Watering'),
        ('history', 'History')
    ]

    id = Column(Integer, primary_key=True)
    type = Column(ChoiceType(EVENT_TYPES))
    description = Column(String(4096), nullable=True)


class Sensor(TimeMixin, Base):
    __tablename__ = 'sensors'

    SENSOR_TYPES = [
        ('digital', 'Digital'),
        ('analog', 'Analog')
    ]

    id = Column(Integer, primary_key=True)
    alias = Column(String(32), default=lambda: hex(int(time.time())), nullable=False, unique=True)
    data = relationship('Data', order_by=Data.created, back_populates="sensor")
    type = Column(ChoiceType(SENSOR_TYPES))

    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    active = Column(Boolean, default=True)
    gpio = Column(Integer, nullable=False, info={'validators': NumberRange(0, 40)})
    gp_idx = Column(Integer, default=None, nullable=True, info={'validators': NumberRange(0, 7)})

    @staticmethod
    def __form(obj, form):
        for field in form.data.keys():
            if hasattr(obj, field):
                setattr(obj, field, form[field].data)
        return obj

    @classmethod
    def from_form(cls, form):
        s = Sensor()
        return cls.__form(s, form)

    def update_from_form(self, form):
        return self.__form(self, form)


class ModelForm(BaseModelForm):
    @classmethod
    def get_session(cls):
        return Session()


class SensorForm(ModelForm):
    class Meta:
        model = Sensor
        exclude = ['alias']


Session = sessionmaker()
Session.configure(bind=engine)
Base.metadata.create_all(engine)

app = Flask(__name__)
app.config.from_mapping({
    'SECRET_KEY': 'nosecrets!'
})


@app.route('/')
def index():
    session = Session()
    sensors = session.query(Sensor).order_by(Sensor.active.desc(), Sensor.name.asc()).all()
    events = session.query(Event).order_by(Event.created.desc()).limit(10).all()
    datas = session.query(Data).order_by(Data.created.desc()).limit(30).all()

    event_count = session.query(func.count(Event.id)).scalar()

    statistics = {
        'event_count': event_count,
#        'data_count': session.query(func.count(Data.id)).scaler(),
#        'uptime': datetime.utcnow() - START_TIME,
#        'thread_count': len(threads)
    }

    session.close()

    return render_template("index.html",
                           stats=statistics,
                           sensors=sensors,
                           events=events,
                           datas=datas)


@app.route('/add/sensor', methods=['GET', 'POST'])
def add_sensor():
    form = SensorForm()

    if form.validate_on_submit():
        session = Session()
        sensor = Sensor.from_form(form)

        session.add(sensor)
        session.commit()

        flash('Successfully added sensor <u>%s</u>' % sensor.name, 'info')

        session.close()
        return redirect(url_for('index'))

    return render_template('add_sensor.html', label='Add', form=form, callback=url_for('add_sensor'))


@app.route('/edit/sensor.<alias>', methods=['GET', 'POST'])
def edit_sensor(alias):
    changed = False

    session = Session()
    sensor = session.query(Sensor).filter(Sensor.alias == alias).first()

    delete_sensor = bool(int(request.args.get('delete', 0)))

    if not sensor:
        return abort(404)

    if delete_sensor:
        session.delete(sensor)
        flash('Removed sensor <u>%s</u>' % sensor.name, 'warning')
        changed = True

    form = SensorForm(obj=sensor)

    if form.validate_on_submit():
        sensor = sensor.update_from_form(form)
        flash('Updated sensor <u>%s</u>' % sensor.name, 'info')
        changed = True

    if changed:
        session.commit()
        session.close()
        return redirect(url_for('index'))

    return render_template('add_sensor.html',
                           can_delete=True,
                           label='Edit',
                           form=form,
                           callback=url_for('edit_sensor', alias=alias))


# // background thread functions
def read_sensors(interval):
    print(interval)


# // create background tasks
for t in [Greenlet.spawn_later(10, read_sensors, interval=30)]:
    threads.append(t)


if __name__ == '__main__':
    app.run(HOST, PORT, debug=DEBUG)