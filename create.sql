CREATE TABLE listens (
  id SERIAL PRIMARY KEY,
  ts TIMESTAMP NOT NULL,
  platform VARCHAR NOT NULL,
	ms_played int4 NOT NULL,
	conn_country VARCHAR NOT NULL,
	master_metadata_track_name VARCHAR,
	master_metadata_album_artist_name VARCHAR,
	master_metadata_album_album_name VARCHAR,
	spotify_track_uri VARCHAR,
	reason_start VARCHAR NOT NULL,
	reason_end VARCHAR NOT NULL,
	shuffle bool,
	skipped bool,
	offline bool,
	offline_timestamp int8 NOT NULL,
	incognito_mode bool
);

CREATE TABLE genres (
	id SERIAL PRIMARY KEY,
	genre VARCHAR NOT NULL,
	listens int NOT NULL
);