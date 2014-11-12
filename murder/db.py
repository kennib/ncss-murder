import sqlite3

from tornado.ncss import ncssbook_log

class Model(object):
	_conn = sqlite3.connect('ncssbook.db', isolation_level=None)
	_table = None

	@classmethod
	def _sql(cls, query, args=()):
		args = tuple(args)
		ncssbook_log.debug('sql query=%r args=%r', query, args)
		return cls._conn.execute(query, args)

	@classmethod
	def _attribs(cls, sep, kwargs):
		keys = kwargs.keys()
		attribs = '= ? {} '.format(sep).join(keys) + ' = ?'
		return attribs, kwargs.values()

	@classmethod
	def select(cls, **kwargs):
		"""select(**kwargs) -> instance
		   returns a cursor from the database with given attributes"""
		if len(kwargs) == 0:
			query = """SELECT * FROM {}""".format(cls._table)
			values = []
		else:
			attribs, values = cls._attribs('AND', kwargs)
			query = """SELECT * FROM {} WHERE {}""".format(cls._table, attribs)
		return cls._sql(query, values)

	@classmethod
	def iter(cls, **kwargs):
		c = cls.select(**kwargs)
		row = c.fetchone()
		while row is not None:
			yield cls(*row)
			row = c.fetchone()

	@classmethod
	def add(cls, **kwargs):
		attribs = ', '.join(kwargs.keys())
		places = ', '.join('?' * len(kwargs))
		values = kwargs.values()
		INSERT = """INSERT INTO {} ({}) VALUES ({})""".format(cls._table, attribs, places)
		c = cls._sql(INSERT, values)
		# this could return the wrong object on near simultaneous Model.adds
		# if multiple threads are using the one database connection
		# not a problem for us here using Tornado since it is single threaded
		GET = """SELECT * FROM {} WHERE id = last_insert_rowid()""".format(cls._table)
		c = cls._sql(GET)
		return cls(*c.fetchone())

	def update(self, **kwargs):
		assert self.id is not None
		assert len(kwargs) != 0
		attribs, values = self._attribs(', ', kwargs)
		UPDATE = """UPDATE {} SET {} WHERE ID = ?""".format(self._table, attribs)
		self._sql(UPDATE, values + [self.id])
		self.__dict__.update(kwargs)

	@classmethod
	def find(cls, **kwargs):
		"""find(field, value) -> instance (or None)

		   returns an instance from the database with given attributes
		   or None if no matching instance exists"""
		c = cls.select(**kwargs)
		# rowcount cannot be trusted in SQLite on SELECT (except when == 0)
		row = c.fetchone()
		if row is None:
			return None
		inst = cls(*row)
		if c.fetchone() is not None:
			raise NonUniqueError("{} is not unique in {}".format(kwargs, cls._table))
		return inst

	@classmethod
	def get(cls, **kwargs):
		"""get(**kwargs) -> instance

		   returns a unique instance from the database with given attributes
		   throws an DoesNotExistError if no matching instance exists"""
		inst = cls.find(**kwargs)
		if inst is None:
			raise DoesNotExistError("instance {} does not exist in {}".format(kwargs, cls._table))
