-- If you wish to create the SQLite database manually, this is the schema.
CREATE TABLE "timelapse_photo" (
        `photo_id`      INTEGER PRIMARY KEY AUTOINCREMENT,
        `filename`      TEXT,
        `timestamp`     TEXT,
        `processed_flag`        TEXT
);
CREATE TABLE timelapse_log (timestamp TEXT, status TEXT, command TEXT);
CREATE TABLE timelapse_video (video_id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT, timestamp TEXT, date TEXT, processed_flag TEXT);
